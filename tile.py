class Tile:
    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.character = None
        self.neighbors = []
        self.obstructed = False

    def distance_to(self, other):
        return (abs(self.q - other.q) + abs(self.r - other.r) + abs((self.q + self.r) - (other.q + other.r))) // 2

    def is_obstructed(self):
        return self.character is not None or self.obstructed
    
    def reachable_tiles(self, max_distance):
        from collections import deque
        visited = set()
        queue = deque()
        queue.append((self, 0))
        visited.add(self)
        result = set()

        while queue:
            current_tile, dist = queue.popleft()
            if dist > max_distance:
                continue
            result.add((current_tile, dist))
            for neighbor in current_tile.neighbors:
                if neighbor not in visited and neighbor.character is None:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        return result