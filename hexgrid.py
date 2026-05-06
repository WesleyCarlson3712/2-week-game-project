import arcade 
import gamemanager
import math
import tile

WIDTH = 1000
HEIGHT = 675
TILE_RADIUS = 30
GRID_RADIUS = 6
UI_WIDTH = WIDTH // 4
UI_HEADER_HEIGHT = HEIGHT // 12
GRID_ORIGIN_X = WIDTH // 2 - UI_WIDTH // 2
GRID_ORIGIN_Y = HEIGHT // 2

# -------------------------
# HEX GRID WORLD
# -------------------------
class HexGrid(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, "Battle Game")
        self.color_palette = 1

        self.backgrounds = [arcade.color.LICORICE, arcade.color.BABY_BLUE]
        arcade.set_background_color(self.backgrounds[self.color_palette])

        self.tiles = {}
        self.hex_colors = [
            [arcade.color.LIGHT_GRAY, arcade.color.DARK_GRAY, arcade.color.GRAY],
            [arcade.color.LIGHT_BLUE, arcade.color.BRIGHT_TURQUOISE, arcade.color.DIAMOND]
            ]   

        self.build_grid()
        self.link_neighbors()
        self.game_manager = gamemanager.GameManager(self)
        
    # -------------------------
    # GRID CREATION
    # -------------------------
    def build_grid(self):
        for q in range(-GRID_RADIUS, GRID_RADIUS + 1):
            for r in range(-GRID_RADIUS, GRID_RADIUS + 1):
                dist = (abs(q) + abs(r) + abs(q + r)) // 2
                if dist <= GRID_RADIUS:
                    self.tiles[(q, r)] = tile.Tile(q, r)

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
    # DRAWING
    # -------------------------
    def draw_grid(self): 
        for tile in self.tiles.values():
            x, y = self.hex_to_pixel(tile.q, tile.r)
            color = self.hex_colors[self.color_palette][(tile.q - tile.r) % 3]

            self.draw_hex(x, y, TILE_RADIUS, color)
                    
            # highlight character tile
            if tile.character:
                arcade.draw_circle_filled(x, y, 10, arcade.color.GREEN if tile.character == self.game_manager.active_character else arcade.color.RED)

        if self.game_manager.state_stack[-1] == "select tile for move":
            for tile in self.game_manager.active_character.tile.neighbors:
                x, y = self.hex_to_pixel(tile.q, tile.r)
                if not tile.is_obstructed():
                    self.draw_hex(x, y, TILE_RADIUS - 1, outline_color = arcade.color.GREEN_YELLOW, outline_width = 4)

    def draw_ui(self, panel_x, mid_y):
        arcade.draw_lrbt_rectangle_filled(
            panel_x, WIDTH,
            0, HEIGHT,
            arcade.color.INDEPENDENCE
        )
        # top box header
        arcade.draw_lrbt_rectangle_filled(
            panel_x, WIDTH,
            HEIGHT - UI_HEADER_HEIGHT, HEIGHT,
            arcade.color.JET
        )
        arcade.draw_lrbt_rectangle_outline(
            panel_x, WIDTH,
            HEIGHT - UI_HEADER_HEIGHT, HEIGHT,
            arcade.color.BLACK
        )
        #bottom box header
        arcade.draw_lrbt_rectangle_filled(
            panel_x, WIDTH,
            mid_y - UI_HEADER_HEIGHT, mid_y,
            arcade.color.JET
        )
        arcade.draw_lrbt_rectangle_outline(
            panel_x, WIDTH,
            mid_y - UI_HEADER_HEIGHT, mid_y,
            arcade.color.BLACK
        )
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

    def draw_hex(self, x, y, radius, fill_color = None, outline_color = arcade.color.BLACK, outline_width = 1):
        points = []
        for i in range(6):
            angle = math.radians(60 * i + 30)  # 30 degree offset for flat-topped
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))
        if fill_color is not None:
            arcade.draw_polygon_filled(points, fill_color)
        arcade.draw_polygon_outline(points, outline_color, outline_width)
        
    # -------------------------
    # RENDER LOOP
    # -------------------------
    def on_draw(self):
        panel_x = WIDTH - UI_WIDTH
        mid_y = HEIGHT // 2

        self.clear()
        self.draw_grid()
        self.draw_ui(panel_x, mid_y)
        if self.game_manager.menu_stack:
            menu = self.game_manager.menu_stack[-1]
            # draw from panel_x, mid_y, to the bottom right corner of the screen
            menu.draw(panel_x, mid_y, WIDTH, 0, UI_HEADER_HEIGHT )

    def on_key_press(self, key, modifiers):
        self.game_manager.on_key_press(key)

    def on_mouse_press(self, x, y, button, modifiers):
        self.game_manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        self.game_manager.on_mouse_motion(x, y, dx, dy)