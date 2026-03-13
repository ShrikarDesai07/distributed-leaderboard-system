import redis

# connect to redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

LEADERBOARD_KEY = "leaderboard"


def update_score(username, score):
    """
    Update leaderboard score
    Lower score = better rank (lap time)
    """
    existing = r.zscore(LEADERBOARD_KEY, username)

    if existing is None or score < float(existing):
        r.zadd(LEADERBOARD_KEY, {username: score})


def get_leaderboard(top_n=10):
    """
    return sorted leaderboard
    """
    board = r.zrange(LEADERBOARD_KEY, 0, top_n - 1, withscores=True)

    leaderboard = []
    rank = 1

    for user, score in board:
        leaderboard.append(f"{rank}. {user} - {score}")
        rank += 1

    return "\n".join(leaderboard)