import os
import time
from dotenv import load_dotenv
import psycopg2
from pymongo import MongoClient

# Load configurations
load_dotenv()

# --- CONNECT TO DATABASES ---
def get_postgres_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

def get_mongodb_db():
    client = MongoClient(os.getenv("MONGO_URI"))
    return client["mobility_db"], client

# --- BENCHMARK ROCKETS ---
def run_benchmarks():
    pg_conn = get_postgres_connection()
    pg_cursor = pg_conn.cursor()
    mongo_db, mongo_client = get_mongodb_db()

    print("=" * 60)
    print("      MULTI-MODEL QUERY PERFORMANCE BENCHMARK SUITE      ")
    print("=" * 60)

    # -------------------------------------------------------------
    # QUERY 1: Trips with User profile and Station names
    # -------------------------------------------------------------
    print("\nExecuting Query 1 (Trips + Users + Stations info)...")
    
    # PostgreSQL
    pg_q1 = """
        SELECT t.trip_id, u.name, s1.name, s2.name
        FROM trips t
        JOIN users u ON t.user_id = u.user_id
        JOIN stations s1 ON t.start_station_id = s1.station_id
        JOIN stations s2 ON t.end_station_id = s2.station_id;
    """
    start = time.time()
    pg_cursor.execute(pg_q1)
    pg_cursor.fetchall()
    pg_time1 = (time.time() - start) * 1000

    # MongoDB (Using Aggregation $lookup to mimic JOINs for referenced fields)
    mongo_pipeline1 = [
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "user"}},
        {"$lookup": {"from": "stations", "localField": "start_station_id", "foreignField": "_id", "as": "start_station"}},
        {"$lookup": {"from": "stations", "localField": "end_station_id", "foreignField": "_id", "as": "end_station"}},
        {"$project": {"_id": 1, "user_name": {"$arrayElemAt": ["$user.name", 0]}, "start_station": {"$arrayElemAt": ["$start_station.name", 0]}, "end_station": {"$arrayElemAt": ["$end_station.name", 0]}}}
    ]
    start = time.time()
    list(mongo_db["trips"].aggregate(mongo_pipeline1))
    mongo_time1 = (time.time() - start) * 1000
    
    print(f"  -> PostgreSQL: {pg_time1:.2f} ms")
    print(f"  -> MongoDB:    {mongo_time1:.2f} ms")

    # -------------------------------------------------------------
    # QUERY 2: Total trips and average trip duration per user
    # -------------------------------------------------------------
    print("\nExecuting Query 2 (Trip counts & Avg duration per user)...")
    
    # PostgreSQL
    pg_q2 = """
        SELECT u.name, COUNT(t.trip_id), AVG(EXTRACT(EPOCH FROM (t.end_time - t.start_time))/60)
        FROM users u
        JOIN trips t ON u.user_id = t.user_id
        GROUP BY u.name, u.user_id;
    """
    start = time.time()
    pg_cursor.execute(pg_q2)
    pg_cursor.fetchall()
    pg_time2 = (time.time() - start) * 1000

    # MongoDB
    mongo_pipeline2 = [
        # To compute duration, we parse strings back to dates, group by user, and join user profiles
        {
            "$project": {
                "user_id": 1,
                "duration_minutes": {
                    "$divide": [
                        {"$subtract": [{"$dateFromString": {"dateString": "$end_time"}}, {"$dateFromString": {"dateString": "$start_time"}}]},
                        60000
                    ]
                }
            }
        },
        {"$group": {"_id": "$user_id", "total_trips": {"$sum": 1}, "avg_duration": {"$avg": "$duration_minutes"}}},
        {"$lookup": {"from": "users", "localField": "_id", "foreignField": "_id", "as": "user_info"}},
        {"$project": {"user_name": {"$arrayElemAt": ["$user_info.name", 0]}, "total_trips": 1, "avg_duration": 1}}
    ]
    start = time.time()
    list(mongo_db["trips"].aggregate(mongo_pipeline2))
    mongo_time2 = (time.time() - start) * 1000

    print(f"  -> PostgreSQL: {pg_time2:.2f} ms")
    print(f"  -> MongoDB:    {mongo_time2:.2f} ms")

    # -------------------------------------------------------------
    # QUERY 3: Traffic volume at each station (Departures vs Arrivals)
    # -------------------------------------------------------------
    print("\nExecuting Query 3 (Station Departures and Arrivals volume)...")
    
    # PostgreSQL
    pg_q3 = """
        SELECT s.name, 
               (SELECT COUNT(*) FROM trips t WHERE t.start_station_id = s.station_id) AS started,
               (SELECT COUNT(*) FROM trips t WHERE t.end_station_id = s.station_id) AS ended
        FROM stations s;
    """
    start = time.time()
    pg_cursor.execute(pg_q3)
    pg_cursor.fetchall()
    pg_time3 = (time.time() - start) * 1000

    # MongoDB
    start = time.time()
    stations = list(mongo_db["stations"].find())
    for s in stations:
        started_count = mongo_db["trips"].count_documents({"start_station_id": s["_id"]})
        ended_count = mongo_db["trips"].count_documents({"end_station_id": s["_id"]})
    mongo_time3 = (time.time() - start) * 1000

    print(f"  -> PostgreSQL: {pg_time3:.2f} ms")
    print(f"  -> MongoDB:    {mongo_time3:.2f} ms")

    # -------------------------------------------------------------
    # QUERY 4: Find all unique trips containing an 'ERROR' event
    # -------------------------------------------------------------
    print("\nExecuting Query 4 (Isolate Trip IDs with ERROR logs)...")
    
    # PostgreSQL (Requires scanning across a foreign table relation link)
    pg_q4 = """
        SELECT DISTINCT t.trip_id
        FROM trips t
        JOIN events e ON t.trip_id = e.trip_id
        WHERE e.event_type = 'ERROR';
    """
    start = time.time()
    pg_cursor.execute(pg_q4)
    pg_cursor.fetchall()
    pg_time4 = (time.time() - start) * 1000

    # MongoDB (Embedded layout advantage: Scan records directly without joining separate collections)
    start = time.time()
    list(mongo_db["trips"].find({"events.event_type": "ERROR"}, {"_id": 1}))
    mongo_time4 = (time.time() - start) * 1000

    print(f"  -> PostgreSQL: {pg_time4:.2f} ms")
    print(f"  -> MongoDB:    {mongo_time4:.2f} ms")
    print("\n" + "=" * 60)

    # Close connections
    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()

if __name__ == "__main__":
    run_benchmarks()