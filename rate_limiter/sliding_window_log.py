from collections import deque
import time
from base import RateLimiter

class SWLRateLimiter(RateLimiter):
    '''
    Implements sliding window log rate limiter
    '''
    def __init__(self, capacity: int, window_slot: int):
        self.capacity = capacity
        self.window_slot = window_slot # in seconds
        self.user_log = {}

        self.validate()

    def validate(self):
        if self.capacity <= 1:
            raise ValueError("Capacity must be atleast 1")
        if self.window_slot <= 0:
            raise ValueError("Window slot can not be negative")

    def allow_request(self, user_id: str) -> bool:
        req_ts = time.time()
        user_log = self.user_log

        # first time req
        if user_id not in user_log:
            user_log[user_id] = deque()
        
        # pop out older ts
        cutoff_ts = req_ts - self.window_slot
        g_user_log = user_log[user_id]
        while(len(g_user_log) > 0 and g_user_log[0] < cutoff_ts):
            g_user_log.popleft()

        # check for size and append
        if len(g_user_log) < self.capacity:
            g_user_log.append(req_ts)
            return True
        
        return False


def main():
    limiter = SWLRateLimiter(capacity = 2, window_slot = 1)

    # alice sends requests
    print("Request 1:", limiter.allow_request("alice"))  # Expect: True
    print("Request 2:", limiter.allow_request("alice"))  # Expect: True
    print("Request 3:", limiter.allow_request("alice"))  # Expect: False (Blocked!)

    time.sleep(1)
    print("Request 4:", limiter.allow_request("alice"))  # Expect: True



if __name__ == "__main__":
    main()