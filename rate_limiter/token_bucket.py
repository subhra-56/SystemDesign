import time
from base import RateLimiter
from models import Bucket

class TokenBucketRateLimiter(RateLimiter):
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets = {}

    def allow_request(self, user_id: str) -> bool:
        ts = time.time()
        if user_id not in self.buckets:
            self.buckets[user_id] = Bucket(
                tokens = self.capacity,
                last_refill_timestamp = ts   
            )
        bucket = self.buckets[user_id]
        prev_refil = bucket.last_refill_timestamp
        tokens = bucket.tokens

        tokens_to_add = (ts - prev_refil) * self.refill_rate
        tokens = min(self.capacity, tokens + tokens_to_add)
        bucket.tokens = tokens
        bucket.last_refill_timestamp = ts

        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        else:
            return False
        

def main():
    limiter = TokenBucketRateLimiter(capacity = 3, refill_rate = 1.0)

    # alice sends a request so we need to log that
    print("Request 1:", limiter.allow_request("alice"))  # Expect: True
    print("Request 2:", limiter.allow_request("alice"))  # Expect: True
    print("Request 3:", limiter.allow_request("alice"))  # Expect: True
    print("Request 4:", limiter.allow_request("alice"))  # Expect: False (Blocked!)

    time.sleep(2)

    print("Request 5:", limiter.allow_request("alice"))


if __name__ == "__main__":
    main()
