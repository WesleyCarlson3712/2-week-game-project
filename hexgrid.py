import arcade 
import game_manager
import math
import tile
import menu

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

        self.tiles = {}
        self.info_box = []
        self.build_grid()
        self.link_neighbors()
        self.color_palette = [(0,0,0),(0,0,0),(0,0,0)]
        self.game_manager = game_manager.GameManager(self)
        
    def update_colors(self, tile_colors, background_color):
        arcade.set_background_color(background_color)
        self.color_palette = tile_colors

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
            color = self.color_palette[(tile.q - tile.r) % 3]

            self.draw_hex(x, y, TILE_RADIUS, color)
                    
            # highlight character tile
            if tile.character:
                arcade.draw_circle_filled(x, y, 16, arcade.color.BLUE if tile.character.owner.name == "Player" else arcade.color.RED)
                if tile.character == self.game_manager.active_character:
                    arcade.draw_circle_outline(x, y, 16, arcade.color.GREEN)
        if self.game_manager.state_stack:
            if self.game_manager.state_stack[-1] == "select tile for move":
                distance_colors = [arcade.color.YELLOW_GREEN, arcade.color.YELLOW]

                for (tile, distance) in self.game_manager.active_character.tile.reachable_tiles(self.game_manager.active_character.movement_range - self.game_manager.moves_taken):
                    x, y = self.hex_to_pixel(tile.q, tile.r)
                    if distance == 0:
                        continue
                    self.draw_hex(x, y, TILE_RADIUS - 4, outline_color = distance_colors[min(distance - 1, len(distance_colors) - 1)], outline_width = 4)

            if self.game_manager.state_stack[-1] == "choose attack target":
                for (q, r), tile in self.tiles.items():
                    if self.game_manager.active_character.tile.distance_to(tile) <= self.game_manager.pending_attack.range:
                        x, y = self.hex_to_pixel(q, r)
                        if tile.character and tile.character.owner != self.game_manager.active_character.owner:
                            self.draw_hex(x, y, TILE_RADIUS - 1, outline_color = arcade.color.RED, outline_width = 4)
                
    def draw_ui(self, panel_x, mid_y):
        horaizontal_padding = (WIDTH - panel_x) / 20
        vertical_padding = (HEIGHT - mid_y) / 40

        self.info_box = [panel_x + horaizontal_padding, (HEIGHT - UI_HEADER_HEIGHT) - vertical_padding, WIDTH - horaizontal_padding, mid_y + vertical_padding]

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
        #info box
        arcade.draw_lrbt_rectangle_filled(
            self.info_box[0], self.info_box[2],
            self.info_box[3], self.info_box[1],
            arcade.color.JET
        )
        arcade.draw_lrbt_rectangle_outline(
            self.info_box[0], self.info_box[2],
            self.info_box[3], self.info_box[1],
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

    def draw_info_text(self, text, x1, y1, x2, y2, header_height):
        # header
        arcade.draw_text(
            text[0],
            x1,
            HEIGHT - (header_height / 2), 
            arcade.color.WHITE,
            menu.Menu.header_font_size,
            x2 - x1,
            "center",
            "consolas",
            bold=True,
            anchor_y = "center"
        )
        #body 
        arcade.draw_text(
            text[1],
            x1 + 10,
            y1 - 10,
            arcade.color.WHITE,
            12,
            x2 - x1 - 10,
            "left",
            "consolas",
            bold=True,
            anchor_y = "top",
            multiline=True
        )

    def draw_stat_bar(self, character, stat, x_offset, y_offset, height):
        x, y = self.hex_to_pixel(character.tile.q, character.tile.r)
        if stat == "health":
            if character.health:
                arcade.draw_lrbt_rectangle_filled((x + x_offset) - (character.health / 4), (x + x_offset) + (character.health / 4), (y + y_offset) - height, (y + y_offset), arcade.color.RED)
                arcade.draw_lrbt_rectangle_outline((x + x_offset) - (character.health / 4), (x + x_offset) + (character.health / 4), (y + y_offset) - height, (y + y_offset), arcade.color.BLACK)
        elif stat == "cooldown":
            if character.cooldown:
                arcade.draw_lrbt_rectangle_filled((x + x_offset) - (character.cooldown / 4), (x + x_offset) + (character.cooldown / 4), (y + y_offset) - height, (y + y_offset), arcade.color.BLUE)
                arcade.draw_lrbt_rectangle_outline((x + x_offset) - (character.cooldown / 4), (x + x_offset) + (character.cooldown / 4), (y + y_offset) - height, (y + y_offset), arcade.color.BLACK)
    
    def draw_name(self, character, x_offset, y_offset, size):
        x, y = self.hex_to_pixel(character.tile.q, character.tile.r)
        arcade.draw_text(character.name, x + x_offset, y + y_offset, arcade.color.BLACK, size, 0, "center", anchor_x="center", anchor_y="center")

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
        self.draw_info_text(self.game_manager.hovered_info, self.info_box[0], self.info_box[1], self.info_box[2], self.info_box[3], UI_HEADER_HEIGHT)
        for character in self.game_manager.characters:
            self.draw_stat_bar(character, "health", 0, -20, 5)
            self.draw_stat_bar(character, "cooldown", 0, -30, 5)
            self.draw_name(character, 0, 30, 12)
        if self.game_manager.menu_stack:
            menu = self.game_manager.menu_stack[-1]
            menu.draw(panel_x, mid_y, WIDTH, 0, UI_HEADER_HEIGHT )

    def on_mouse_press(self, x, y, button, modifiers):
        self.game_manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        self.game_manager.on_mouse_motion(x, y, dx, dy)