"""
Distributed Leaderboard System - Main Entry Point

This is the unified server that runs all components:
1. TCP Server (port 5000) - For terminal clients
2. WebSocket Server (port 8765) - For browser clients
3. HTTP Server (port 8080) - Serves static web files

Computer Networks Concepts Demonstrated:
- Multi-protocol server architecture
- Concurrent server handling with threading
- TCP socket programming
- WebSocket protocol
- HTTP static file serving

Usage:
    python main.py
    
Then:
    - Terminal clients: python client.py
    - Browser clients: http://localhost:8080
"""

import threading
import asyncio
import http.server
import socketserver
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import HOST, TCP_PORT, WS_PORT, HTTP_PORT
from server.shared import log_header, log_server_info, log
from server.redis_db import test_connection
from server.tcp_handler import start_tcp_server

# =============================================================================
# HTTP STATIC FILE SERVER
# =============================================================================

class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """
    HTTP handler that serves static files from web/ directory
    with minimal logging
    """
    
    def __init__(self, *args, **kwargs):
        # Serve files from web/ directory
        super().__init__(*args, directory="web", **kwargs)
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging to reduce noise"""
        pass
    
    def do_GET(self):
        """Handle GET requests with proper MIME types"""
        # Log only HTML page requests
        if self.path == "/" or self.path.endswith(".html"):
            log("HTTP", f"Serving: {self.path}")
        super().do_GET()

def start_http_server(host: str = HOST, port: int = HTTP_PORT) -> None:
    """
    Start HTTP server for static files
    
    This serves the web interface (HTML, CSS, JS) for browser clients.
    """
    # Check if web directory exists
    if not os.path.exists("web"):
        log("ERR", "web/ directory not found!")
        return
    
    try:
        with socketserver.TCPServer((host, port), QuietHTTPHandler) as httpd:
            log("INFO", f"HTTP Server listening on {host}:{port}")
            httpd.serve_forever()
    except Exception as e:
        log("ERR", f"HTTP Server error: {e}")

# =============================================================================
# WEBSOCKET SERVER (ASYNC)
# =============================================================================

def start_ws_server_thread(host: str, port: int) -> None:
    """
    Run WebSocket server in its own thread with its own event loop
    """
    import websockets
    from server.ws_handler import handle_ws_client
    
    async def ws_main():
        log("INFO", f"WebSocket Server listening on {host}:{port}")
        async with websockets.serve(handle_ws_client, host, port, origins=None):
            await asyncio.Future()
    
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(ws_main())
    except Exception as e:
        log("ERR", f"WebSocket Server error: {e}")

# =============================================================================
# MAIN SERVER
# =============================================================================

def main():
    """
    Main function - starts all servers
    
    Architecture:
        Main Thread: TCP Server (blocking accept loop)
        Thread 1: WebSocket Server (async event loop)
        Thread 2: HTTP Server (static file serving)
    """
    # Print header
    log_header()
    
    # Test Redis connection
    print("\033[94m[INFO] Testing Redis connection...\033[0m")
    if not test_connection():
        print("\033[91m[ERROR] Could not connect to Redis!\033[0m")
        print("\033[91m[ERROR] Make sure Redis server is running (redis-server)\033[0m")
        sys.exit(1)
    print("\033[92m[INFO] Redis connection OK\033[0m")
    print()
    
    # Print server info
    log_server_info(TCP_PORT, WS_PORT, HTTP_PORT)
    
    # Start HTTP server in separate thread
    http_thread = threading.Thread(
        target=start_http_server,
        args=(HOST, HTTP_PORT),
        daemon=True
    )
    http_thread.start()
    
    # Start WebSocket server in separate thread
    ws_thread = threading.Thread(
        target=start_ws_server_thread,
        args=(HOST, WS_PORT),
        daemon=True
    )
    ws_thread.start()
    
    # Give other servers time to start
    import time
    time.sleep(0.5)
    
    # Start TCP server in main thread (blocking)
    # This keeps the main thread alive
    try:
        start_tcp_server(HOST, TCP_PORT)
    except KeyboardInterrupt:
        print()
        log("INFO", "Shutting down servers...")
        print("\033[91m\n" + "=" * 65)
        print("              SERVER STOPPED")
        print("=" * 65 + "\033[0m")

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
