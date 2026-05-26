import os
from pymongo import MongoClient
from dotenv import load_dotenv

# This looks for your hidden .env file and loads its variables into system memory
load_dotenv()

# Pulls the string safely without writing it explicitly in the code
uri = os.getenv("MONGO_URI")


# ==============================================================================
# DATABASE CONNECTION
# Purpose: Establishes a communication channel with the local MongoDB instance 
#          and targets the appropriate collection.
# ==============================================================================





# ==============================================================================
# DATABASE ENVIRONMENT CONFIGURATION
# ==============================================================================

# 1. UNCOMMENT this line to target your own machine:
# uri = "mongodb://127.0.0.1:27017/"


# ==============================================================================
# CLOUD DATABASE CONNECTION
# Purpose: Pointing the script to your MongoDB Atlas cloud cluster instance
# ==============================================================================

# 2. COMMENT OUT the cloud connection string with a '#' symbol:

client = MongoClient(uri)
db = client["mobility_db"]
collection = db["trips"]

# print("Connected successfully to your LOCAL MongoDB server!")

print("Connected successfully to MongoDB Atlas Cloud Cluster!")


# ==============================================================================
# C (CREATE) - ENVIRONMENT PURGE & SEEDING
# Purpose: Clears existing legacy documents to guarantee a fresh playground,
#          then inserts a new batch of embedded trip logs.
# ==============================================================================
collection.delete_many({})

trips_data = [
    {
        "trip_id": 1,
        "user": {
            "name": "John",
            "surname": "cena.isnomoresoyoucantseehim",
            "birthdate": "1995-05-10",
            "country": "USA"
        },
        "start_station": {"name": "Station A"},
        "end_station": {"name": "Station B"},
        "total_cost": 5.5,
        "events": [
                {"type": "GPS", "value": 1.1},
                {"type": "ERROR", "value": 0}
            ]
    },
    {
        "trip_id": 2,
        "user": {
            "name": "Maria",
            "surname": "Rossi",
            "birthdate": "1993-08-15",
            "country": "Italy"
        },
        "start_station": {"name": "Station B"},
        "end_station": {"name": "Station C"},
        "total_cost": 6.0
    },
    {
        "trip_id": 3,
        "user": {
            "name": "Farooq",
            "surname": "Muhammad",
            "birthdate": "2002-10-18",
            "country": "Pakistan"
        },
        "start_station": {"name": "Station A"},
        "end_station": {"name": "Station C"},
        "total_cost": 4.0
    },
    {
        "trip_id": 4,
        "user": {
            "name": "Alex",
            "surname": "Schmidt",
            "birthdate": "1992-06-15",
            "country": "Germany"
        },
        "start_station": {"name": "Station A"},
        "end_station": {"name": "Station B"},
        "total_cost": 7.5
    }
]

collection.insert_many(trips_data)
print("Inserted!")

# ==============================================================================
# R (READ) - INVENTORY DISCOVERY
# Purpose: Queries and displays all records currently held within the document array.
# ==============================================================================
print("\nAll Data:")
for trip in collection.find():
    print(trip)

# ==============================================================================
# U (UPDATE) - ATTRIBUTE MODIFICATION
# Purpose: Locates a specific target profile using unique attributes and changes
#          its transactional financial value.
# ==============================================================================
collection.update_one(
    {"trip_id": 4},
    {"$set": {"total_cost": 8.0}}
)

collection.update_one(
  { "trip_id": 2 },
  {
    "$set": {
      "events": [
        { "type": "GPS", "value": 1.1 },
        { "type": "ERROR", "value": 0 }
      ]
    }
  }
)
print("\nUpdated!")

# ==============================================================================
# D (DELETE) - ENTITY REMOVAL
# Purpose: Drops a single specified document profile out of the workspace.
# ==============================================================================
collection.delete_one({"trip_id": 4})
print("Deleted!")

# ==============================================================================
# VERIFICATION CONTROL
# Purpose: Runs a final lookup to review the active dataset following changes.
# ==============================================================================
print("\nFinal Data:")
for trip in collection.find():
    print(trip)