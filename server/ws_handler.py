"""
WebSocket Server Handler for Distributed Leaderboard System

This module implements the WebSocket server for browser clients.
WebSocket provides full-duplex communication over a single TCP connection,
making it ideal for real-time web applications.

Computer Networks Concepts Demonstrated:

1. WebSocket Protocol
   - Built on top of TCP
   - Starts with HTTP upgrade handshake
   - Full-duplex communication
   - Message framing (not raw byte stream)

2. Comparison with Raw TCP
   - TCP: Raw byte stream, manual framing
   - WebSocket: Message-based, browser-compatible

3. Async I/O
   - Non-blocking operations
   - Event-driven architecture

Protocol (JSON):
    Client -> Server:
        {"type": "hello", "hostname": "BROWSER-USER"}
        {"type": "submit", "username": "player1", "score": 9.300}
    
    Server -> Client:
        {"type": "leaderboard", "data": [...]}
"""

import asyncio
import json
import websockets
from websockets.server import WebSocketServerProtocol
from typing import Set

from config import HOST, WS_PORT
from server.shared import (
    register_ws_client,
    unregister_ws_client,
    update_ws_hostname,
    broadcast_leaderboard,
    log,
    ws_clients,
    clients_lock
)
from server.redis_db import update_score, get_leaderboard, get_leaderboard_json

# =============================================================================
# WEBSOCKET CLIENT HANDLER
# =============================================================================

async def handle_ws_client(websocket: WebSocketServerProtocol) -> None:
    """
    Handle a single WebSocket client connection
    
    This is an async function that handles the WebSocket connection lifecycle:
    1. Register client on connect
    2. Process incoming messages
    3. Unregister client on disconnect
    
    Args:
        websocket: The WebSocket connection object
        
    Computer Networks Concepts:
        - Async/await: Non-blocking I/O
        - WebSocket frames: Message-based protocol
        - JSON: Application layer data format
    """
    # Get client IP from connection
    try:
        ip = websocket.remote_address[0] if websocket.remote_address else "Unknown"
    except:
        ip = "Unknown"
    
    # Register client with initial hostname
    register_ws_client(websocket, ip, "Browser")
    
    # Send current leaderboard to new client
    try:
        leaderboard_json = get_leaderboard_json()
        welcome_msg = json.dumps({
            "type": "leaderboard",
            "data": leaderboard_json
        })
        await websocket.send(welcome_msg)
    except Exception as e:
        log("ERR", f"Error sending welcome message: {e}")
    
    try:
        # Main message loop
        async for message in websocket:
            try:
                # Parse JSON message
                data = json.loads(message)
                msg_type = data.get("type", "")
                
                # Handle hello message (client identification)
                if msg_type == "hello":
                    hostname = data.get("hostname", "Browser")
                    update_ws_hostname(websocket, hostname)
                    continue
                
                # Handle score submission
                if msg_type == "submit":
                    username = data.get("username", "").strip()
                    score = data.get("score", 0)
                    
                    if not username:
                        continue
                    
                    try:
                        score = float(score)
                    except (ValueError, TypeError):
                        continue
                    
                    # Get client hostname for logging
                    with clients_lock:
                        client_info = ws_clients.get(websocket, {})
                        hostname = client_info.get("hostname", "Browser")
                    
                    # Update score in Redis
                    updated = update_score(username, score)
                    
                    if updated:
                        log("WS", f"Score from {hostname}: {username} = {score:.3f}s")
                    else:
                        log("WS", f"Score from {hostname}: {username} = {score:.3f}s (not best)")
                    
                    # Broadcast updated leaderboard to ALL clients
                    leaderboard_text = get_leaderboard()
                    leaderboard_json = get_leaderboard_json()
                    
                    # For WebSocket broadcast, we need to do it async
                    await broadcast_to_all_ws(leaderboard_json)
                    
                    # Also broadcast to TCP clients (sync)
                    from server.shared import broadcast_to_tcp
                    tcp_message = "LEADERBOARD\n" + leaderboard_text
                    broadcast_to_tcp(tcp_message)
                    
                    # Log broadcast
                    from server.shared import get_client_count
                    tcp_count, ws_count, total = get_client_count()
                    log("-->", f"Broadcasting to {total} clients (TCP: {tcp_count}, WS: {ws_count})")
                    
            except json.JSONDecodeError:
                log("ERR", f"Invalid JSON from WebSocket client: {message[:50]}")
            except Exception as e:
                log("ERR", f"WebSocket message error: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        log("ERR", f"WebSocket client error: {e}")
    finally:
        # Clean up
        unregister_ws_client(websocket)

# =============================================================================
# WEBSOCKET BROADCAST
# =============================================================================

async def broadcast_to_all_ws(leaderboard_json: list) -> None:
    """
    Broadcast leaderboard to all connected WebSocket clients
    
    Args:
        leaderboard_json: List of leaderboard entries
    """
    message = json.dumps({
        "type": "leaderboard",
        "data": leaderboard_json
    })
    
    dead_clients = []
    
    with clients_lock:
        clients_snapshot = list(ws_clients.keys())
    
    for ws in clients_snapshot:
        try:
            await ws.send(message)
        except:
            dead_clients.append(ws)
    
    # Clean up dead clients
    if dead_clients:
        with clients_lock:
            for dc in dead_clients:
                if dc in ws_clients:
                    del ws_clients[dc]

# =============================================================================
# WEBSOCKET SERVER
# =============================================================================

async def start_ws_server(host: str = HOST, port: int = WS_PORT) -> None:
    """
    Start the WebSocket server
    
    This creates an async WebSocket server that handles browser connections.
    
    Args:
        host: IP address to bind to
        port: Port number to listen on
        
    Computer Networks Concepts:
        - WebSocket server initialization
        - Async event loop
        - HTTP upgrade to WebSocket
    """
    log("INFO", f"WebSocket Server listening on {host}:{port}")
    
    # Create and start WebSocket server
    async with websockets.serve(
        handle_ws_client,
        host,
        port,
        # Allow connections from any origin (for development)
        # In production, you'd want to restrict this
        origins=None
    ):
        # Keep server running forever
        await asyncio.Future()

def run_ws_server(host: str = HOST, port: int = WS_PORT) -> None:
    """
    Run WebSocket server (blocking call)
    
    This is a wrapper to run the async server from sync code.
    """
    asyncio.run(start_ws_server(host, port))

# =============================================================================
# STANDALONE MODE
# =============================================================================

if __name__ == "__main__":
    from server.shared import log_header
    
    log_header()
    print(f"Running WebSocket Server standalone on {HOST}:{WS_PORT}")
    print("-" * 65)
    run_ws_server()
