# Distributed Real-Time Leaderboard System

## Overview

This project implements a **Distributed Real-Time Leaderboard System** using a **client–server architecture**. Multiple clients can send score updates to a centralized server simultaneously. The server processes these updates concurrently and stores the rankings in **Redis**, which maintains a sorted leaderboard.

The system demonstrates key distributed system concepts such as **concurrent connections, real-time updates, and efficient ranking management**.

---

## Features

* **Real-time leaderboard updates**
* **Concurrent client connections using multithreading**
* **High-performance leaderboard storage using Redis Sorted Sets**
* **Automatic ranking updates**
* **Simulated load testing with multiple clients**
* **Live leaderboard display in client terminals**

---

## System Architecture

The system follows a **client-server architecture** with Redis as the database.

```
Clients
   │
   │ TCP Socket Connections
   ▼
Multithreaded Python Server
   │
   │ Redis Commands (ZADD, ZRANGE)
   ▼
Redis Database (Sorted Set Leaderboard)
   │
   ▼
Updated Leaderboard Broadcast to Clients
```

---

## Project Structure

```
leaderboard_project/
│
├── server.py        # Multithreaded TCP server
├── client.py        # Manual client for testing
├── redis_db.py      # Redis database operations
├── load_test.py     # Simulates multiple players
└── README.md
```

---

## Technologies Used

| Component            | Technology             |
| -------------------- | ---------------------- |
| Programming Language | Python                 |
| Networking           | TCP Socket Programming |
| Concurrency          | Multithreading         |
| Database             | Redis                  |
| Data Structure       | Redis Sorted Sets      |

---

## Why Redis?

Redis is used because it provides **fast in-memory data structures** and supports **Sorted Sets**, which are ideal for leaderboard systems.

Advantages:

* **Automatic ranking** of players
* **Atomic updates** (no race conditions)
* **High throughput** for frequent score updates
* **Efficient retrieval of top players**

Example Redis commands used:

```
ZADD leaderboard score username
ZRANGE leaderboard 0 9 WITHSCORES
```

---

## Installation

### 1. Install Python Dependencies

```
pip install redis
```

### 2. Install Redis

Download Redis for Windows from:

https://github.com/tporadowski/redis/releases

Extract and run:

```
redis-server.exe
```

You should see:

```
Ready to accept connections
```

---

## How to Run the Project

### Step 1: Start Redis Server

```
redis-server
```

---

### Step 2: Start the Leaderboard Server

```
python server.py
```

Expected output:

```
Server started...
Listening on 127.0.0.1:5000
```

---

### Step 3: Run Manual Client

```
python client.py
```

Example input:

```
Enter username: alex
Enter lap time: 90
```

---

### Step 4: Simulate Multiple Players

To simulate many players sending scores simultaneously:

```
python load_test.py
```

This creates **multiple concurrent clients** that continuously update scores.

---

## Checking Data in Redis

Open Redis CLI:

```
redis-cli
```

View leaderboard:

```
ZRANGE leaderboard 0 -1 WITHSCORES
```

Example output:

```
player19 70
player23 70
player26 71
player54 72
```

---

## Workflow

1. Client connects to server using TCP.
2. Client sends score update in format `username#score`.
3. Server receives the update and processes it in a separate thread.
4. Server updates the leaderboard stored in Redis.
5. Redis maintains the sorted ranking.
6. Server retrieves the updated leaderboard.
7. Server broadcasts the leaderboard to all connected clients.

---

## Example Output

```
🏁 LIVE LEADERBOARD

1. player19 - 70
2. player23 - 70
3. player33 - 71
4. player54 - 72
5. player10 - 73
```

---

## Future Improvements

* Web-based leaderboard dashboard
* Redis Pub/Sub for real-time notifications
* Authentication for players
* Horizontal scaling using multiple servers
* Persistent storage for long-term score history

---

## Learning Outcomes

This project demonstrates:

* Socket programming using TCP
* Multithreaded server architecture
* Concurrent client handling
* Redis database integration
* Real-time leaderboard systems used in multiplayer games

---

## Author

Developed as part of a **Computer Networks / Distributed Systems mini project**.
