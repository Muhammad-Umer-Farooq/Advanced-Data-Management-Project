from pyspark.sql import SparkSession

# ==============================================================================
# ENGINE INSTANTIATION
# Purpose: Initialize a local compute context for running parallel workloads.
# ==============================================================================
spark = SparkSession.builder \
    .appName("Mobility Project") \
    .getOrCreate()

print("Spark started!")

# ==============================================================================
# IN-MEMORY DATASET DEFINITION
# Purpose: Define a raw tabular array and its associated field identifiers.
# ==============================================================================
data = [
    (1, "John", "Station A", "Station B", 5.5),
    (2, "Maria", "Station B", "Station C", 6.0),
    (3, "Farooq", "Station A", "Station C", 4.0)
]

columns = ["trip_id", "user", "start_station", "end_station", "cost"]

df = spark.createDataFrame(data, columns)

# ==============================================================================
# DATA FRAME MATERIALIZATION
# Purpose: Print out the complete row-and-column structure to standard output.
# ==============================================================================
print("\nAll Data:")
df.show()

# ==============================================================================
# STRUCTURAL METADATA INSPECTION
# Purpose: Display the data type hierarchy and structural constraints of the schema.
# ==============================================================================
print("\nSchema:")
df.printSchema()

# ==============================================================================
# AGGREGATION ANALYSIS
# Purpose: Partition the dataset by rider and compute the volume of trips per group.
# ==============================================================================
print("\nTrips per user:")
df.groupBy("user").count().show()

# ==============================================================================
# ROW CONDITIONAL FILTERING
# Purpose: Isolate records where the final terminal destination matches a specific hub.
# ==============================================================================
print("\nTrips ending at Station C:")
df.filter(df.end_station == "Station C").show()