# Distributed Leaderboard System - Architecture

## Overview

This is a **distributed leaderboard system** built using Python with a centralized client-server architecture. It uses TCP sockets for real-time communication and Redis for persistent, ranked data storage.

---

## High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                         DISTRIBUTED LEADERBOARD SYSTEM                            |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|   +-------------+     +-------------+     +-------------+     +-------------+     |
|   |  Client 1   |     |  Client 2   |     |  Client 3   |     |  Client N   |     |
|   | (Terminal)  |     | (Terminal)  |     | (Terminal)  |     | (Terminal)  |     |
|   | client.py   |     | client.py   |     | client.py   |     | client.py   |     |
|   +------+------+     +------+------+     +------+------+     +------+------+     |
|          |                   |                   |                   |            |
|          |     TCP Socket Connection (Port 5000)                     |            |
|          |           Protocol: "username#score"                      |            |
|          |                   |                   |                   |            |
|          +-------------------+-------------------+-------------------+            |
|                              |                                                    |
|                              v                                                    |
|   +-----------------------------------------------------------------------+       |
|   |                    MULTITHREADED SERVER (server.py)                   |       |
|   |                         127.0.0.1:5000                                |       |
|   |                                                                       |       |
|   |   +---------------+   +---------------+   +---------------+           |       |
|   |   |   Thread 1    |   |   Thread 2    |   |   Thread N    |           |       |
|   |   |handle_client()|   |handle_client()|   |handle_client()|           |       |
|   |   +-------+-------+   +-------+-------+   +-------+-------+           |       |
|   |           |                   |                   |                   |       |
|   |           +-------------------+-------------------+                   |       |
|   |                               |                                       |       |
|   |                               v                                       |       |
|   |                   +-----------------------+                           |       |
|   |                   |    clients_lock       |  Thread Synchronization   |       |
|   |                   |    (Threading Mutex)  |                           |       |
|   |                   +-----------+-----------+                           |       |
|   |                               |                                       |       |
|   |                               v                                       |       |
|   |                   +-----------------------+                           |       |
|   |                   |     broadcast()       |  Send updates to all      |       |
|   |                   |                       |  connected clients        |       |
|   |                   +-----------+-----------+                           |       |
|   |                               |                                       |       |
|   +-----------------------------------------------------------------------+       |
|                                   |                                               |
|                                   v                                               |
|   +-----------------------------------------------------------------------+       |
|   |                 REDIS DATABASE LAYER (redis_db.py)                    |       |
|   |                                                                       |       |
|   |   +-------------------------+   +---------------------------+         |       |
|   |   |     update_score()      |   |    get_leaderboard()      |         |       |
|   |   |  - ZADD (add/update)    |   |  - ZRANGE (get top N)     |         |       |
|   |   |  - ZSCORE (get score)   |   |  - Returns ranked list    |         |       |
|   |   +------------+------------+   +-------------+-------------+         |       |
|   |                |                              |                       |       |
|   +-----------------------------------------------------------------------+       |
|                    |                              |                               |
|                    +---------------+--------------+                               |
|                                    |                                              |
|                                    v                                              |
|   +-----------------------------------------------------------------------+       |
|   |                         REDIS SERVER                                  |       |
|   |                       localhost:6379                                  |       |
|   |                                                                       |       |
|   |                  +---------------------------+                        |       |
|   |                  |       Sorted Set          |                        |       |
|   |                  |     "leaderboard"         |                        |       |
|   |                  |                           |                        |       |
|   |                  |   player1: 70.5 (rank 1)  |                        |       |
|   |                  |   player2: 72.3 (rank 2)  |                        |       |
|   |                  |   player3: 75.1 (rank 3)  |                        |       |
|   |                  |   ...                     |                        |       |
|   |                  +---------------------------+                        |       |
|   |                                                                       |       |
|   +-----------------------------------------------------------------------+       |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

---

