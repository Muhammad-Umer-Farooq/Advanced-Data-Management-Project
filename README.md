Here is the clean, perfectly formatted version of your `README.md`.

The main formatting issues in your draft were unclosed code blocks, inconsistent headings, and unformatted script blocks. I fixed the code blocks so GitHub will render them as clean, copy-pasteable snippets, structured your console tables using proper Markdown syntax, and added sleek badges to make the repository look incredibly professional.

You can copy and paste this entire block directly into your `README.md` file:

```markdown
# Distributed City Mobility Platform: Advanced Data Management & Analytics

[![Database](https://img.shields.io/badge/Database-MongoDB%20Atlas-green?style=flat-square&logo=mongodb)](https://www.mongodb.com/)
[![Analytics Engine](https://img.shields.io/badge/Analytics-Apache%20Spark-orange?style=flat-square&logo=apachespark)](https://spark.apache.org/)
[![Language](https://img.shields.io/badge/Language-Python%203.11-blue?style=flat-square&logo=python)](https://www.python.org/)

An advanced data management component for a city mobility platform designed to handle the short-term rental of shared electric vehicles (e-scooters/e-bikes). This repository implements a robust multi-database architecture utilizing **MongoDB Atlas** for operational telemetry and dynamic schema handling, alongside **Apache Spark (PySpark)** and **GraphFrames** for large-scale distributed graph analytics and network centrality scoring.

---

## 📌 Project Overview
Modern micro-mobility platforms generate massive streams of irregular telemetry and highly interconnected trip networks. This project addresses these requirements by building a dual-engine architecture:

1. **Operational Layer (MongoDB)**: Efficient storage of users, trips, inventory, and semi-structured telemetry data. Optimized using target indexing strategies, validation frameworks, and performance profiling.
2. **Analytical Layer (Apache Spark & GraphFrames)**: Distributed extraction, transformation, and structural graph modeling to run network analysis algorithms (PageRank, Degree Centrality) identifying critical bottlenecks and traffic hot-spots in city stations.

---

## 🛠️ Architecture & Technology Stack
* **Runtime Environment**: Python 3.11+ / Java 17 (JDK LTS)
* **Execution Core**: Apache Spark 3.5.x (PySpark Ecosystem)
* **Graph Compute Engine**: Spark GraphFrames (`0.8.3-spark3.5-s_2.13`)
* **Operational Database**: MongoDB Atlas (Cloud Cluster / Local Deployment)
* **OS Compatibility**: Fully optimized for Windows environments via localized Hadoop environment setups (`winutils.exe`).

---

## 📁 Repository Structure
```text
Advanced-Data-Management-Project/
│
├── python/
│   ├── spark_graph_analytics.py  # Spark Engine & GraphFrames Centrality Suite
│   ├── mongo_python.py           # MongoDB Connection & Basic Document CRUD
│   ├── generate_data.py          # Synthetic Data Generator (Users, Trips, Telemetry)
│   ├── benchmark_queries.py      # MongoDB Read/Write Performance Profiler
│   ├── create_indexes.py         # Database Index Optimization Suites
│   ├── run_graph_queries.py      # Analytical Extraction Logic
│   ├── run_scalability_test.py   # System Scalability Profiler
│   └── schema_evolution.py       # NoSQL Dynamic Schema Evolution Tests
│
├── hadoop_tmp/
│   └── bin/winutils.exe          # Windows-native POSIX Permission Simulator
│
├── graphframes-0.8.3-spark3.5-s_2.13.jar  # GraphFrames Driver Extension
├── python/benchmark_results.csv           # Tracked Query Metrics Log
└── README.md                              # Project Documentation

```

---

## 🚀 Execution & Quickstart Guide

### 1. Prerequisites Setup

Ensure your local system has Java 17 installed and your environment variables include path targets for Apache Spark. If running on Windows, the repository already bundles `winutils.exe` under `hadoop_tmp/bin/` to bypass POSIX initialization issues.

### 2. Run Synthetic Mobility Data Simulation

Populate the pipeline variables and test configurations by triggering the local simulation datasets generator:

```bash
python python/generate_data.py

```

### 3. Run NoSQL Database & Indexing Operations

Execute the base database layer tasks, including indexes configuration and schema evaluations:

```bash
python python/create_indexes.py
python python/mongo_python.py

```

### 4. Execute Distributed Spark Graph Analytics

Trigger the PySpark pipeline to spin up the local Spark engine, build the distributed DataFrames, map network vertices/edges, and evaluate station centralities:

```bash
python python/spark_graph_analytics.py

```

---

## 📊 Analytical Core & Algorithmic Results

The network processing core extracts distinct trip sequences, casting vehicle stations as structural **Vertices** and the aggregate user journeys as **Directed Edges**.

### Network Prestige (PageRank Centrality)

Evaluates spatial importance across stations by analyzing structural flow vectors through 5 iterations:

| ID | Station Name | PageRank Centrality Score |
| --- | --- | --- |
| **1** | Station A | `1.0595046379156818` |
| **3** | Station C | `1.0147323489325522` |
| **2** | Station B | `0.9257630131517663` |

> 💡 **Insight**: *Station A* functions as the dominant structural pivot across the graph network, pulling in a disproportionately heavy ratio of incoming rebalancing routes.

### Structural Connectivity (Degree Centrality)

Calculates absolute trip transaction vectors per hub, acting as an alternative execution strategy tailored for Windows native file structures:

| ID | Total Connections (Degree) |
| --- | --- |
| **1** | 694 |
| **3** | 672 |
| **2** | 634 |

---

## 📈 Benchmarks & Performance Engineering

The framework tracks operational query speeds against escalating scale vectors. The internal metrics logs evaluate:

* Index-based read operations vs. unindexed collections.
* Bulk stream writes under high telemetry loads.
* Scalability coefficients during Spark transformation partitioning.

All execution runs automatically append diagnostic runtimes down to a dedicated tracking ledger: `python/benchmark_results.csv`.

---

*Developed as part of the Advanced Data Management and Decision Support Systems curriculum.*

```

```