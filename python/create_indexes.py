import os
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING

load_dotenv()

def apply_mongodb_optimization():
    print("Connecting to MongoDB Atlas to apply database indexes...")
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["mobility_db"]
    
    # 1. Index for Query 4: Multikey Index on the embedded array field
    print("Creating Multikey index on trips.events.event_type...")
    db["trips"].create_index([("events.event_type", ASCENDING)])
    
    # 2. Indexes for Query 1 & 2: Single field indexes on referenced foreign keys
    print("Creating single-field target indexes on reference IDs...")
    db["trips"].create_index([("user_id", ASCENDING)])
    db["trips"].create_index([("start_station_id", ASCENDING)])
    db["trips"].create_index([("end_station_id", ASCENDING)])
    
    print("✔ All MongoDB performance optimizations successfully applied!")
    client.close()

if __name__ == "__main__":
    apply_mongodb_optimization()