## Component Details

### 1. Client Layer (`client.py`)

```
+----------------------------------+
|           CLIENT                 |
+----------------------------------+
|  - Connects to server via TCP    |
|  - Sends: "username#score"       |
|  - Receives: Leaderboard updates |
|  - Runs receive thread           |
+----------------------------------+
         |
         | TCP Socket
         v
      Server
```

**Responsibilities:**
- Establish TCP connection to server
- Send score updates in `username#score` format
- Receive and display leaderboard broadcasts
- Handle user input for score submission

### 2. Server Layer (`server.py`)

```
+--------------------------------------------------+
|                  SERVER                          |
+--------------------------------------------------+
|                                                  |
|  +------------+  +------------+  +------------+  |
|  | Thread 1   |  | Thread 2   |  | Thread N   |  |
|  +-----+------+  +-----+------+  +-----+------+  |
|        |               |               |         |
|        +---------------+---------------+         |
|                        |                         |
|                        v                         |
|              +-----------------+                 |
|              | Shared State    |                 |
|              | - clients[]     |                 |
|              | - clients_lock  |                 |
|              +-----------------+                 |
|                        |                         |
|                        v                         |
|              +-----------------+                 |
|              |  broadcast()    |                 |
|              +-----------------+                 |
|                                                  |
+--------------------------------------------------+
```

**Responsibilities:**
- Accept incoming TCP connections
- Spawn thread per client connection
- Parse incoming messages (`username#score`)
- Update Redis database
- Broadcast leaderboard to all clients

### 3. Database Layer (`redis_db.py`)

```
+------------------------------------------+
|           REDIS DB LAYER                 |
+------------------------------------------+
|                                          |
|  update_score(username, score)           |
|  +------------------------------------+  |
|  | 1. current = ZSCORE leaderboard    |  |
|  | 2. if new < current or not exists: |  |
|  |    ZADD leaderboard score username |  |
|  +------------------------------------+  |
|                                          |
|  get_leaderboard()                       |
|  +------------------------------------+  |
|  | ZRANGE leaderboard 0 9 WITHSCORES  |  |
|  | Returns: [(player, score), ...]    |  |
|  +------------------------------------+  |
|                                          |
+------------------------------------------+
```

**Responsibilities:**
- Manage Redis connection
- Update player scores (keep best/lowest)
- Retrieve top N players with scores
- Automatic ranking via Sorted Set

---

## Data Flow Diagram

