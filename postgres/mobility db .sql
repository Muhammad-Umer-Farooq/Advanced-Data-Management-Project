/* 
================================================================================
  ENVIRONMENT INITIALIZATION
  Destroys existing relational structures to ensure an error-free, clean slate.
  Dependencies are dropped sequentially from leaf tables to core parent entities.
================================================================================
*/
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS stations;
DROP TABLE IF EXISTS users;

/* 
================================================================================
  SCHEMA DEFINITION & DATA SEEDING: USERS
  Maintains the profile definitions and demographic insights of system riders.
================================================================================
*/
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    surname VARCHAR(50),
    birthdate DATE,
    country VARCHAR(50)
);

-- Populating initial commuter registration records
INSERT INTO users (name, surname, birthdate, country) VALUES
('John', 'Doe', '1995-05-10', 'USA'),
('Maria', 'Rossi', '1998-03-15', 'Italy'),
('Farooq', 'Muhammad', '2000-07-20', 'Pakistan');

/* 
================================================================================
  SCHEMA DEFINITION & DATA SEEDING: STATIONS
  Tracks the geometric nodes, location contexts, and docking capacities of the network.
================================================================================
*/
CREATE TABLE stations (
    station_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    city VARCHAR(50),
    capacity INT
);

-- Populating physical terminal node coordinates
INSERT INTO stations (name, city, capacity) VALUES
('Station A', 'Milan', 10),
('Station B', 'Rome', 15),
('Station C', 'Naples', 12);

/* 
================================================================================
  SCHEMA DEFINITION & DATA SEEDING: TRIPS
  The transactional backbone mapping customer activity between checkout nodes.
================================================================================
*/
CREATE TABLE trips (
    trip_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    start_station_id INT REFERENCES stations(station_id),
    end_station_id INT REFERENCES stations(station_id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    total_cost FLOAT
);

-- Populating historical mobility rental entries
INSERT INTO trips (user_id, start_station_id, end_station_id, start_time, end_time, total_cost) VALUES
(1, 1, 2, '2024-04-01 10:00:00', '2024-04-01 10:30:00', 5.5),
(2, 2, 3, '2024-04-02 11:00:00', '2024-04-02 11:45:00', 6.0),
(3, 1, 3, '2024-04-03 09:00:00', '2024-04-03 09:25:00', 4.0);

/* 
================================================================================
  SCHEMA DEFINITION & DATA SEEDING: EVENTS
  Telemetry log storing fine-grained sensory checkpoints and runtime state flags.
================================================================================
*/
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    trip_id INT REFERENCES trips(trip_id),
    timestamp TIMESTAMP,
    event_type VARCHAR(20),
    value FLOAT
);

-- Populating mid-transit diagnostic messages and status logs
INSERT INTO events (trip_id, timestamp, event_type, value) VALUES
(1, '2024-04-01 10:10:00', 'GPS', 1.1),
(1, '2024-04-01 10:20:00', 'ERROR', 0.0),
(2, '2024-04-02 11:20:00', 'BATTERY', 75),
(3, '2024-04-03 09:10:00', 'DELAY', 2.5);

/* 
================================================================================
  ANALYTICAL PROCESSING LAYER
================================================================================
*/

-- Query 1: Extract complete route details including the commuter's name and station locations
SELECT 
    t.trip_id,
    u.name AS user_name,
    s1.name AS start_station,
    s2.name AS end_station
FROM trips t
JOIN users u ON t.user_id = u.user_id
JOIN stations s1 ON t.start_station_id = s1.station_id
JOIN stations s2 ON t.end_station_id = s2.station_id;

-- Query 2: Calculate user-specific metrics to evaluate total rides completed and their average flight time in minutes
SELECT 
    u.name,
    COUNT(t.trip_id) AS total_trips,
    AVG(EXTRACT(EPOCH FROM (t.end_time - t.start_time))/60) AS avg_duration_minutes
FROM users u
JOIN trips t ON u.user_id = t.user_id
GROUP BY u.name;

-- Query 3: Measure traffic volume at each hub by tallying the total departures and arrivals
SELECT 
    s.name,
    COUNT(t.start_station_id) AS trips_started,
    COUNT(t.end_station_id) AS trips_ended
FROM stations s
LEFT JOIN trips t 
ON s.station_id = t.start_station_id 
OR s.station_id = t.end_station_id
GROUP BY s.name;

-- Query 4: Isolate unique journey identifiers that encountered operational faults or critical system issues
SELECT DISTINCT t.trip_id
FROM trips t
JOIN events e ON t.trip_id = e.trip_id
WHERE e.event_type = 'ERROR';