# Computer Networks Concepts - Viva Documentation

## Distributed Real-Time Leaderboard System

This document explains all the Computer Networks concepts demonstrated in this project, designed to help you prepare for your viva/presentation.

---

## Table of Contents

1. [Socket Programming](#1-socket-programming)
2. [TCP Protocol](#2-tcp-protocol)
3. [Client-Server Architecture](#3-client-server-architecture)
4. [Multithreading & Concurrency](#4-multithreading--concurrency)
5. [Broadcasting](#5-broadcasting)
6. [Protocol Design](#6-protocol-design)
7. [WebSocket Protocol](#7-websocket-protocol)
8. [LAN Communication](#8-lan-communication)
9. [Code References](#9-code-references)
10. [Viva Questions & Answers](#10-viva-questions--answers)

---

## 1. Socket Programming

### What is a Socket?

A **socket** is an endpoint for communication between two machines over a network. It's like a "door" through which data can be sent and received.

```
┌─────────────────┐         Network          ┌─────────────────┐
│    Machine A    │                          │    Machine B    │
│                 │                          │                 │
│   Application   │                          │   Application   │
│        │        │                          │        │        │
│   ┌────▼────┐   │      Data Flow           │   ┌────▼────┐   │
│   │ Socket  │◄──┼──────────────────────────┼──►│ Socket  │   │
│   │ (Port)  │   │                          │   │ (Port)  │   │
│   └─────────┘   │                          │   └─────────┘   │
│                 │                          │                 │
└─────────────────┘                          └─────────────────┘
```

### Socket API Functions

| Function | Purpose | Used In |
|----------|---------|---------|
| `socket()` | Create a new socket | `server.py`, `client.py` |
| `bind()` | Associate socket with IP:Port | `server.py` |
| `listen()` | Mark socket as passive (server) | `server.py` |
| `accept()` | Wait for and accept connection | `server.py` |
| `connect()` | Establish connection to server | `client.py` |
| `send()` | Send data through socket | Both |
| `recv()` | Receive data from socket | Both |
| `close()` | Close the socket | Both |

### Code Example (from our project)

```python
# Server-side socket creation
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))      # Bind to address
server.listen(5)               # Start listening

# Accept client connection
client_socket, addr = server.accept()

# Receive and send data
data = client_socket.recv(1024)
client_socket.send(response.encode())
```

### Socket Types

| Type | Protocol | Description |
|------|----------|-------------|
| `SOCK_STREAM` | TCP | Reliable, ordered, connection-oriented |
| `SOCK_DGRAM` | UDP | Unreliable, unordered, connectionless |

**Our project uses `SOCK_STREAM` (TCP) because:**
- Leaderboard data must be delivered reliably
- Order matters (newest update should be last)
- We need acknowledgment that data was received

---

## 2. TCP Protocol

### What is TCP?

**Transmission Control Protocol (TCP)** is a transport layer protocol that provides:
- **Reliable delivery** - Data is guaranteed to arrive
- **Ordered delivery** - Data arrives in the same order it was sent
- **Error checking** - Corrupted data is retransmitted
- **Flow control** - Prevents sender from overwhelming receiver
- **Connection-oriented** - Connection must be established before data transfer

### TCP 3-Way Handshake

Before data can be sent, TCP establishes a connection using a 3-way handshake:

```
   Client                                Server
      │                                     │
      │───────── SYN (seq=x) ──────────────►│
      │          "I want to connect"        │
      │                                     │
      │◄────── SYN-ACK (seq=y, ack=x+1) ────│
      │       "OK, I acknowledge"           │
      │                                     │
      │───────── ACK (ack=y+1) ────────────►│
      │          "Connection established"   │
      │                                     │
      │◄═══════ DATA TRANSFER ══════════════│
      │                                     │
```

**In our project:** Every time `client.py` connects to `server.py`, this handshake happens automatically (handled by OS).

### TCP vs UDP Comparison

| Feature | TCP | UDP |
|---------|-----|-----|
| Connection | Required (3-way handshake) | Not required |
| Reliability | Guaranteed delivery | Best effort |
| Ordering | Maintained | Not guaranteed |
| Speed | Slower (overhead) | Faster |
| Use case | Web, Email, Leaderboards | Gaming, Streaming, DNS |

**Why TCP for our leaderboard?**
- Every score must be received (reliability)
- All clients must see same order (consistency)
- We need confirmation of delivery

---

## 3. Client-Server Architecture

### What is Client-Server?

A computing model where:
- **Server**: Provides services, always running, waits for requests
- **Client**: Requests services, initiates communication

```
                    ┌─────────────────────┐
                    │       SERVER        │
                    │                     │
                    │  - Waits for clients│
                    │  - Processes requests│
                    │  - Sends responses  │
                    │                     │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
     ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
     │  CLIENT 1   │    │  CLIENT 2   │    │  CLIENT N   │
     │             │    │             │    │             │
     │ - Initiates │    │ - Initiates │    │ - Initiates │
     │ - Requests  │    │ - Requests  │    │ - Requests  │
     │ - Displays  │    │ - Displays  │    │ - Displays  │
     └─────────────┘    └─────────────┘    └─────────────┘
```

### In Our Project

| Component | Role | File |
|-----------|------|------|
| Leaderboard Server | Central server handling all clients | `main.py` |
| Terminal Client | TCP client for manual testing | `client.py` |
| Browser Client | WebSocket client (game) | `web/js/websocket.js` |
| Redis | Database server | External |

### Request-Response Flow

```
1. Client connects to server
2. Client sends: "HELLO#LAPTOP-NAME"
3. Server registers client
4. Client sends: "player1#9.300" (score)
5. Server processes score
6. Server broadcasts to ALL clients
7. All clients update their displays
```

---

## 4. Multithreading & Concurrency

### Why Multithreading?

Without multithreading, the server can only handle **one client at a time**:

```
Single-threaded (BAD):
Client1 connects → Server busy
Client2 connects → BLOCKED (waiting)
Client3 connects → BLOCKED (waiting)
```

With multithreading, multiple clients are handled **simultaneously**:

```
Multi-threaded (GOOD):
Client1 connects → Thread 1 handles
Client2 connects → Thread 2 handles
Client3 connects → Thread 3 handles
```

### Thread Per Client Model

```
                    ┌─────────────────────────────────┐
                    │         MAIN THREAD             │
                    │                                 │
                    │    while True:                  │
                    │        client = accept()        │
                    │        spawn_thread(client)     │
                    └─────────────┬───────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
┌────────▼────────┐      ┌────────▼────────┐      ┌────────▼────────┐
│    THREAD 1     │      │    THREAD 2     │      │    THREAD N     │
│ handle_client() │      │ handle_client() │      │ handle_client() │
│    Client 1     │      │    Client 2     │      │    Client N     │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

### Thread Synchronization

**Problem:** Multiple threads accessing shared data can cause **race conditions**.

**Solution:** Use a **lock (mutex)** to ensure only one thread accesses shared data at a time.

```python
# In our project (server/shared.py)
clients_lock = threading.Lock()

# Safe access to shared client list
with clients_lock:
    clients[socket] = client_info  # Only one thread at a time
```

### Code Example

```python
# From server/tcp_handler.py
def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    
    while True:
        client_socket, addr = server.accept()  # Blocks until connection
        
        # Spawn new thread for this client
        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, addr),
            daemon=True  # Thread dies when main program exits
        )
        thread.start()
```

---

## 5. Broadcasting

### What is Broadcasting?

Sending the same message to **all connected clients** simultaneously.

```
        Server receives update
                 │
                 ▼
    ┌────────────────────────┐
    │   for client in all:   │
    │       send(message)    │
    └────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
 Client1      Client2      Client3
 (updated)    (updated)    (updated)
```

### Implementation in Our Project

```python
# From server/shared.py
def broadcast_to_tcp(message: str) -> int:
    # Get snapshot of all clients
    with clients_lock:
        clients_snapshot = list(tcp_clients.keys())
    
    # Send to each client
    for client_socket in clients_snapshot:
        try:
            client_socket.send(message.encode())
        except:
            # Handle dead clients
            pass
```

### Why Snapshot?

We copy the client list before iterating because:
1. Clients might disconnect during broadcast
2. New clients might connect during broadcast
3. Prevents holding the lock too long

---

## 6. Protocol Design

### What is an Application Protocol?

Rules for how data is formatted and exchanged between applications.

### Our Protocol Design

**TCP Protocol (Terminal Clients):**

```
# Message format
username#score

# Examples
HELLO#LAPTOP-SHRIKAR       # Identification
player1#9.300              # Score submission

# Server response
LEADERBOARD
--- Leaderboard ---
1. player1 - 9.300s
2. player2 - 9.450s
-------------------
```

**WebSocket Protocol (Browser Clients):**

```json
// Client -> Server
{"type": "hello", "hostname": "BROWSER-USER"}
{"type": "submit", "username": "player1", "score": 9.300}

// Server -> Client
{"type": "leaderboard", "data": [
    {"rank": 1, "username": "player1", "score": 9.300},
    {"rank": 2, "username": "player2", "score": 9.450}
]}
```

### Design Decisions

| Choice | Reason |
|--------|--------|
| `#` delimiter (TCP) | Simple to parse, unlikely in usernames |
| JSON (WebSocket) | Native JavaScript support, structured data |
| Score as float | Millisecond precision for lap times |
| Type field in JSON | Easy message routing |

---

## 7. WebSocket Protocol

### What is WebSocket?

A protocol that provides **full-duplex communication** over a single TCP connection, designed for web browsers.

### WebSocket vs HTTP

| HTTP | WebSocket |
|------|-----------|
| Request-response only | Full-duplex (both ways) |
| Connection per request | Persistent connection |
| Server can't push | Server can push anytime |
| High overhead | Low overhead |

### WebSocket Handshake (HTTP Upgrade)

```
Client → Server:
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==

Server → Client:
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=

[Connection is now WebSocket, not HTTP]
```

### Why WebSocket for Browser?

Browsers **cannot** open raw TCP sockets (security restriction). WebSocket is the only way to maintain a persistent, bidirectional connection from a browser.

### In Our Project

```javascript
// web/js/websocket.js
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
    ws.send(JSON.stringify({type: 'hello', hostname: 'Browser'}));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'leaderboard') {
        updateDisplay(data.data);
    }
};
```

---

## 8. LAN Communication

### Local Area Network Setup

```
                   ┌─────────────────────────────────┐
                   │         SERVER LAPTOP           │
                   │                                 │
                   │  WiFi Hotspot: 192.168.137.1    │
                   │  Running: main.py               │
                   │                                 │
                   └─────────────────┬───────────────┘
                                     │ WiFi
            ┌────────────────────────┼────────────────────────┐
            │                        │                        │
  ┌─────────▼─────────┐    ┌─────────▼─────────┐    ┌─────────▼─────────┐
  │   CLIENT LAPTOP   │    │   CLIENT LAPTOP   │    │   PHONE/TABLET    │
  │   192.168.137.2   │    │   192.168.137.3   │    │   192.168.137.4   │
  │                   │    │                   │    │                   │
  │   client.py       │    │   Browser         │    │   Browser         │
  └───────────────────┘    └───────────────────┘    └───────────────────┘
```

### Configuration for LAN Demo

**Server (config.py):**
```python
HOST = "0.0.0.0"  # Listen on ALL interfaces
```

**Client:**
```python
HOST = "192.168.137.1"  # Server's hotspot IP
```

**Browser:**
```
http://192.168.137.1:8080
```

### Steps to Run LAN Demo

1. **Server laptop:** Create WiFi hotspot
2. **Server laptop:** Note the IP (usually 192.168.137.1)
3. **Server laptop:** Run `python main.py`
4. **Client laptops:** Connect to hotspot
5. **Client laptops:** Run `python client.py 192.168.137.1` or open browser

---

## 9. Code References

### Key Files and Concepts

| File | CN Concepts |
|------|-------------|
| `server/tcp_handler.py` | TCP socket server, multithreading, accept loop |
| `server/ws_handler.py` | WebSocket protocol, async I/O |
| `server/shared.py` | Thread synchronization, broadcasting |
| `client.py` | TCP client, socket connection |
| `web/js/websocket.js` | WebSocket client, message handling |

### Important Code Sections

**TCP Server (socket, bind, listen, accept):**
`server/tcp_handler.py:100-130`

**Thread per client:**
`server/tcp_handler.py:125-135`

**Broadcasting:**
`server/shared.py:140-170`

**WebSocket handling:**
`server/ws_handler.py:40-100`

---

## 10. Viva Questions & Answers

### Basic Questions

**Q: What is a socket?**
A: A socket is an endpoint for communication between two machines. It's identified by an IP address and port number.

**Q: Why did you use TCP instead of UDP?**
A: TCP provides reliable, ordered delivery which is essential for a leaderboard. Every score must be received and in the correct order.

**Q: What is the 3-way handshake?**
A: The process TCP uses to establish a connection:
1. Client sends SYN
2. Server responds with SYN-ACK
3. Client sends ACK
Connection is now established.

### Intermediate Questions

**Q: How do you handle multiple clients?**
A: We use multithreading. Each client gets its own thread (handle_client function) that runs concurrently.

**Q: What is a race condition and how do you prevent it?**
A: A race condition occurs when multiple threads access shared data simultaneously. We prevent it using a mutex (threading.Lock) to ensure only one thread accesses shared data at a time.

**Q: Explain your message protocol.**
A: For TCP: `username#score` format (e.g., "player1#9.300")
For WebSocket: JSON objects with type field (e.g., `{"type": "submit", "username": "player1", "score": 9.3}`)

### Advanced Questions

**Q: Why use WebSocket for browsers instead of raw TCP?**
A: Browsers cannot open raw TCP sockets due to security restrictions. WebSocket is the only protocol that provides persistent, bidirectional communication for web applications.

**Q: How does WebSocket relate to TCP?**
A: WebSocket is built ON TOP of TCP. It starts with an HTTP handshake (upgrade request), then uses the underlying TCP connection for full-duplex communication.

**Q: Explain your broadcasting mechanism.**
A: When a score is received:
1. Update Redis database
2. Get snapshot of all connected clients (holding lock)
3. Release lock
4. Send update to each client
5. Handle any failed sends (remove dead clients)

**Q: What's the difference between blocking and non-blocking I/O?**
A: Blocking I/O (like `socket.recv()`) pauses the thread until data arrives. Non-blocking allows the program to continue and check later. We use blocking I/O in separate threads to simulate non-blocking behavior.

---

## Summary

This project demonstrates these key Computer Networks concepts:

1. **Socket Programming** - Creating network endpoints for communication
2. **TCP Protocol** - Reliable, ordered data transmission
3. **Client-Server Model** - Centralized architecture with multiple clients
4. **Multithreading** - Handling concurrent connections
5. **Broadcasting** - Sending updates to all connected clients
6. **Protocol Design** - Defining message formats for communication
7. **WebSocket** - Modern web-based real-time communication
8. **LAN Communication** - Local network deployment

---

## Authors

Computer Networks Mini Project  
Shrikar Desai | Sujal Sachin Yadavi | Shreyas P Kulkarni
