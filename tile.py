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
        queue = deque()
        queue.append((self, 0))
        shortest_distances = {self: 0}

        while queue:
            current_tile, dist = queue.popleft()
            if dist >= max_distance:
                continue
            for neighbor in current_tile.neighbors:
                if neighbor.character is None:
                    new_dist = dist + 1
                    if new_dist <= max_distance and (neighbor not in shortest_distances or new_dist < shortest_distances[neighbor]):
                        shortest_distances[neighbor] = new_dist
                        queue.append((neighbor, new_dist))
        # Exclude the starting tile (self) from the result
        return [(tile, distance) for tile, distance in shortest_distances.items() if tile is not self]