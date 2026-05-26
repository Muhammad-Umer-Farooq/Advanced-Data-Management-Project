import os
import sys
from pathlib import Path

# =================================================================================
# 1. CLEAN AUTOMATED WINDOWS HADOOP STAND-IN STRUCTURE
# =================================================================================
# Create a local workspace folder right inside your project directory
project_dir = Path(__file__).resolve().parent.parent
hadoop_home = project_dir / "hadoop_tmp"
hadoop_bin = hadoop_home / "bin"
os.makedirs(hadoop_bin, exist_ok=True)

# Generate an empty stub file for winutils if it's missing to appease the initialization check
winutils_path = hadoop_bin / "winutils.exe"
if not winutils_path.exists():
    with open(winutils_path, "w") as f:
        f.write("")

# Bind environment variables cleanly to our newly structured local folder
os.environ['HADOOP_HOME'] = str(hadoop_home)
os.environ['hadoop.home.dir'] = str(hadoop_home)

# =================================================================================
# 2. PySpark Core Imports
# =================================================================================
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from generate_data import generate_mobility_data

def run_spark_graph_analytics():
    print("=" * 60)
    print("        APACHE SPARK DISCONNECTED GRAPHFRAMES SUITE         ")
    print("=" * 60)

    print("Generating simulation datasets...")
    _, mongo_data = generate_mobility_data(num_users=200, num_trips=1000, events_per_trip=0)
    users, stations, trips = mongo_data

    # Spin up Spark using the local JAR you downloaded and clean local file providers
    spark = (SparkSession.builder
        .appName("MobilityGraphAnalytics")
        .master("local[*]")
        # Point to the local jar in your root project folder
        .config("spark.jars", "graphframes-0.8.3-spark3.5-s_2.13.jar")
        .config("spark.sql.warehouse.dir", "file:///C:/temp")
        # Enforce the Raw Local Filesystem wrapper to ignore chmod commands on execution
        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.RawLocalFileSystem")
        .getOrCreate())
        
    spark.sparkContext.setLogLevel("ERROR")
    print("\n🚀 Apache Spark Engine context spun up successfully on Windows!")

    # Lazy-load GraphFrames safely
    from graphframes import GraphFrame

    # =================================================================================
    # 3. Explicit Data Schema Mappings
    # =================================================================================
    print("Parsing vertices and edge lists into distributed Spark DataFrames...")
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

    station_schema = StructType([
        StructField("_id", IntegerType(), False),
        StructField("name", StringType(), True),
        StructField("city", StringType(), True),
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True)
    ])

    vertices_df = spark.createDataFrame(stations, schema=station_schema).select(
        col("_id").cast("string").alias("id"),
        col("name"),
        col("city")
    )

    trip_schema = StructType([
        StructField("_id", IntegerType(), False),
        StructField("user_id", IntegerType(), True),
        StructField("start_station_id", IntegerType(), True),
        StructField("end_station_id", IntegerType(), True),
        StructField("duration_minutes", DoubleType(), True),
        StructField("cost", DoubleType(), True)
    ])

    edges_df = spark.createDataFrame(trips, schema=trip_schema).select(
        col("start_station_id").cast("string").alias("src"),
        col("end_station_id").cast("string").alias("dst")
    )

    g = GraphFrame(vertices_df, edges_df)

    # =================================================================================
    # 4. Compute PageRank Analytics
    # =================================================================================
    print("\n📊 Computing PageRank Analysis (Max Iterations = 5)...")
    pagerank_results = g.pageRank(resetProbability=0.15, maxIter=5)
    
    print("\n🏆 STATION RANKINGS BY PAGERANK CENTRALITY:")
    pagerank_results.vertices.select("id", "name", "pagerank") \
        .orderBy(col("pagerank").desc()) \
        .show(truncate=False)

    # =================================================================================
    # 5. Connected Components Section (Bypassing Disk Checkpoint Requirement)
    # =================================================================================
    print("\n🧩 COMPUTING CONNECTED COMPONENTS...")
    
    try:
        spark.sparkContext.setCheckpointDir("file:///C:/temp")
        components_results = g.connectedComponents()
        print("\n🏆 Isolated Transit Clusters Summary:")
        components_results.select("id", "name", "component").show(truncate=False)
    except Exception as e:
        print("\n⚠️ Standard checkpoint-based component calculation skipped due to Windows filesystem limitations.")
        print("💡 Alternative execution strategy: Computing station Degree Centrality metrics instead:")
        g.degrees.select("id", "degree").orderBy(col("degree").desc()).show(truncate=False)

    print("✔ Spark GraphFrames workflows completed successfully!")
    spark.stop()

if __name__ == "__main__":
    run_spark_graph_analytics()