import os
import time
import csv
import random
from datetime import datetime, timedelta
from faker import Faker
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from pymongo import MongoClient, ASCENDING

# Load environment credentials
load_dotenv()
fake = Faker()

# --- DATABASE CONNECTIONS ---
def get_postgres_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

def get_mongo_db():
    client = MongoClient(os.getenv("MONGO_URI"))
    return client["mobility_db"], client

# --- OPTIMIZED DATA GENERATION FOR LOOP SCALES ---
def generate_dataset(num_users, num_trips, events_per_trip):
    users_pg, users_mongo = [], []
    countries = ['Italy', 'USA', 'Pakistan', 'Spain', 'France', 'Germany']
    
    for i in range(1, num_users + 1):
        name, surname = fake.first_name(), fake.last_name()
        birthdate = fake.date_of_birth(minimum_age=18, maximum_age=70).strftime('%Y-%m-%d')
        country = random.choice(countries)
        users_pg.append((i, name, surname, birthdate, country))
        users_mongo.append({"_id": i, "name": name, "surname": surname, "birthdate": birthdate, "country": country})

    stations_pg = [(1, "Station A", "Milan", 10), (2, "Station B", "Rome", 15), (3, "Station C", "Naples", 12)]
    stations_mongo = [{"_id": 1, "name": "Station A", "city": "Milan", "capacity": 10},
                      {"_id": 2, "name": "Station B", "city": "Rome", "capacity": 15},
                      {"_id": 3, "name": "Station C", "city": "Naples", "capacity": 12}]

    trips_pg, trips_mongo, events_pg = [], [], []
    event_id_counter = 1
    event_types = ['GPS', 'ERROR', 'BATTERY', 'DELAY']
    base_time = datetime(2026, 1, 1, 8, 0, 0)

    for trip_id in range(1, num_trips + 1):
        user_id = random.randint(1, num_users)
        start_sid, end_sid = random.randint(1, 3), random.randint(1, 3)
        start_time = base_time + timedelta(minutes=random.randint(1, 10000))
        end_time = start_time + timedelta(minutes=random.randint(5, 60))
        total_cost = round(random.uniform(2.0, 15.0), 2)

        trips_pg.append((trip_id, user_id, start_sid, end_sid, start_time, end_time, total_cost))

        trip_events_embedded = []
        for _ in range(events_per_trip):
            event_type = random.choice(event_types)
            if random.random() < 0.1: event_type = 'ERROR'
            value = round(random.uniform(1.0, 100.0), 1) if event_type != 'ERROR' else 0.0
            event_timestamp = start_time + timedelta(minutes=random.randint(1, 5))

            events_pg.append((event_id_counter, trip_id, event_timestamp, event_type, value))
            trip_events_embedded.append({"event_id": event_id_counter, "timestamp": event_timestamp.isoformat(), "event_type": event_type, "value": value})
            event_id_counter += 1

        trips_mongo.append({"_id": trip_id, "user_id": user_id, "start_station_id": start_sid, "end_station_id": end_sid, "start_time": start_time.isoformat(), "end_time": end_time.isoformat(), "total_cost": total_cost, "events": trip_events_embedded})

    return (users_pg, stations_pg, trips_pg, events_pg), (users_mongo, stations_mongo, trips_mongo)

# --- WORKLOAD POPULATION ENGINE ---
def populate_databases(pg_data, mongo_data):
    # PostgreSQL
    pg_conn = get_postgres_conn()
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("TRUNCATE table events, trips, stations, users RESTART IDENTITY CASCADE;")
    execute_values(pg_cursor, "INSERT INTO stations VALUES %s", pg_data[1])
    execute_values(pg_cursor, "INSERT INTO users VALUES %s", pg_data[0])
    execute_values(pg_cursor, "INSERT INTO trips VALUES %s", pg_data[2])
    if pg_data[3]:
        execute_values(pg_cursor, "INSERT INTO events VALUES %s", pg_data[3])
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()

    # MongoDB
    mongo_db, mongo_client = get_mongo_db()
    mongo_db["users"].drop()
    mongo_db["stations"].drop()
    mongo_db["trips"].drop()
    
    mongo_db["users"].insert_many(mongo_data[0])
    mongo_db["stations"].insert_many(mongo_data[1])
    mongo_db["trips"].insert_many(mongo_data[2])
    
    # Re-apply our successful indexes instantly after drop
    mongo_db["trips"].create_index([("events.event_type", ASCENDING)])
    mongo_db["trips"].create_index([("user_id", ASCENDING)])
    mongo_client.close()

