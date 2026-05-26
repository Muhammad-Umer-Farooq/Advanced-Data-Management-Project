import os
import time
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

class Neo4jQueries:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"), 
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )

    def close(self):
        self.driver.close()

    def execute_assignment_queries(self, target_user_id):
        with self.driver.session() as session:
            print("=" * 60)
            print("         NATIVE NEO4J CYPHER GRAPH QUERY SUITE          ")
            print("=" * 60)

            # --- CYPHER QUERY 1: REACHABLE STATIONS FOR A USER (WITH TOINTEGER CASTING) ---
            # Using toInteger() bypasses any float/string structural type mismatches safely
            query1 = """
            MATCH (u:User) WHERE toInteger(u.id) = toInteger($user_id)
            MATCH (u)-[:PERFORMED]->(t:Trip)-[:STARTS_AT|ENDS_AT]->(s:Station)
            RETURN DISTINCT toInteger(s.id) AS station_id, s.name AS name, s.city AS city
            """
            
            print(f"\nExecuting Graph Query 1: Finding all stations reachable by User ID {target_user_id}...")
            start_time = time.time()
            result1 = session.run(query1, user_id=int(target_user_id))
            records1 = list(result1)
            duration1 = (time.time() - start_time) * 1000
            
            print(f"  -> Execution Time: {duration1:.2f} ms")
            print(f"  -> Reachable Stations Found: {len(records1)}")
            for rec in records1:
                print(f"     * Station {rec['station_id']}: {rec['name']} ({rec['city']})")

            # --- CYPHER QUERY 2: TOP 3 MOST IMPORTANT STATIONS ---
            # Counts the degree connections linking directly into station structures
            query2 = """
            MATCH (t:Trip)-[r:STARTS_AT|ENDS_AT]->(s:Station)
            RETURN s.name AS station_name, s.city AS city, COUNT(r) AS degree_centrality
            ORDER BY degree_centrality DESC
            LIMIT 3
            """
            
            print("\nExecuting Graph Query 2: Identifying the top 3 most important stations...")
            start_time = time.time()
            result2 = session.run(query2)
            records2 = list(result2)
            duration2 = (time.time() - start_time) * 1000
            
            print(f"  -> Execution Time: {duration2:.2f} ms")
            print("  -> Top 3 Stations Matrix:")
            if records2:
                for idx, rec in enumerate(records2, 1):
                    print(f"     {idx}. {rec['station_name']} ({rec['city']}) - Traffic Connections: {rec['degree_centrality']}")
            else:
                print("     ⚠️ No traffic links resolved. Verifying baseline graph topology edges...")
                # Backup checker: See if nodes exist independently
                count_nodes = session.run("MATCH (n) RETURN labels(n)[0] AS lbl, count(n) AS cnt;").data()
                print("     Current Database Node Allocation Summary:")
                for c in count_nodes:
                    print(f"       - Label: {c['lbl']} | Count: {c['cnt']}")
                    
            print("\n" + "=" * 60)

if __name__ == "__main__":
    runner = Neo4jQueries()
    try:
        runner.execute_assignment_queries(target_user_id=42)
    finally:
        runner.close()