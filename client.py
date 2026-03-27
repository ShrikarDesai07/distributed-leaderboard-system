"""
TCP Client for Distributed Leaderboard System

This is the terminal-based client that connects to the server via TCP socket.
It demonstrates client-side socket programming for Computer Networks.

Features:
- Connects to server via TCP
- Sends hostname on connect (HELLO#hostname)
- Sends lap times (username#score)
- Receives and displays live leaderboard updates

Computer Networks Concepts:
- TCP Client Socket Programming
- Connection establishment
- Bidirectional communication
- Async receive with threading
"""

import socket
import threading
import os
import sys

# Import configuration
try:
    from config import CLIENT_HOST, CLIENT_TCP_PORT
    HOST = CLIENT_HOST
    PORT = CLIENT_TCP_PORT
except ImportError:
    # Fallback for standalone use
    HOST = "127.0.0.1"
    PORT = 5000

# =============================================================================
# RECEIVE THREAD
# =============================================================================

def receive_messages(sock: socket.socket) -> None:
    """
    Background thread to receive leaderboard broadcasts from server
    
    This runs continuously, waiting for server messages.
    When a message arrives, it clears the terminal and displays
    the updated leaderboard.
    
    Args:
        sock: Connected socket to server
        
    Computer Networks Concept:
        This demonstrates non-blocking I/O pattern - while the main
        thread handles user input, this thread handles incoming data.
    """
    while True:
        try:
            # recv() blocks until data arrives
            msg = sock.recv(4096).decode()
            
            if not msg:
                print("\nConnection closed by server.")
                break
            
            # Clear terminal for fresh leaderboard display
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("=" * 50)
            print("        LIVE LEADERBOARD")
            print("=" * 50)
            print()
            print(msg)
            print()
            print("-" * 50)
            print("Enter lap time (or 'quit' to exit): ", end="", flush=True)
            
        except ConnectionResetError:
            print("\nConnection lost.")
            break
        except Exception as e:
            print(f"\nReceive error: {e}")
            break
    
    # Exit program when connection is lost
    os._exit(0)

# =============================================================================
# MAIN CLIENT
# =============================================================================

def start_client() -> None:
    """
    Main client function
    
    1. Gets username from user
    2. Connects to server via TCP
    3. Sends HELLO message with hostname
    4. Starts receive thread
    5. Main loop: get lap times and send to server
    
    Computer Networks Concepts:
        - socket.connect(): Establish TCP connection (3-way handshake)
        - socket.send(): Send data to server
        - Threading for async receive
    """
    # Clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("=" * 50)
    print("    DISTRIBUTED LEADERBOARD - TCP CLIENT")
    print("=" * 50)
    print()
    print(f"Server: {HOST}:{PORT}")
    print()
    
    # Get username
    username = input("Enter your username: ").strip()
    if not username:
        print("Username cannot be empty!")
        return
    
    print()
    print(f"Connecting to server as '{username}'...")
    
    try:
        # Create TCP socket and connect to server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        print("Connected!")
        
    except ConnectionRefusedError:
        print(f"\nError: Could not connect to server at {HOST}:{PORT}")
        print("Make sure the server is running.")
        return
    except Exception as e:
        print(f"\nConnection error: {e}")
        return
    
    # Send HELLO message with computer hostname
    # This allows the server to identify this client
    computer_name = socket.gethostname()
    hello_msg = f"HELLO#{computer_name}"
    client_socket.send(hello_msg.encode())
    
    print(f"Identified as: {computer_name}")
    print()
    print("Waiting for leaderboard...")
    print()
    
    # Start background thread to receive server messages
    receive_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket,),
        daemon=True
    )
    receive_thread.start()
    
    # Main input loop
    try:
        while True:
            # Get lap time from user
            lap_time_str = input()
            
            # Check for quit command
            if lap_time_str.lower() in ['quit', 'exit', 'q']:
                print("Disconnecting...")
                break
            
            # Validate lap time
            try:
                lap_time = float(lap_time_str)
                if lap_time <= 0:
                    print("Lap time must be positive!")
                    continue
            except ValueError:
                print("Invalid lap time! Enter a number (e.g., 9.5)")
                continue
            
            # Send score to server: username#score
            message = f"{username}#{lap_time}"
            client_socket.send(message.encode())
            
    except KeyboardInterrupt:
        print("\nDisconnecting...")
    finally:
        client_socket.close()

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Allow command-line override of server address
    if len(sys.argv) >= 2:
        HOST = sys.argv[1]
    if len(sys.argv) >= 3:
        PORT = int(sys.argv[2])
    
    start_client()
