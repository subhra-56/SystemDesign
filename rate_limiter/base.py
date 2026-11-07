from abc import ABC, abstractmethod

class RateLimiter(ABC): # abstract base class so that we can have multiple implementations of rate limiters
                        # also object for this can not be created directly
    @abstractmethod # any class inheriting this class must implement this method
    def allow_request(self, user_id: str) -> bool:
        pass