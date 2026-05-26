import os
import random
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

def evolve_mongodb_schema():
    print("=" * 60)
    print("        MONGODB SCHEMA EVOLUTION: BATTERY LEVEL FIELD        ")
    print("=" * 60)
    
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["mobility_db"]
    
    # 1. Simulate Schema Evolution: Inject 'battery_level' into only a subset of trips
    # This simulates a rolling software update where old trips don't have it, but new ones do!
    print("\nUpdating a subset of trips to include the evolved 'battery_level' field inside events...")
    
    sample_trips = db["trips"].find().limit(5)
    
    for trip in sample_trips:
        updated_events = []
        for event in trip.get("events", []):
            # Evolve schema by adding the new battery metric to the nested dictionary object
            event["battery_level"] = random.randint(15, 100) 
            updated_events.append(event)
            
        db["trips"].update_one(
            {"_id": trip["_id"]},
            {"$set": {"events": updated_events, "schema_version": "2.0.0"}}
        )
        print(f" ✔ Evolved Trip ID: {trip['_id']} to Schema Version 2.0.0")

    # 2. Assignment Query Part 1 (Query 2 variant): Identify trips with critical low battery (< 20%)
    print("\nExecuting Evolved Document Pipeline (Find critical battery levels < 20%)...")
    
    pipeline = [
        {"$unwind": "$events"},
        {"$match": {"events.battery_level": {"$lt": 20}}},
        {"$project": {
            "trip_id": "$_id",
            "event_id": "$events.event_id",
            "current_battery": "$events.battery_level",
            "schema": "$schema_version"
        }}
    ]
    
    low_battery_trips = list(db["trips"].aggregate(pipeline))
    
    if low_battery_trips:
        for alert in low_battery_trips:
            print(f"🚨 ALERT: Trip ID {alert['trip_id']} has critical battery: {alert['current_battery']}% (Schema: {alert['schema']})")
    else:
        print("ℹ No trips hit the critical <20% threshold in this sample batch.")
        
    client.close()

if __name__ == "__main__":
    evolve_mongodb_schema()