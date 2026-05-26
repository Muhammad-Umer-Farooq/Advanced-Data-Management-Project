import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from generate_data import generate_mobility_data

load_dotenv()

class Neo4jPipeline:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"), 
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )

    def close(self):
        self.driver.close()

    def build_graph_network(self, users, stations, trips):
        with self.driver.session() as session:
            print("\nWiping existing graph elements to ensure clean state...")
            session.run("MATCH (n) DETACH DELETE n;")

            # 1. Create Station Nodes
            print("Creating Station nodes...")
            for st in stations:
                session.run(
                    "CREATE (s:Station {id: $id, name: $name, city: $city, capacity: $capacity})",
                    id=int(st["_id"]), name=st["name"], city=st["city"], capacity=int(st["capacity"])
                )

            # 2. Create User Nodes
            print("Creating User nodes...")
            for usr in users:
                session.run(
                    "CREATE (u:User {id: $id, name: $name, surname: $surname, country: $country})",
                    id=int(usr["_id"]), name=usr["name"], surname=usr["surname"], country=usr["country"]
                )

            # 3. Create Trip Nodes
            print("Creating Trip transaction nodes...")
            for tr in trips:
                session.run(
                    "CREATE (t:Trip {id: $id, start_time: $start_time, end_time: $end_time, cost: $cost})",
                    id=int(tr["_id"]), start_time=tr["start_time"], end_time=tr["end_time"], cost=float(tr["total_cost"])
                )

            # Build simple range indexes
            print("Indexing nodes for relationship matching acceleration...")
            session.run("CREATE INDEX station_id_idx IF NOT EXISTS FOR (s:Station) ON (s.id);")
            session.run("CREATE INDEX user_id_idx IF NOT EXISTS FOR (u:User) ON (u.id);")
            session.run("CREATE INDEX trip_id_idx IF NOT EXISTS FOR (t:Trip) ON (t.id);")

            # 4. Weave User -> Trip Edges
            print("Weaving edge links: (:User)-[:PERFORMED]->(:Trip)...")
            for tr in trips:
                session.run(
                    """
                    MATCH (u:User {id: $user_id})
                    MATCH (t:Trip {id: $trip_id})
                    CREATE (u)-[:PERFORMED]->(t)
                    """,
                    user_id=int(tr["user_id"]), trip_id=int(tr["_id"])
                )

            # 5. Weave Trip -> Station Edges
            print("Weaving spatial routes: (:Trip)-[:STARTS_AT]->(:Station) and (:Trip)-[:ENDS_AT]->(:Station)...")
            for tr in trips:
                session.run(
                    """
                    MATCH (t:Trip {id: $trip_id})
                    MATCH (sStart:Station {id: $start_sid})
                    MATCH (sEnd:Station {id: $end_sid})
                    CREATE (t)-[:STARTS_AT]->(sStart)
                    CREATE (t)-[:ENDS_AT]->(sEnd)
                    """,
                    trip_id=int(tr["_id"]), 
                    start_sid=int(tr["start_station_id"]), 
                    end_sid=int(tr["end_station_id"])
                )

            print("✔ Graph topological network construction complete!")

if __name__ == "__main__":
    print("Generating system data pools for graph conversion...")
    _, mongo_data = generate_mobility_data(num_users=500, num_trips=2000, events_per_trip=0)
    users, stations, trips = mongo_data
    
    pipeline = Neo4jPipeline()
    try:
        pipeline.build_graph_network(users, stations, trips)
    finally:
        pipeline.close()