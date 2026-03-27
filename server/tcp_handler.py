"""
TCP Socket Server Handler for Distributed Leaderboard System

This module implements the raw TCP socket server for terminal clients.
It demonstrates core Computer Networks concepts:

1. TCP Socket Programming
   - socket(), bind(), listen(), accept()
   - Reliable, connection-oriented communication

2. Multithreading
   - Thread per client model
   - Concurrent connection handling

3. Protocol Design
   - HELLO#hostname - Client identification
   - username#score - Score submission

4. Broadcasting
   - Sending updates to all connected clients
"""

import socket
import threading
from typing import Tuple

from config import HOST, TCP_PORT
from server.shared import (
    register_tcp_client,
    unregister_tcp_client,
    update_tcp_hostname,
    broadcast_leaderboard,
    log,
    get_tcp_client_info
)
from server.redis_db import update_score, get_leaderboard, get_leaderboard_json

# =============================================================================
# CLIENT HANDLER
# =============================================================================

def handle_client(client_socket: socket.socket, addr: Tuple[str, int]) -> None:
    """
    Handle a single TCP client connection
    
    This function runs in a separate thread for each connected client.
    It processes incoming messages and broadcasts leaderboard updates.
    
    Protocol:
        1. Client sends: HELLO#hostname (identification)
        2. Client sends: username#score (score submission)
        3. Server responds: LEADERBOARD\\n<formatted leaderboard>
    
    Args:
        client_socket: The client's socket object
        addr: Tuple of (ip, port)
        
    Computer Networks Concepts:
        - recv(): Blocking call to receive data from socket
        - send(): Send data to client
        - Message parsing: Application layer protocol
    """
    ip, port = addr
    
    # Register client with initial "Unknown" hostname
    register_tcp_client(client_socket, ip, port, "Unknown")
    
    try:
        while True:
            # Receive data from client
            # recv() blocks until data arrives or connection closes
            data = client_socket.recv(1024).decode()
            
            if not data:
                # Empty data means client disconnected
                break
            
            # Handle multiple messages in one packet (edge case)
            messages = data.strip().split('\n')
            
            for message in messages:
                if not message:
                    continue
                    
                # Parse message
                if '#' not in message:
                    continue
                    
                parts = message.split('#', 1)
                if len(parts) != 2:
                    continue
                    
                command, value = parts
                
                # Handle HELLO message (client identification)
                if command.upper() == "HELLO":
                    hostname = value.strip()
                    update_tcp_hostname(client_socket, hostname)
                    
                    # Send current leaderboard to new client
                    leaderboard = get_leaderboard()
                    welcome_msg = f"LEADERBOARD\n{leaderboard}"
                    client_socket.send(welcome_msg.encode())
                    continue
                
                # Handle score submission
                try:
                    username = command.strip()
                    score = float(value.strip())
                except ValueError:
                    # Invalid score format
                    continue
                
                # Get client info for logging
                client_info = get_tcp_client_info(client_socket)
                hostname = client_info["hostname"] if client_info else "Unknown"
                
                # Update score in Redis
                updated = update_score(username, score)
                
                if updated:
                    log("TCP", f"Score from {hostname}: {username} = {score:.3f}s")
                else:
                    log("TCP", f"Score from {hostname}: {username} = {score:.3f}s (not best)")
                
                # Get updated leaderboard and broadcast to ALL clients
                leaderboard_text = get_leaderboard()
                leaderboard_json = get_leaderboard_json()
                broadcast_leaderboard(leaderboard_text, leaderboard_json)
                
    except ConnectionResetError:
        # Client forcefully disconnected
        pass
    except Exception as e:
        log("ERR", f"TCP client error: {e}")
    finally:
        # Clean up: unregister client and close socket
        unregister_tcp_client(client_socket)
        try:
            client_socket.close()
        except:
            pass

# =============================================================================
# TCP SERVER
# =============================================================================

def start_tcp_server(host: str = HOST, port: int = TCP_PORT) -> None:
    """
    Start the TCP socket server
    
    This is the main TCP server loop that:
    1. Creates a TCP socket
    2. Binds to host:port
    3. Listens for incoming connections
    4. Spawns a thread for each client
    
    Args:
        host: IP address to bind to ("0.0.0.0" for all interfaces)
        port: Port number to listen on
        
    Computer Networks Concepts:
        - socket(AF_INET, SOCK_STREAM): Create TCP socket
        - bind(): Associate socket with IP and port
        - listen(): Mark socket as passive (accepting connections)
        - accept(): Block until client connects, return new socket
        - Threading: Handle multiple clients concurrently
    """
    # Create TCP socket
    # AF_INET: IPv4 addressing
    # SOCK_STREAM: TCP (connection-oriented, reliable)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Allow socket reuse (prevents "Address already in use" error)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind socket to address
    server_socket.bind((host, port))
    
    # Start listening for connections
    # Argument is the backlog (max queued connections)
    server_socket.listen(5)
    
    log("INFO", f"TCP Server listening on {host}:{port}")
    
    # Main accept loop
    while True:
        try:
            # accept() blocks until a client connects
            # Returns new socket for this specific client and their address
            client_socket, addr = server_socket.accept()
            
            # Spawn a new thread to handle this client
            # daemon=True means thread will be killed when main program exits
            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, addr),
                daemon=True
            )
            thread.start()
            
        except KeyboardInterrupt:
            log("INFO", "TCP Server shutting down...")
            break
        except Exception as e:
            log("ERR", f"TCP accept error: {e}")
    
    # Cleanup
    server_socket.close()

# =============================================================================
# STANDALONE MODE
# =============================================================================

if __name__ == "__main__":
    # Run TCP server standalone (for testing)
    from server.shared import log_header, log_server_info
    
    log_header()
    print(f"Running TCP Server standalone on {HOST}:{TCP_PORT}")
    print("-" * 65)
    start_tcp_server()
