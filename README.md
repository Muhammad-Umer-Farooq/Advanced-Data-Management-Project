# Advanced Data Management: City Mobility Platform

[![Database](https://img.shields.io/badge/Database-Multi--Model-blue.svg)](#)
[![Python](https://img.shields.io/badge/Language-Python%203.10%2B-green.svg)](#)
[![Academic Project](https://img.shields.io/badge/Academic-Master%27s%20Level-orange.svg)](#)

An advanced, multi-model data management platform built to handle the transactional, sensory, and topological lifecycle of a city-wide electric vehicle sharing platform across various hubs in Italy. This project evaluates database design methodologies, architectural scale performance across relational and document paradigms, graph theory topology analysis, and parallel computing via Apache Spark.

---

## 📌 Project Architecture & Specification

The platform orchestrates and models four core entity tracking blocks over varying database designs:
* **Users:** Demographic profiles and verification vectors of active micro-mobility commuters.
* **Stations:** Geographic terminal nodes managing dock locations, city scopes, and parking caps.
* **Trips:** Main transaction ledger indexing complete checkout-to-checkin user operations.
* **Events:** Sub-second time-series telemetry streams logging diagnostic metrics (`GPS`, `ERROR`, `BATTERY`, `DELAY`).


---

## 🗂️ Project Repository Structure

```text
├── mongodb/
│   └── mongo_queries.txt      # Target optimized NoSQL queries and pipeline aggregations
├── neo4j/
│   └── Neo4j_queires.txt      # Cypher scripts defining node entities and spatial connections
├── postgres/
│   └── mobility db .sql       # Relational DDL tables, referencing schemas, and transactional seeding
├── python/
│   └── mongo_python.py        # Programmatic interface pipeline connecting to MongoDB Atlas DBaaS
├── report/                    # Project documentation, design trade-offs, and scalability analysis
├── spark/
│   └── spark_code.py          # Parallel RDD/DataFrame routines and GraphFrames network analytics
├── .env                       # Local environment configurations (Git-ignored)
└── .gitignore                 # Exclusion configuration manifest for local run runtimes