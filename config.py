"""
Configuration settings for Distributed Leaderboard System

This file centralizes all configuration settings for easy management
and switching between localhost (development) and LAN (demo) modes.
"""

# =============================================================================
# NETWORK SETTINGS
# =============================================================================

# Server host - "0.0.0.0" listens on all interfaces (required for LAN demo)
# Change to "127.0.0.1" for localhost-only testing
HOST = "0.0.0.0"

# TCP Server port - for terminal clients (raw socket programming)
TCP_PORT = 5000

# WebSocket Server port - for browser clients
WS_PORT = 8765

# HTTP Server port - serves static web files
HTTP_PORT = 8080

# =============================================================================
# REDIS SETTINGS
# =============================================================================

REDIS_HOST = "localhost"
REDIS_PORT = 6379
LEADERBOARD_KEY = "leaderboard"

# =============================================================================
# LEADERBOARD SETTINGS
# =============================================================================

# Number of top players to display
TOP_N = 10

# =============================================================================
# LOGGING SETTINGS
# =============================================================================

# Enable detailed logging
DEBUG = True

# Log format with timestamps
LOG_FORMAT = "[{time}] [{type}] {message}"

# =============================================================================
# LAN DEMO CONFIGURATION
# =============================================================================
# When running demo on WiFi hotspot:
# 1. Server creates hotspot (typically 192.168.137.1 on Windows)
# 2. Update CLIENT_HOST below to server's hotspot IP
# 3. Clients connect to this IP

# For clients connecting to the server (used by client.py)
# Change this to server's IP when running on LAN
CLIENT_HOST = "127.0.0.1"  # Change to "192.168.137.1" for LAN demo
CLIENT_TCP_PORT = TCP_PORT
CLIENT_WS_PORT = WS_PORT
