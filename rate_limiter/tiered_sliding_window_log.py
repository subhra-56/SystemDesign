from collections import deque
import time
from base import RateLimiter
from config import UserTier, get_limit_for_tier

class SWLRateLimiter(RateLimiter):
    '''
    Implements tiered sliding window log rate limiter
    '''
    def __init__(self, window_slot: int):
        self.window_slot = window_slot
        self.user_log = {}

    def allow_request(self, user_id: str, tier: UserTier = UserTier.FREE) -> bool:
        capacity = get_limit_for_tier(tier)
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
        if len(g_user_log) < capacity:
            g_user_log.append(req_ts)
            return True
        
        return False

def main():
    limiter = SWLRateLimiter(window_slot = 1)

    # --- Test Case 1: FREE user (limit = 2) ---
    print("Alice (Free) 1:", limiter.allow_request("alice", UserTier.FREE))  # True
    print("Alice (Free) 2:", limiter.allow_request("alice", UserTier.FREE))  # True
    print("Alice (Free) 3:", limiter.allow_request("alice", UserTier.FREE))  # False (Blocked!)
    
    # --- Test Case 2: PREMIUM user (limit = 10) ---
    # Bob can send up to 10 requests in the same 1-second window!
    for i in range(1, 11):
        print(f"Bob (Premium) {i}:", limiter.allow_request("bob", UserTier.PREMIUM))  # All True!
    print("Bob (Premium) 11:", limiter.allow_request("bob", UserTier.PREMIUM))  # False (Blocked!)
    
    # --- Test Case 3: Default / Guest user (no tier passed) ---
    # Automatically falls back to FREE (limit = 2)
    print("Guest 1:", limiter.allow_request("guest_123"))  # True
    print("Guest 2:", limiter.allow_request("guest_123"))  # True
    print("Guest 3:", limiter.allow_request("guest_123"))  # False (Blocked!)

if __name__ == "__main__":
    main()