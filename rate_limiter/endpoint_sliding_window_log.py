import time
from base import RateLimiter
from config import Endpoint, get_limit_for_endpoints
from collections import deque

class EndpointSWLRateLimiter(RateLimiter):
    '''
    Implements Endpoint SWL Rate Limiter
    '''
    def __init__(self, window_slot: int):
        self.window_slot = window_slot
        self.user_log = {}

    def allow_request(self, user_id: str, endpoint: Endpoint = Endpoint.REST) -> bool:
        window_slot = self.window_slot
        user_log =  self.user_log
        req_ts =  time.time()

        if user_id not in user_log:
            user_log[user_id] = {}
        
        if endpoint not in user_log[user_id]:
            user_log[user_id][endpoint] = deque()
        
        cutoff_ts = req_ts - window_slot
        user_endpoint_list = user_log[user_id][endpoint]
        endpoint_limit = get_limit_for_endpoints(endpoint)

        while(len(user_endpoint_list) > 0 and cutoff_ts > user_endpoint_list[0]):
            user_endpoint_list.popleft()

        if(len(user_endpoint_list) < endpoint_limit):
            user_endpoint_list.append(req_ts)
            return True

        return False


def main():
    limiter = EndpointSWLRateLimiter(window_slot=1)

    # 1. Test Endpoint.LOGIN (limit = 2)
    print("Login 1:", limiter.allow_request("alice", Endpoint.LOGIN))  # Expect: True
    print("Login 2:", limiter.allow_request("alice", Endpoint.LOGIN))  # Expect: True
    print("Login 3:", limiter.allow_request("alice", Endpoint.LOGIN))  # Expect: False (Blocked!)

    # 2. Test Endpoint.FEED (limit = 4) - unaffected by login limits!
    print("Feed 1:", limiter.allow_request("alice", Endpoint.FEED))    # Expect: True
    print("Feed 2:", limiter.allow_request("alice", Endpoint.FEED))    # Expect: True
    print("Feed 3:", limiter.allow_request("alice", Endpoint.FEED))    # Expect: True
    print("Feed 4:", limiter.allow_request("alice", Endpoint.FEED))    # Expect: True
    print("Feed 5:", limiter.allow_request("alice", Endpoint.FEED))    # Expect: False (Blocked!)

    # 3. Test default Endpoint.REST (limit = 1)
    print("Rest 1:", limiter.allow_request("alice"))                   # Expect: True
    print("Rest 2:", limiter.allow_request("alice"))                   # Expect: False (Blocked!)

    # 4. Wait for window to slide
    time.sleep(1)
    print("Login 4 (after 1s):", limiter.allow_request("alice", Endpoint.LOGIN))  # Expect: True


if __name__ == "__main__":
    main()