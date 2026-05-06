class Player:
    def __init__(self, game, name, items=[]):
        self.game_manager = game
        self.name = name
        self.characters = []
        self.items = items

    def add_character(self, character):
        self.characters.append(character)

    def remove_character(self, character):
        if character in self.characters:
            self.characters.remove(character)

    def add_item(self, item):
        self.items.append(item)
        item.owner = self

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            item.owner = None
    