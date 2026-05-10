import enemies
class Wave:
    def __init__(self, game, enemies, music = None, board_colors = None, background_color = None):
        self.game = game
        self.enemies = enemies
        self.music = music
        self.board_colors = board_colors
        self.background_color = background_color

    def begin_wave(self):
        if self.board_colors and self.background_color:
            self.game.grid.update_colors(self.board_colors, self.background_color)
        if self.music:
            self.game.grid.update_music(self.music)
        self.spawn_enemies()

    def spawn_enemies(self):
        for enemy in self.enemies:
            enemy_factory = enemies.enemy_types.get(enemy)
            enemy = enemy_factory(self.game, self.game.get_random_tile(), self.game.players["AI"])
            self.game.characters.append(enemy)
            enemy.apply_cooldown(30)
