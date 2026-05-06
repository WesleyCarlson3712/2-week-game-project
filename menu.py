import arcade
class Menu:
    def __init__(self, game, header, options = ("", lambda: None)):
        self.game = game
        self.options = options  # (label, function)
        self.selected_index = None
        self.header = header
        self.header_font_size = 30
        self.option_font_size = 20
        self.option_rects = []  # to store the rectangles for each option for mouse interaction

    def get_option_index_at(self, x, y):
        for i, rect in enumerate(self.option_rects):
            x1, y1, x2, y2 = rect
            if x1 <= x <= x2 and y1 >= y >= y2:
                return i

    def select(self):
        _, action = self.options[self.selected_index]
        if action:
            action()

    def draw(self, x1, y1, x2, y2, header_height):

        # Draw options
        height_of_options_box = y1 - header_height - y2
        top_y_of_options_box = y1 - header_height
        option_height = height_of_options_box / len(self.options) if self.options else 0
        vertical_padding = option_height / 10
        horizontal_padding = (x2 - x1) / 20

        # Draw header if it exists
        if self.header:
            arcade.draw_text(
                self.header,
                x1,
                y1 - (header_height / 2), 
                arcade.color.WHITE,
                self.header_font_size,
                x2 - x1,
                "center",
                "consolas",
                bold=True,
                anchor_y = "center"
            )

        for i, (label, _) in enumerate(self.options):
            option_y = top_y_of_options_box - i * option_height - option_height / 2
            # store rects as (x1, y1, x2, y2) for mouse interaction
            self.option_rects.append((
                x1 + horizontal_padding, 
                (option_y + (option_height / 2)) - vertical_padding, 
                x2 - horizontal_padding, 
                (option_y - (option_height / 2)) + vertical_padding
                ))

            arcade.draw_lrbt_rectangle_filled(
                self.option_rects[-1][0], self.option_rects[-1][2],
                self.option_rects[-1][3], self.option_rects[-1][1],
                arcade.color.JET
            )
            arcade.draw_lrbt_rectangle_outline(
                self.option_rects[-1][0], self.option_rects[-1][2],
                self.option_rects[-1][3], self.option_rects[-1][1],
                arcade.color.BLACK
            )

            if i == self.selected_index:
                color = arcade.color.YELLOW
            else:
                color = arcade.color.WHITE

            arcade.draw_text(
                label,
                x1,
                option_y,
                color,
                self.option_font_size,
                x2 - x1,
                "center",
                "consolas",
                anchor_y = "center"

            )