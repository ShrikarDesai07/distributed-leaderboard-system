"""
Shared State and Utilities for Distributed Leaderboard System

This module contains:
- Shared client registries (TCP and WebSocket)
- Thread-safe locks for synchronization
- Unified broadcast function
- Logging utilities with timestamps and hostnames

Computer Networks Concepts Demonstrated:
- Thread synchronization (mutex/lock)
- Shared state management
- Broadcasting to multiple clients
"""

import threading
import json
from datetime import datetime
from typing import Dict, Any, Optional

# =============================================================================
# CLIENT REGISTRIES
# =============================================================================

# TCP clients: {socket: {"hostname": "LAPTOP-X", "ip": "192.168.1.2", "port": 54321, "username": None}}
tcp_clients: Dict[Any, Dict[str, Any]] = {}

# WebSocket clients: {websocket: {"hostname": "BROWSER-X", "ip": "192.168.1.3", "username": None}}
ws_clients: Dict[Any, Dict[str, Any]] = {}

# Thread lock for safe access to client registries
clients_lock = threading.Lock()

# =============================================================================
# LOGGING UTILITIES
# =============================================================================

def get_timestamp() -> str:
    """Get current timestamp in HH:MM:SS format"""
    return datetime.now().strftime("%H:%M:%S")

def get_full_timestamp() -> str:
    """Get full timestamp in YYYY-MM-DD HH:MM:SS format"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ANSI Color Codes for terminal logging
COLORS = {
    "TCP": "\033[96m",   # Cyan
    "WS": "\033[95m",    # Magenta
    "-->": "\033[93m",   # Yellow (Broadcasts)
    "INFO": "\033[92m",  # Green
    "ERR": "\033[91m",   # Red
    "RESET": "\033[0m"   # Reset formatting
}

def log(log_type: str, message: str) -> None:
    """
    Log a message with timestamp and type

    Args:
        log_type: Type of log (TCP, WS, -->, INFO, ERR)
        message: Log message
    """
    timestamp = get_timestamp()
    
    # Check if the log type has a specific color mapping, otherwise default to no color
    color = COLORS.get(log_type.strip(), "")
    reset = COLORS["RESET"] if color else ""
    
    print(f"{color}[{timestamp}] [{log_type:4}] {message}{reset}")

def log_header() -> None:
    """Print server startup header"""
    c = COLORS["INFO"]
    r = COLORS["RESET"]
    print(f"{c}" + "=" * 65)
    print(f"{c}           DISTRIBUTED LEADERBOARD SERVER")
    print(f"{c}" + "=" * 65 + f"{r}")

def log_server_info(tcp_port: int, ws_port: int, http_port: int) -> None:       
    """Print server connection information"""
    from config import HOST, REDIS_HOST, REDIS_PORT

    c = COLORS["INFO"]
    r = COLORS["RESET"]
    print(f"{c}[{get_timestamp()}] Server started{r}")
    print(f"[{get_timestamp()}] {COLORS['TCP']}TCP Server:{r}       {HOST}:{tcp_port}")
    print(f"[{get_timestamp()}] {COLORS['WS']}WebSocket Server:{r} {HOST}:{ws_port}")
    print(f"[{get_timestamp()}] HTTP Server:      {HOST}:{http_port}")
    print(f"[{get_timestamp()}] Redis:            {REDIS_HOST}:{REDIS_PORT}")   
    print(f"{c}" + "-" * 65 + f"{r}")
    print(f"{c}[{get_timestamp()}] Waiting for connections...{r}")
    print(f"{c}" + "-" * 65 + f"{r}")

# =============================================================================
# CLIENT MANAGEMENT
# =============================================================================

def register_tcp_client(socket: Any, ip: str, port: int, hostname: str = "Unknown") -> None:
    """
    Register a new TCP client
    
    Args:
        socket: Client socket object
        ip: Client IP address
        port: Client port
        hostname: Client hostname (sent by client on connect)
    """
    with clients_lock:
        tcp_clients[socket] = {
            "hostname": hostname,
            "ip": ip,
            "port": port,
            "username": None
        }
    log("TCP", f"Connected: {hostname} ({ip}:{port})")

def register_ws_client(websocket: Any, ip: str, hostname: str = "Browser") -> None:
    """
    Register a new WebSocket client
    
    Args:
        websocket: WebSocket connection object
        ip: Client IP address
        hostname: Client hostname (sent by client on connect)
    """
    with clients_lock:
        ws_clients[websocket] = {
            "hostname": hostname,
            "ip": ip,
            "username": None
        }
    log("WS", f"Connected: {hostname} ({ip})")

def update_tcp_hostname(socket: Any, hostname: str) -> None:
    """Update hostname for a TCP client after HELLO message"""
    with clients_lock:
        if socket in tcp_clients:
            old_hostname = tcp_clients[socket]["hostname"]
            tcp_clients[socket]["hostname"] = hostname
            ip = tcp_clients[socket]["ip"]
            port = tcp_clients[socket]["port"]
    log("TCP", f"Identified: {hostname} ({ip}:{port})")

def update_ws_hostname(websocket: Any, hostname: str) -> None:
    """Update hostname for a WebSocket client after hello message"""
    with clients_lock:
        if websocket in ws_clients:
            ws_clients[websocket]["hostname"] = hostname
            ip = ws_clients[websocket]["ip"]
    log("WS", f"Identified: {hostname} ({ip})")

def unregister_tcp_client(socket: Any) -> None:
    """Remove a TCP client from registry"""
    with clients_lock:
        if socket in tcp_clients:
            client = tcp_clients[socket]
            hostname = client["hostname"]
            ip = client["ip"]
            port = client["port"]
            del tcp_clients[socket]
            log("TCP", f"Disconnected: {hostname} ({ip}:{port})")

def unregister_ws_client(websocket: Any) -> None:
    """Remove a WebSocket client from registry"""
    with clients_lock:
        if websocket in ws_clients:
            client = ws_clients[websocket]
            hostname = client["hostname"]
            ip = client["ip"]
            del ws_clients[websocket]
            log("WS", f"Disconnected: {hostname} ({ip})")

def get_client_count() -> tuple:
    """
    Get count of connected clients
    
    Returns:
        Tuple of (tcp_count, ws_count, total_count)
    """
    with clients_lock:
        tcp_count = len(tcp_clients)
        ws_count = len(ws_clients)
    return tcp_count, ws_count, tcp_count + ws_count

def get_tcp_client_info(socket: Any) -> Optional[Dict[str, Any]]:
    """Get info for a TCP client"""
    with clients_lock:
        return tcp_clients.get(socket)

# =============================================================================
# BROADCASTING
# =============================================================================

def broadcast_to_tcp(message: str) -> int:
    """
    Broadcast message to all TCP clients
    
    Args:
        message: String message to send
        
    Returns:
        Number of clients successfully sent to
    """
    dead_clients = []
    sent_count = 0
    
    # Get snapshot of clients
    with clients_lock:
        clients_snapshot = list(tcp_clients.keys())
    
    # Send to each client (outside lock to avoid blocking)
    for client_socket in clients_snapshot:
        try:
            client_socket.send(message.encode())
            sent_count += 1
        except:
            dead_clients.append(client_socket)
    
    # Clean up dead clients
    if dead_clients:
        with clients_lock:
            for dc in dead_clients:
                if dc in tcp_clients:
                    client = tcp_clients[dc]
                    log("TCP", f"Connection lost: {client['hostname']} ({client['ip']}:{client['port']})")
                    del tcp_clients[dc]
    
    return sent_count

async def broadcast_to_ws(message: str) -> int:
    """
    Broadcast message to all WebSocket clients
    
    Args:
        message: String message to send (JSON)
        
    Returns:
        Number of clients successfully sent to
    """
    import asyncio
    
    dead_clients = []
    sent_count = 0
    
    # Get snapshot of clients
    with clients_lock:
        clients_snapshot = list(ws_clients.keys())
    
    # Send to each client
    for ws in clients_snapshot:
        try:
            await ws.send(message)
            sent_count += 1
        except:
            dead_clients.append(ws)
    
    # Clean up dead clients
    if dead_clients:
        with clients_lock:
            for dc in dead_clients:
                if dc in ws_clients:
                    client = ws_clients[dc]
                    log("WS", f"Connection lost: {client['hostname']} ({client['ip']})")
                    del ws_clients[dc]
    
    return sent_count

def broadcast_leaderboard(leaderboard_text: str, leaderboard_json: list) -> None:
    """
    Broadcast leaderboard update to ALL connected clients (TCP and WebSocket)
    
    This is the main broadcast function that sends updates to both
    terminal clients (TCP) and browser clients (WebSocket).
    
    Args:
        leaderboard_text: Formatted string for TCP clients
        leaderboard_json: List of dicts for WebSocket clients
        
    Computer Networks Concept:
        This demonstrates broadcasting - sending the same data to multiple
        connected clients simultaneously. It's similar to multicast but
        implemented at the application layer.
    """
    import asyncio
    
    tcp_count, ws_count, total = get_client_count()
    
    # Broadcast to TCP clients (synchronous)
    tcp_message = "LEADERBOARD\n" + leaderboard_text
    tcp_sent = broadcast_to_tcp(tcp_message)
    
    # Broadcast to WebSocket clients (needs async handling)
    ws_message = json.dumps({
        "type": "leaderboard",
        "data": leaderboard_json
    })
    
    # Schedule WebSocket broadcast in the event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast_to_ws(ws_message))
        else:
            loop.run_until_complete(broadcast_to_ws(ws_message))
    except RuntimeError:
        # No event loop running, create one for this broadcast
        asyncio.run(broadcast_to_ws(ws_message))
    
    log("-->", f"Broadcasting to {total} clients (TCP: {tcp_count}, WS: {ws_count})")
