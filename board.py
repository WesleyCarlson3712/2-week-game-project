import character
import arcade 
import math

WIDTH = 1000
HEIGHT = 675
TILE_RADIUS = 30
GRID_RADIUS = 6
UI_WIDTH = 1/4 * WIDTH
GRID_ORIGIN_X = WIDTH // 2 - UI_WIDTH // 2
GRID_ORIGIN_Y = HEIGHT // 2

# -------------------------
# TILE CLASS
# -------------------------
class Tile:
    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.character = None
        self.neighbors = []

    def distance_to(self, other):
        return (abs(self.q - other.q) + abs(self.r - other.r) + abs((self.q + self.r) - (other.q + other.r))) // 2
# -------------------------
# HEX GRID WORLD
# -------------------------
class HexGrid(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, "Hex Tile World")
        arcade.set_background_color(arcade.color.BABY_BLUE)

        self.tiles = {}

        self.build_grid()
        self.link_neighbors()

        # place one test character
        center_tile = self.tiles[(0, 0)]
        self.player = character.Character("Player", 100, center_tile, 3)

    # -------------------------
    # GRID CREATION
    # -------------------------
    def build_grid(self):
        for q in range(-GRID_RADIUS, GRID_RADIUS + 1):
            for r in range(-GRID_RADIUS, GRID_RADIUS + 1):
                dist = (abs(q) + abs(r) + abs(q + r)) // 2
                if dist <= GRID_RADIUS:
                    self.tiles[(q, r)] = Tile(q, r)

    def draw_grid(self):
        colors = [
            arcade.color.LIGHT_GRAY,
            arcade.color.DARK_GRAY,
            arcade.color.GRAY
            ]       
        for tile in self.tiles.values():
            x, y = self.hex_to_pixel(tile.q, tile.r)
            self.draw_hex(x, y, colors[(tile.q - tile.r) % 3])
            # highlight character tile
            if tile.character:
                arcade.draw_circle_filled(x, y, 10, arcade.color.RED)
    # -------------------------
    # NEIGHBOR LINKING
    # -------------------------
    def link_neighbors(self):
        directions = [
            (1, 0), (-1, 0),
            (0, 1), (0, -1),
            (1, -1), (-1, 1)
        ]

        for (q, r), tile in self.tiles.items():
            for dq, dr in directions:
                neighbor = self.tiles.get((q + dq, r + dr))
                if neighbor:
                    tile.neighbors.append(neighbor)

    # -------------------------
    # HEX → PIXEL CONVERSION
    # ------------------------- 
    def hex_to_pixel(self, q, r):
        # Flat-topped hexes
        x = GRID_ORIGIN_X + TILE_RADIUS * math.sqrt(3) * (q + r / 2)
        y = GRID_ORIGIN_Y + TILE_RADIUS * 1.5 * r
        return x, y

    # -------------------------
    # PIXEL → HEX CONVERSION
    # -------------------------
    def pixel_to_hex(self, x, y):
        # Flat-topped hex math
        px = x - GRID_ORIGIN_X
        py = y - GRID_ORIGIN_Y
        q = (math.sqrt(3)/3 * px - 1/3 * py) / TILE_RADIUS
        r = (2/3 * py) / TILE_RADIUS
        # Cube coordinates
        s = -q - r
        rq = round(q)
        rr = round(r)
        rs = round(s)
        q_diff = abs(rq - q)
        r_diff = abs(rr - r)
        s_diff = abs(rs - s)
        if q_diff > r_diff and q_diff > s_diff:
            rq = -rr - rs
        elif r_diff > s_diff:
            rr = -rq - rs
        else:
            rs = -rq - rr
        return rq, rr

    # -------------------------
    # DRAW HEXAGON
    # -------------------------
    def draw_hex(self, x, y, color):
        points = []
        for i in range(6):
            angle = math.radians(60 * i + 30)  # 30 degree offset for flat-topped
            px = x + TILE_RADIUS * math.cos(angle)
            py = y + TILE_RADIUS * math.sin(angle)
            points.append((px, py))
        arcade.draw_polygon_filled(points, color)
        arcade.draw_polygon_outline(points, arcade.color.BLACK, 1)
        

    # -------------------------
    # RENDER LOOP
    # -------------------------
    def on_draw(self):
        self.clear()
        self.draw_grid()

        panel_x = WIDTH - UI_WIDTH

        arcade.draw_lrbt_rectangle_filled(
            panel_x, WIDTH,
            0, HEIGHT,
            arcade.color.DARK_SLATE_GRAY
        )
        mid_y = self.height // 2

        # top box (tile info)
        arcade.draw_lrbt_rectangle_outline(
            panel_x, WIDTH,
            mid_y, HEIGHT,
            arcade.color.BLACK
        )

        # bottom box (menu)
        arcade.draw_lrbt_rectangle_outline(
            panel_x, WIDTH,
            0, mid_y,
            arcade.color.BLACK
        )




    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            q, r = self.pixel_to_hex(x, y)
            print(f"Clicked on tile: {q}, {r}" if (q, r) in self.tiles else "Clicked outside of grid")
            #print distance between current tile and clicked tile
            print(f"Distance from player: {self.tiles[(q, r)].distance_to(self.player.tile) if (q, r) in self.tiles else 'N/A'}")

            if (q, r) in self.tiles:
                self.player.move(self.tiles[(q, r)])

