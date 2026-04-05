# Distributed Real-Time Leaderboard System

A real-time distributed leaderboard system inspired by [HotlapDaily.com](https://hotlapdaily.com), demonstrating core Computer Networks concepts through a practical racing game application.

## Features

- **Real-time leaderboard updates** across all connected clients (now scales up to top 100 players!)
- **Advanced 2D Racing Physics**: HTML5 Canvas game with AABB rectangle collision, auto-gas/WASD controls, and track curb leniency.
- **Persistent Player Identities**: Uses `localStorage` to remember racer names seamlessly across sessions.
- **F1-Style Visuals**: Color-coded cars mapping to constructor choices with accurate track highlighting.
- **Dual protocol support**: TCP (terminal) + WebSocket (browser)
- **Concurrent client handling** using multithreading
- **Redis-powered** high-performance ranking system
- **High-Performance Load Testing**: Included `asyncio` load tester (`load_test.py`) simulating realistic burst traffic, personal bests, and unexpected disconnects to verify backend stability.
- **ANSI Color-Coded Terminal Logs**: Real-time traffic monitoring distinctly color-coded by protocol (TCP vs WS) and event type.
- **LAN demo ready** for multi-device presentations

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Redis Server

```bash
redis-server
```

### 3. Start the Leaderboard Server

```bash
python main.py
```

You should see:
```
=================================================================
           DISTRIBUTED LEADERBOARD SERVER
=================================================================
[HH:MM:SS] Server started
[HH:MM:SS] TCP Server:       0.0.0.0:5000
[HH:MM:SS] WebSocket Server: 0.0.0.0:8765
[HH:MM:SS] HTTP Server:      0.0.0.0:8080
[HH:MM:SS] Redis:            localhost:6379
-----------------------------------------------------------------
[HH:MM:SS] Waiting for connections...
```

### 4. Play the Game

**Browser (Recommended):**
- Open http://localhost:8080
- Enter your name
- Press SPACE to start racing
- Use arrow keys to drive

**Terminal Client:**
```bash
python client.py
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐                     ┌──────────────┐         │
│   │   Browser    │                     │   Terminal   │         │
│   │  (Game UI)   │                     │   Client     │         │
│   └──────┬───────┘                     └──────┬───────┘         │
│          │                                    │                 │
│          │ WebSocket                          │ TCP Socket      │
│          │ (port 8765)                        │ (port 5000)     │
│          │                                    │                 │
│          └──────────────┬─────────────────────┘                 │
│                         │                                       │
│              ┌──────────▼──────────┐                            │
│              │   Python Server     │                            │
│              │     (main.py)       │                            │
│              └──────────┬──────────┘                            │
│                         │                                       │
│              ┌──────────▼──────────┐                            │
│              │       Redis         │                            │
│              │   (Sorted Sets)     │                            │
│              └─────────────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
distributed-leaderboard-system/
├── main.py                 # Unified server entry point
├── config.py               # Configuration settings
├── client.py               # Terminal TCP client
├── requirements.txt        # Python dependencies
│
├── server/                 # Server modules
│   ├── __init__.py
│   ├── tcp_handler.py      # TCP socket server
│   ├── ws_handler.py       # WebSocket server
│   ├── shared.py           # Shared state & broadcasting
│   └── redis_db.py         # Redis operations
│
├── web/                    # Web frontend
│   ├── index.html          # Game + leaderboard UI
│   ├── css/
│   │   └── style.css       # Dark theme styling
│   └── js/
│       ├── game.js         # Racing game logic
│       ├── websocket.js    # WebSocket client
│       └── leaderboard.js  # Leaderboard display
│
├── docs/
│   └── CN_CONCEPTS.md      # documentation
│
└── legacy/                 # Original files (for reference)
    ├── server.py
    ├── redis_db.py
    └── load_test.py
```

## Computer Networks Concepts Demonstrated

| Concept | Implementation |
|---------|----------------|
| **TCP Socket Programming** | Raw socket server for terminal clients |
| **WebSocket Protocol** | Browser-compatible real-time communication |
| **Client-Server Architecture** | Centralized server handling multiple clients |
| **Multithreading** | Concurrent client handling with threading |
| **Broadcasting** | Real-time updates to all connected clients |
| **Protocol Design** | Custom message formats (text + JSON) |
| **LAN Communication** | WiFi hotspot demo deployment |

## Running the LAN Demo

### Server Laptop

1. Create a WiFi hotspot
2. Note the IP address (usually `192.168.137.1` on Windows)
3. Update `config.py`:
   ```python
   HOST = "0.0.0.0"  # Listen on all interfaces
   ```
4. Run `python main.py`

### Client Devices

Connect to the hotspot, then:

**Browser:** Open `http://192.168.137.1:8080`

**Terminal:**
```bash
python client.py 192.168.137.1
```

## Troubleshooting & Maintenance

### Wipe the Leaderboard (Redis)
If you want to clear the entire leaderboard (perhaps during testing or after a heavy load-testing session), run the following command in your `redis-cli`:

```bash
redis-cli ZREMRANGEBYRANK leaderboard 0 -1
```
This efficiently removes all elements in the 'leaderboard' Sorted Set from rank 0 to -1 (the end).

### Running a Stress Test
To run a simulated load against your server, launch the load tester in a separate terminal:
```bash
python load_test.py
```
This will launch 100 concurrent asynchronous clients that simulate realistic tracking, personal best updates, and random network turbulence, while outputting beautifully color-coded ANSI metrics!

## Technologies Used

| Component | Technology |
|-----------|------------|
| Server Language | Python 3.8+ |
| TCP Server | `socket` module |
| WebSocket Server | `websockets` library |
| Database | Redis (Sorted Sets) |
| Frontend | HTML5 Canvas, JavaScript |
| Styling | CSS3 (Dark theme) |

## Server Logs

The server provides detailed logging for demo purposes:

```
[10:23:45] [TCP ] Connected: LAPTOP-SHRIKAR (192.168.137.2:54321)
[10:23:47] [WS  ] Connected: DESKTOP-SUJAL (192.168.137.3)
[10:23:50] [TCP ] Score from LAPTOP-SHRIKAR: player1 = 9.300s
[10:23:50] [--> ] Broadcasting to 2 clients (TCP: 1, WS: 1)
```

## Documentation

For detailed explanation of Computer Networks concepts, see:
- [docs/CN_CONCEPTS.md](docs/CN_CONCEPTS.md)

## Authors

Computer Networks Mini Project  
**Shrikar Desai** | **Sujal Sachin Yadavi** | **Shreyas P Kulkarni**

## License

This project is for educational purposes.
