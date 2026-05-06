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