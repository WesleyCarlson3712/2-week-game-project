import enemies
class Wave:
    def __init__(self, game, enemies, board_colors = [(0,0,0),(0,0,0),(0,0,0)], background_color = (0,0,0)):
        self.game = game
        self.enemies = enemies
        self.board_colors = board_colors
        self.background_color = background_color

    def begin_wave(self):
        self.game.grid.update_colors(self.board_colors, self.background_color)
        self.spawn_enemies()

    def spawn_enemies(self):
        for enemy in self.enemies:
            enemy_factory = enemies.enemy_types.get(enemy)
            enemy = enemy_factory(self.game, self.game.get_random_tile(), self.game.players["AI"])
            self.game.characters.append(enemy)