# --- BENCHMARK EXECUTION SUITE ---
def execute_benchmark_round(num_users, num_trips, num_events):
    pg_conn = get_postgres_conn()
    pg_cursor = pg_conn.cursor()
    mongo_db, mongo_client = get_mongo_db()

    results = {
        "scale": f"U{num_users}_T{num_trips}_E{num_events}",
        "pg_q1": 0, "mongo_q1": 0, "pg_q2": 0, "mongo_q2": 0,
        "pg_q3": 0, "mongo_q3": 0, "pg_q4": 0, "mongo_q4": 0
    }

    # Q1
    t0 = time.time()
    pg_cursor.execute("SELECT t.trip_id, u.name, s1.name, s2.name FROM trips t JOIN users u ON t.user_id = u.user_id JOIN stations s1 ON t.start_station_id = s1.station_id JOIN stations s2 ON t.end_station_id = s2.station_id;")
    pg_cursor.fetchall()
    results["pg_q1"] = round((time.time() - t0) * 1000, 2)

    t0 = time.time()
    list(mongo_db["trips"].aggregate([{"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "u"}}, {"$lookup": {"from": "stations", "localField": "start_station_id", "foreignField": "_id", "as": "s1"}}, {"$lookup": {"from": "stations", "localField": "end_station_id", "foreignField": "_id", "as": "s2"}}, {"$project": {"_id": 1, "un": {"$arrayElemAt": ["$u.name", 0]}}}]))
    results["mongo_q1"] = round((time.time() - t0) * 1000, 2)

    # Q2
    t0 = time.time()
    pg_cursor.execute("SELECT u.name, COUNT(t.trip_id), AVG(EXTRACT(EPOCH FROM (t.end_time - t.start_time))/60) FROM users u JOIN trips t ON u.user_id = t.user_id GROUP BY u.name, u.user_id;")
    pg_cursor.fetchall()
    results["pg_q2"] = round((time.time() - t0) * 1000, 2)

    t0 = time.time()
    list(mongo_db["trips"].aggregate([{"$project": {"user_id": 1, "dur": {"$divide": [{"$subtract": [{"$dateFromString": {"dateString": "$end_time"}}, {"$dateFromString": {"dateString": "$start_time"}}]}, 60000]}}}, {"$group": {"_id": "$user_id", "cnt": {"$sum": 1}, "avg_d": {"$avg": "$dur"}}}, {"$lookup": {"from": "users", "localField": "_id", "foreignField": "_id", "as": "ui"}}, {"$project": {"un": {"$arrayElemAt": ["$ui.name", 0]}, "cnt": 1, "avg_d": 1}}]))
    results["mongo_q2"] = round((time.time() - t0) * 1000, 2)

    # Q3
    t0 = time.time()
    pg_cursor.execute("SELECT s.name, (SELECT COUNT(*) FROM trips t WHERE t.start_station_id = s.station_id) AS s, (SELECT COUNT(*) FROM trips t WHERE t.end_station_id = s.station_id) AS e FROM stations s;")
    pg_cursor.fetchall()
    results["pg_q3"] = round((time.time() - t0) * 1000, 2)

    t0 = time.time()
    for s in list(mongo_db["stations"].find()):
        mongo_db["trips"].count_documents({"start_station_id": s["_id"]})
        mongo_db["trips"].count_documents({"end_station_id": s["_id"]})
    results["mongo_q3"] = round((time.time() - t0) * 1000, 2)

    # Q4
    t0 = time.time()
    pg_cursor.execute("SELECT DISTINCT t.trip_id FROM trips t JOIN events e ON t.trip_id = e.trip_id WHERE e.event_type = 'ERROR';")
    pg_cursor.fetchall()
    results["pg_q4"] = round((time.time() - t0) * 1000, 2)

    t0 = time.time()
    list(mongo_db["trips"].find({"events.event_type": "ERROR"}, {"_id": 1}))
    results["mongo_q4"] = round((time.time() - t0) * 1000, 2)

    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()
    return results

# --- MAIN LOOP RUNNER ---
if __name__ == "__main__":
    # Defining a progressive scaling subset matrix from the project PDF parameters
    test_scales = [
        {"users": 1000, "trips": 10000, "events": 0},
        {"users": 1000, "trips": 10000, "events": 2},
        {"users": 10000, "trips": 50000, "events": 5}
    ]

    csv_file = "python/benchmark_results.csv"
    fieldnames = ["scale", "pg_q1", "mongo_q1", "pg_q2", "mongo_q2", "pg_q3", "mongo_q3", "pg_q4", "mongo_q4"]

    with open(csv_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for scale in test_scales:
            u, t, e = scale["users"], scale["trips"], scale["events"]
            print(f"\n🚀 Running Scalability Layer: Users={u}, Trips={t}, Events={e}...")
            
            # Step A: Dynamic generation
            pg_d, mongo_d = generate_dataset(u, t, e)
            
            # Step B: Clean wipe and insert
            populate_databases(pg_d, mongo_d)
            
            # Step C: Time metrics
            metrics = execute_benchmark_round(u, t, e)
            writer.writerow(metrics)
            print(f"✔ Completed. Q4 Times -> PG: {metrics['pg_q4']}ms | Mongo: {metrics['mongo_q4']}ms")

    print(f"\n🎉 All scalability tests complete! Metrics saved to: {csv_file}")