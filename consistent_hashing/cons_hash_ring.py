import bisect
import hashlib

def _hash(key: str) -> int:
    hex_digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    return int(hex_digest, 16)

class ConsistentHashRing:
    '''
    Implements consistent hashing
    '''
    def __init__(self, servers: list[str] = None, virtual_nodes: int = 3):
        self.servers = []
        self.virtual_nodes = virtual_nodes

        self.hash_ring = []
        self.server_map = {} # map hash to server

        if servers:
            for s in servers:
                self.add_server(s)

    def add_server(self, server_id: str):
        if server_id in self.servers:
            raise ValueError(f"{server_id} is already present")

        self.servers.append(server_id)

        for i in range(self.virtual_nodes):
            vnode_hash = _hash(f"{server_id}#{i}")
            self.server_map[vnode_hash] = server_id
            idx = bisect.bisect_left(self.hash_ring, vnode_hash)
            self.hash_ring.insert(idx, vnode_hash)
            

    def remove_server(self, server_id: str):
        if server_id not in self.servers:
            raise KeyError(f"Server '{server_id}' not found on the ring")
        self.servers.remove(server_id)

        for k, v in list(self.server_map.items()):
            if v == server_id:
                del self.server_map[k]
                idx = bisect.bisect_left(self.hash_ring, k)
                del self.hash_ring[idx]

    def get_server(self, key: str) -> str:
        if not self.hash_ring:
            raise ValueError("No servers available")
        key_hash = _hash(key)
        idx = bisect.bisect_right(self.hash_ring, key_hash)
        if idx == len(self.hash_ring):
            idx = 0
        vnode_hash = self.hash_ring[idx]
        return self.server_map[vnode_hash]

            
def main():
    print("==================================================")
    print("TEST 1: Initial Server Mapping & Key Routing")
    print("==================================================")
    ring = ConsistentHashRing(servers=["server_A", "server_B", "server_C"], virtual_nodes=3)

    test_keys = ["user_101", "user_204", "order_550", "cart_999", "payment_12", "session_88", "profile_42"]
    for key in test_keys:
        print(f"Key '{key}' -> {ring.get_server(key)}")

    print("\n==================================================")
    print("TEST 2: Adding a New Server (server_D) - Scale Out")
    print("==================================================")
    ring.add_server("server_D")
    print("Added server_D! Updated routing (only affected keys move):")
    for key in test_keys:
        print(f"Key '{key}' -> {ring.get_server(key)}")

    print("\n==================================================")
    print("TEST 3: Removing a Server (server_B) - Failover")
    print("==================================================")
    ring.remove_server("server_B")
    print("Removed server_B! Keys re-routed to remaining servers:")
    for key in test_keys:
        print(f"Key '{key}' -> {ring.get_server(key)}")

    print("\n==================================================")
    print("TEST 4: Edge Case - Duplicate Server Addition")
    print("==================================================")
    try:
        ring.add_server("server_A")
    except ValueError as e:
        print(f"Caught expected error: {e}")

    print("\n==================================================")
    print("TEST 5: Edge Case - Removing Non-Existent Server")
    print("==================================================")
    try:
        ring.remove_server("server_UNKNOWN")
    except KeyError as e:
        print(f"Caught expected error: {e}")

    print("\n==================================================")
    print("TEST 6: Edge Case - Querying an Empty Ring")
    print("==================================================")
    empty_ring = ConsistentHashRing()
    try:
        empty_ring.get_server("any_key")
    except ValueError as e:
        print(f"Caught expected error: {e}")


if __name__ == "__main__":
    main()