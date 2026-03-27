# Distributed Leaderboard System - Mini Project

## Computer Networks Mini Project

A real-time distributed leaderboard system inspired by [HotlapDaily.com](https://hotlapdaily.com), demonstrating core computer networking concepts through a practical lap-time tracking application.

---

## Project Concept

### What is HotlapDaily?

HotlapDaily is a popular racing community platform where players submit their best lap times for daily challenges. Players compete globally, and the leaderboard updates in real-time as new times are submitted.

### Our Implementation

We are building a **local network version** of this concept for demonstration purposes:

```
                    ┌─────────────────────────────────────┐
                    │         SERVER LAPTOP               │
                    │     (Hotspot + Redis + Server)      │
                    │                                     │
                    │   ┌─────────┐    ┌─────────────┐   │
                    │   │  Redis  │◄───│  server.py  │   │
                    │   │   DB    │    │  (TCP:5000) │   │
                    │   └─────────┘    └──────┬──────┘   │
                    └─────────────────────────┼──────────┘
                                              │
                           WiFi Hotspot (LAN) │
                    ┌─────────────────────────┼──────────┐
                    │                         │          │
          ┌─────────▼─────────┐     ┌─────────▼─────────┐
          │    CLIENT 1       │     │    CLIENT 2       │
          │  (Laptop/Phone)   │     │  (Laptop/Phone)   │
          │                   │     │                   │
          │  - Submit laps    │     │  - Submit laps    │
          │  - View live      │     │  - View live      │
          │    leaderboard    │     │    leaderboard    │
          └───────────────────┘     └───────────────────┘
                    │                         │
          ┌─────────▼─────────┐     ┌─────────▼─────────┐
          │    CLIENT 3       │     │    CLIENT 4       │
          │  (Laptop/Phone)   │     │  (Laptop/Phone)   │
          └───────────────────┘     └───────────────────┘
```

---

## Demo Setup

### Hardware Requirements

| Component | Quantity | Purpose |
|-----------|----------|---------|
| Server Laptop | 1 | Hosts hotspot, Redis, and server |
| Client Laptops | 4-5 | Connect to hotspot, submit lap times |

### Network Configuration

1. **Server Laptop** creates a WiFi hotspot
2. **Client Laptops** connect to this hotspot
3. All devices are on the same local network (LAN)
4. Server listens on its local IP (e.g., `192.168.137.1:5000`)

---

## How It Works

### Workflow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client     │     │   Server     │     │    Redis     │     │ All Clients  │
│  submits lap │────►│  receives    │────►│   updates    │────►│   receive    │
│    time      │     │  & processes │     │  leaderboard │     │  broadcast   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

1. **Client connects** to server via TCP socket
2. **Client submits** lap time (e.g., `player1#72.543`)
3. **Server receives** the data and updates Redis
4. **Redis maintains** sorted leaderboard (best times first)
5. **Server broadcasts** updated leaderboard to ALL connected clients
6. **All clients** see the leaderboard update in real-time

### Real-Time Updates

When any player submits a new lap time:
- The leaderboard is immediately recalculated
- ALL connected clients receive the update
- Displays refresh automatically on every client terminal

---

## Computer Networks Concepts Demonstrated

| Concept | Implementation |
|---------|----------------|
| **TCP Socket Programming** | Reliable client-server communication |
| **Client-Server Architecture** | Centralized server handling multiple clients |
| **Multithreading** | Concurrent handling of multiple client connections |
| **Broadcasting** | Server sends updates to all connected clients |
| **LAN Communication** | Devices communicate over local WiFi hotspot |
| **Protocol Design** | Simple `username#score` message format |
| **Real-Time Systems** | Instant leaderboard updates across network |

---

## Demo Scenario

### Setup Phase
1. Start Redis on server laptop
2. Start `server.py` on server laptop
3. Create WiFi hotspot on server laptop
4. Connect 4-5 client laptops to hotspot
5. Run `client.py` on each client (pointing to server IP)

### Demo Flow

```
Timeline:
─────────────────────────────────────────────────────────────►

    Player1 submits    Player3 submits    Player2 submits
       72.5s              71.2s              70.8s
         │                  │                  │
         ▼                  ▼                  ▼
    ┌─────────┐        ┌─────────┐        ┌─────────┐
    │ Board:  │        │ Board:  │        │ Board:  │
    │ 1. P1   │───────►│ 1. P3   │───────►│ 1. P2   │
    │    72.5 │        │ 2. P1   │        │ 2. P3   │
    └─────────┘        └─────────┘        │ 3. P1   │
                                          └─────────┘
    
    All clients see     All clients see    All clients see
    this instantly      this instantly     this instantly
```

### What Viewers Will See

Each client terminal displays:
```
🏁 LIVE LEADERBOARD

--- Leaderboard ---
1. player2 - 70.8
2. player3 - 71.2
3. player1 - 72.5
4. player4 - 73.1
5. player5 - 75.0
-------------------
```

The leaderboard updates **instantly** on ALL screens when anyone submits a new time.

---

## Key Features for Demo

| Feature | Description |
|---------|-------------|
| **Instant Updates** | Leaderboard refreshes on all clients immediately |
| **Best Time Tracking** | Only keeps each player's best (lowest) lap time |
| **Automatic Ranking** | Redis Sorted Sets handle ranking automatically |
| **Concurrent Connections** | Multiple players can submit simultaneously |
| **Network Demonstration** | Shows real LAN communication between devices |

---

## Files Overview

```
distributed-leaderboard-system/
├── server.py       # TCP server (runs on server laptop)
├── client.py       # Client app (runs on client laptops)
├── redis_db.py     # Redis operations (leaderboard logic)
├── load_test.py    # Simulate many clients for stress testing
├── README.md       # Technical documentation
└── ARCHITECTURE.md # System architecture details
```

---

## Running the Demo

### On Server Laptop

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start server (update HOST to hotspot IP)
python server.py
```

### On Client Laptops

```bash
# Update HOST in client.py to server's hotspot IP
python client.py
```

### Configuration Changes for Demo

In `server.py`:
```python
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 5000
```

In `client.py`:
```python
HOST = "192.168.137.1"  # Server's hotspot IP
PORT = 5000
```

---

## Why This Project?

This mini project effectively demonstrates:

1. **Practical Networking** - Real devices communicating over a network
2. **Distributed Systems** - Multiple clients, centralized server
3. **Real-Time Communication** - Instant updates across all clients
4. **Concurrency** - Handling multiple simultaneous connections
5. **Protocol Design** - Simple, effective message format
6. **Database Integration** - Redis for fast data operations

---

## Comparison with HotlapDaily

| Feature | HotlapDaily.com | Our Demo |
|---------|-----------------|----------|
| Network | Internet (Global) | WiFi Hotspot (Local) |
| Scale | Thousands of users | 4-5 laptops |
| Frontend | Web Dashboard | Terminal UI |
| Backend | Cloud Servers | Single Laptop |
| Database | Production DB | Redis (local) |
| Core Concept | Same - Real-time leaderboard updates |

---

## Learning Outcomes

By completing this project, we demonstrate understanding of:

- Socket programming (TCP)
- Client-server architecture
- Multithreaded server design
- Network broadcasting
- LAN configuration and communication
- Real-time data synchronization
- Database integration for rankings

---

## Authors

Computer Networks Mini Project  
Shrikar Desai | Sujal Sachin Yadavi | Shreyas P Kulkarni
