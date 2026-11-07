from enum import Enum

class UserTier(Enum):
    FREE = "free"
    PREMIUM = "premium"

class Endpoint(Enum):
    LOGIN = "/api/login"
    FEED = "/api/feed"
    REST = "/*"

TIER_LIMITS = {
    UserTier.FREE: 2,
    UserTier.PREMIUM: 10,
}

ENDPOINT_LIMITS = {
    Endpoint.LOGIN: 2,
    Endpoint.FEED: 4,
    Endpoint.REST: 1
}

def get_limit_for_tier(tier: UserTier) -> int:
    return TIER_LIMITS.get(tier, TIER_LIMITS[UserTier.FREE])

def get_limit_for_endpoints(endpoint: Endpoint) -> int:
    return ENDPOINT_LIMITS.get(endpoint, ENDPOINT_LIMITS[Endpoint.REST])

