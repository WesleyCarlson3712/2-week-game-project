class Item:
    def __init__(self, name, description = None, on_equip=None, on_unequip=None):
        self.name = name
        self.owner = None
        self.description = description
        self.on_equip = on_equip
        self.on_unequip = on_unequip

    def on_equip(self, character):
        if self.on_equip:
            self.on_equip(character)

    def on_unequip(self, character):
        if self.on_unequip:
            self.on_unequip(character)

    def delete(self):
        if self in self.owner.items:
            self.owner.items.remove(self)