```
+----------+         +----------+         +----------+         +----------+
|  Client  |         |  Server  |         | redis_db |         |  Redis   |
+----+-----+         +----+-----+         +----+-----+         +----+-----+
     |                    |                    |                    |
     | 1. Connect         |                    |                    |
     |------------------->|                    |                    |
     |                    |                    |                    |
     | 2. Send            |                    |                    |
     | "alice#72.5"       |                    |                    |
     |------------------->|                    |                    |
     |                    |                    |                    |
     |                    | 3. update_score    |                    |
     |                    | ("alice", 72.5)    |                    |
     |                    |------------------->|                    |
     |                    |                    |                    |
     |                    |                    | 4. ZADD            |
     |                    |                    |------------------->|
     |                    |                    |                    |
     |                    |                    | 5. OK              |
     |                    |                    |<-------------------|
     |                    |                    |                    |
     |                    | 6. get_leaderboard |                    |
     |                    |------------------->|                    |
     |                    |                    |                    |
     |                    |                    | 7. ZRANGE          |
     |                    |                    |------------------->|
     |                    |                    |                    |
     |                    |                    | 8. Results         |
     |                    |                    |<-------------------|
     |                    |                    |                    |
     |                    | 9. Leaderboard     |                    |
     |                    |<-------------------|                    |
     |                    |                    |                    |
     | 10. broadcast()    |                    |                    |
     | (to all clients)   |                    |                    |
     |<-------------------|                    |                    |
     |                    |                    |                    |
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Client** | Python + Sockets | Terminal-based user interface |
| **Server** | Python + Threading | Concurrent connection handling |
| **Database** | Redis (Sorted Set) | Ranked data storage |
| **Protocol** | TCP | Reliable communication |
| **Testing** | load_test.py | Performance testing |

---

## Network Configuration

```
+-------------------+          +-------------------+          +-------------------+
|      CLIENT       |          |      SERVER       |          |      REDIS        |
+-------------------+          +-------------------+          +-------------------+
|                   |          |                   |          |                   |
|  Connects to:     |   TCP    |  Listens on:      |   TCP    |  Listens on:      |
|  127.0.0.1:5000   |--------->|  127.0.0.1:5000   |--------->|  localhost:6379   |
|                   |          |                   |          |                   |
+-------------------+          +-------------------+          +-------------------+
```

| Setting | Value |
|---------|-------|
| Server Host | `127.0.0.1` |
| Server Port | `5000` |
| Redis Host | `localhost` |
| Redis Port | `6379` |
| Leaderboard Key | `"leaderboard"` |
| Top N Display | `10` |

---

## Concurrency Model

```
                    +---------------------------+
                    |      Main Thread          |
                    |   socket.accept() loop    |
                    +-------------+-------------+
                                  |
                                  | spawn
                    +-------------+-------------+
                    |                           |
          +---------v---------+       +---------v---------+
          |     Thread 1      |       |     Thread 2      |
          |  handle_client()  |       |  handle_client()  |
          +---------+---------+       +---------+---------+
                    |                           |
                    |      +----------+         |
                    +----->|  LOCK    |<--------+
                           +----+-----+
                                |
                           +----v-----+
                           | clients  |
                           | list[]   |
                           +----------+
```

**Thread Safety:**
- `clients_lock` - Mutex protecting shared client list
- Redis commands are atomic
- Daemon threads for clean shutdown

---

## Message Protocol

### Client to Server
```
Format: "username#score"
Example: "alice#72.543"
```

### Server to Client (Broadcast)
```
Format: Formatted leaderboard string
Example:
"
--- Leaderboard ---
1. alice - 70.5
2. bob - 72.3
3. charlie - 75.1
-------------------
"
```

---

## File Structure

```
distributed-leaderboard-system/
|
+-- server.py          # Multithreaded TCP server
|
+-- client.py          # Interactive terminal client
|
+-- redis_db.py        # Redis database operations
|
+-- load_test.py       # Performance testing script
|
+-- README.md          # Project documentation
|
+-- ARCHITECTURE.md    # This file
```

---

## Quick Start Sequence

```
+-------------+         +-------------+         +-------------+
|   Step 1    |         |   Step 2    |         |   Step 3    |
+-------------+         +-------------+         +-------------+
|             |         |             |         |             |
| Start Redis |-------->| Start Server|-------->| Run Clients |
|             |         |             |         |             |
| redis-server|         | python      |         | python      |
|             |         | server.py   |         | client.py   |
+-------------+         +-------------+         +-------------+
```

---

## Architectural Characteristics

| Characteristic | Implementation |
|----------------|----------------|
| **Topology** | Star (clients connect to central server) |
| **Scalability** | Vertical (single server instance) |
| **State Management** | Centralized (Redis) |
| **Consistency** | Strong (single Redis instance) |
| **Communication** | Synchronous TCP |
| **Ranking Logic** | Lower score = better rank (racing times) |

---

## Future Improvements

| Current State | Potential Enhancement |
|---------------|----------------------|
| Terminal clients | Web-based dashboard with WebSocket |
| Polling broadcast | Redis Pub/Sub for push notifications |
| No authentication | JWT/OAuth player authentication |
| Single server | Horizontal scaling with load balancer |
| In-memory Redis | Redis persistence + historical data |
| Hardcoded config | Environment variables / config files |
