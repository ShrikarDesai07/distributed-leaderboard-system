"""
Server package for Distributed Leaderboard System

This package contains:
- shared.py: Shared state and broadcast logic
- tcp_handler.py: TCP socket server for terminal clients
- ws_handler.py: WebSocket server for browser clients
- redis_db.py: Redis database operations
"""

# Note: Imports are done directly in the modules that need them
# to avoid circular import issues
