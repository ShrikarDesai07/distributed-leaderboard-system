"""
Redis Database Operations for Distributed Leaderboard System

This module handles all Redis operations for the leaderboard:
- Storing player scores using Sorted Sets
- Retrieving top players with rankings
- Automatic ranking (lower score = better rank for lap times)

Computer Networks Concepts Demonstrated:
- Database integration with network application
- Atomic operations for concurrent access
- Efficient data structures for rankings

Redis Commands Used:
- ZADD: Add/update player score
- ZSCORE: Get player's current score
- ZRANGE: Get ranked list of players
"""

import redis
from typing import List, Tuple, Dict, Any, Optional
from config import REDIS_HOST, REDIS_PORT, LEADERBOARD_KEY, TOP_N

# =============================================================================
# REDIS CONNECTION
# =============================================================================

# Connect to Redis server
# decode_responses=True returns strings instead of bytes
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def test_connection() -> bool:
    """Test if Redis connection is working"""
    try:
        r.ping()
        return True
    except redis.ConnectionError:
        return False

# =============================================================================
# SCORE OPERATIONS
# =============================================================================

def update_score(username: str, score: float) -> bool:
    """
    Update a player's score on the leaderboard
    
    For lap times, lower is better. Only updates if:
    - Player doesn't exist yet, OR
    - New score is better (lower) than existing score
    
    Args:
        username: Player's username
        score: Lap time in seconds
        
    Returns:
        True if score was updated, False if existing score was better
        
    Redis Command:
        ZADD leaderboard score username
        
    Computer Networks Concept:
        This uses Redis Sorted Sets which provide atomic operations,
        preventing race conditions when multiple clients update simultaneously.
    """
    # Get existing score
    existing = r.zscore(LEADERBOARD_KEY, username)
    
    # Update only if new score is better (lower) or player is new
    if existing is None or score < float(existing):
        r.zadd(LEADERBOARD_KEY, {username: score})
        return True
    
    return False

def get_player_score(username: str) -> Optional[float]:
    """
    Get a specific player's best score
    
    Args:
        username: Player's username
        
    Returns:
        Player's best score, or None if not found
    """
    return r.zscore(LEADERBOARD_KEY, username)

def get_player_rank(username: str) -> Optional[int]:
    """
    Get a player's rank on the leaderboard
    
    Args:
        username: Player's username
        
    Returns:
        Player's rank (1-indexed), or None if not found
    """
    rank = r.zrank(LEADERBOARD_KEY, username)
    return rank + 1 if rank is not None else None

# =============================================================================
# LEADERBOARD RETRIEVAL
# =============================================================================

def get_leaderboard(top_n: int = TOP_N) -> str:
    """
    Get formatted leaderboard string (for TCP clients)
    
    Args:
        top_n: Number of top players to retrieve
        
    Returns:
        Formatted string with rankings
        
    Redis Command:
        ZRANGE leaderboard 0 (n-1) WITHSCORES
    """
    # Get top N players with scores (sorted by score ascending)
    board = r.zrange(LEADERBOARD_KEY, 0, top_n - 1, withscores=True)
    
    if not board:
        return "--- Leaderboard ---\nNo scores yet!\n-------------------"
    
    # Format as string
    lines = ["--- Leaderboard ---"]
    for rank, (username, score) in enumerate(board, start=1):
        # Format score to 3 decimal places
        lines.append(f"{rank}. {username} - {score:.3f}s")
    lines.append("-------------------")
    
    return "\n".join(lines)

def get_leaderboard_json(top_n: int = TOP_N) -> List[Dict[str, Any]]:
    """
    Get leaderboard as JSON-serializable list (for WebSocket clients)
    
    Args:
        top_n: Number of top players to retrieve
        
    Returns:
        List of dicts with rank, username, and score
    """
    # Get top N players with scores
    board = r.zrange(LEADERBOARD_KEY, 0, top_n - 1, withscores=True)
    
    result = []
    for rank, (username, score) in enumerate(board, start=1):
        result.append({
            "rank": rank,
            "username": username,
            "score": round(score, 3)
        })
    
    return result

def get_full_leaderboard() -> List[Tuple[str, float]]:
    """
    Get complete leaderboard with all players
    
    Returns:
        List of (username, score) tuples
    """
    return r.zrange(LEADERBOARD_KEY, 0, -1, withscores=True)

# =============================================================================
# ADMIN OPERATIONS
# =============================================================================

def clear_leaderboard() -> int:
    """
    Clear all scores from leaderboard
    
    Returns:
        Number of players removed
    """
    count = r.zcard(LEADERBOARD_KEY)
    r.delete(LEADERBOARD_KEY)
    return count

def remove_player(username: str) -> bool:
    """
    Remove a player from the leaderboard
    
    Args:
        username: Player to remove
        
    Returns:
        True if player was removed, False if not found
    """
    return r.zrem(LEADERBOARD_KEY, username) > 0

def get_player_count() -> int:
    """
    Get total number of players on leaderboard
    
    Returns:
        Number of players
    """
    return r.zcard(LEADERBOARD_KEY)
