import redis
import json

# Redis client
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def get_cache(key: str):
    """Retrieve data from Redis cache."""
    data = redis_client.get(key)
    json_data = json.loads(data) if data else None
    return json_data

def set_cache(key: str, value: str, expiry: int = 60):
    """Set data in Redis with expiration time (default: 60 sec)."""
    redis_client.setex(key, expiry, value)