import os
import random
from datetime import datetime, timedelta
from faker import Faker
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from pymongo import MongoClient

# Load configuration details from your .env file
load_dotenv()

fake = Faker()

def generate_mobility_data(num_users, num_trips, events_per_trip):
    print(f"\n--- Starting generation for {num_users} users, {num_trips} trips, with {events_per_trip} events/trip ---")
    
    # 1. Generate Users
    users_pg = []
    users_mongo = []
    countries = ['Italy', 'USA', 'Pakistan', 'Spain', 'France', 'Germany']
    for i in range(1, num_users + 1):
        name = fake.first_name()
        surname = fake.last_name()
        birthdate = fake.date_of_birth(minimum_age=18, maximum_age=70).strftime('%Y-%m-%d')
        country = random.choice(countries)
        
        # PostgreSQL format (Tuple)
        users_pg.append((i, name, surname, birthdate, country))
        # MongoDB format (Dictionary/JSON)
        users_mongo.append({
            "_id": i,
            "name": name,
            "surname": surname,
            "birthdate": birthdate,
            "country": country
        })
    print(f"✔ Generated {len(users_pg)} users.")

    # 2. Fixed Stations
    stations_pg = [
        (1, "Station A", "Milan", 10),
        (2, "Station B", "Rome", 15),
        (3, "Station C", "Naples", 12)
    ]
    stations_mongo = [
        {"_id": 1, "name": "Station A", "city": "Milan", "capacity": 10},
        {"_id": 2, "name": "Station B", "city": "Rome", "capacity": 15},
        {"_id": 3, "name": "Station C", "city": "Naples", "capacity": 12}
    ]

    # 3. Generate Trips & Events
    trips_pg = []
    trips_mongo = []
    events_pg = []
    
    event_id_counter = 1
    event_types = ['GPS', 'ERROR', 'BATTERY', 'DELAY']
    base_time = datetime(2026, 1, 1, 8, 0, 0)

    for trip_id in range(1, num_trips + 1):
        user_id = random.randint(1, num_users)
        start_station_id = random.randint(1, len(stations_mongo))
        end_station_id = random.randint(1, len(stations_mongo))
        
        start_time = base_time + timedelta(minutes=random.randint(1, 10000))
        duration_minutes = random.randint(5, 60)
        end_time = start_time + timedelta(minutes=duration_minutes)
        total_cost = round(random.uniform(2.0, 15.0), 2)

        # PostgreSQL structured flat format
        trips_pg.append((
            trip_id, user_id, start_station_id, end_station_id, start_time, end_time, total_cost
        ))

        # We build the embedded events sub-array for this specific trip in MongoDB
        trip_events_embedded = []
        for _ in range(events_per_trip):
            event_type = random.choice(event_types)
            if random.random() < 0.1: 
                event_type = 'ERROR'
                
            value = round(random.uniform(1.0, 100.0), 1) if event_type != 'ERROR' else 0.0
            event_timestamp = start_time + timedelta(minutes=random.randint(1, duration_minutes - 1))

            # PostgreSQL flat record row format
            events_pg.append((
                event_id_counter, trip_id, event_timestamp, event_type, value
            ))
            event_id_counter += 1

            # MongoDB nested object structure
            trip_events_embedded.append({
                "event_id": event_id_counter,
                "timestamp": event_timestamp.isoformat(),
                "event_type": event_type,
                "value": value
            })

        # MongoDB master document layout with embedded array properties
        trips_mongo.append({
            "_id": trip_id,
            "user_id": user_id,
            "start_station_id": start_station_id,
            "end_station_id": end_station_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_cost": total_cost,
            "events": trip_events_embedded # Dynamic nested array
        })

    print(f"✔ Generated {len(trips_pg)} trips and {len(events_pg)} telemetry events.")
    return (users_pg, stations_pg, trips_pg, events_pg), (users_mongo, stations_mongo, trips_mongo)


def insert_to_postgres(users, stations, trips, events):
    print("\nConnecting to PostgreSQL database to inject data...")
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        cursor = conn.cursor()
        print("Clearing out old PostgreSQL records...")
        cursor.execute("TRUNCATE table events, trips, stations, users RESTART IDENTITY CASCADE;")

        print("Bulk inserting relational structures...")
        execute_values(cursor, "INSERT INTO stations VALUES %s", stations)
        execute_values(cursor, "INSERT INTO users VALUES %s", users)
        execute_values(cursor, "INSERT INTO trips VALUES %s", trips)
        execute_values(cursor, "INSERT INTO events VALUES %s", events)

        conn.commit()
        print("✔ Successfully populated PostgreSQL with all benchmark records!")
    except Exception as e:
        print(f"❌ PostgreSQL Error: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()


def insert_to_mongodb(users, stations, trips):
    print("\nConnecting to MongoDB Atlas Cluster to inject data...")
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client["mobility_db"]
        
        # Clean state: Wipe existing documents to prevent duplicate primary key _id collisions
        print("Clearing out old MongoDB collections...")
        db["users"].drop()
        db["stations"].drop()
        db["trips"].drop()

        # Bulk insert document mappings
        print("Bulk inserting users documents...")
        db["users"].insert_many(users)
        
        print("Bulk inserting stations documents...")
        db["stations"].insert_many(stations)
        
        print("Bulk inserting trips documents (with embedded telemetry arrays)...")
        db["trips"].insert_many(trips)

        print("✔ Successfully populated MongoDB Atlas with all benchmark documents!")
    except Exception as e:
        print(f"❌ MongoDB Error: {e}")
    finally:
        if client:
            client.close()


if __name__ == "__main__":
    # Starting Benchmark Matrix Parameters
    num_users = 1000
    num_trips = 10000
    events_per_trip = 2
    
    pg_data, mongo_data = generate_mobility_data(num_users, num_trips, events_per_trip)
    
    # Process both pipeline blocks
    insert_to_postgres(*pg_data)
    insert_to_mongodb(*mongo_data)