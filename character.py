import random


class Character:
    def __init__(self, name, max_health, tile, movement_range, move_cost, owner, attacks = None, items = [], abilities = None):
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.tile = tile
        self.movement_range = movement_range
        self.move_cost = move_cost
        self.owner = owner
        self.attacks = attacks
        self.abilities = abilities
        self.items = items
        self.cooldown = 0
        self.effects = []
        self.priority = random.random()

        owner.add_character(self)
        tile.character = self

    def move(self, target_tile):
        if target_tile.is_obstructed():
            raise ValueError("Target tile is occupied")
        self.tile.character = None
        target_tile.character = self
        self.tile = target_tile
        self.apply_cooldown(self.move_cost)
    
    def apply_cooldown(self, cooldown):
        # using this function gives room to add discounts or increases to cooldown in the future
        self.cooldown += cooldown

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def use_ability(self, ability):
        ability(self)

    def equip_item(self, item):
        print(f"item owner before equip: {item.owner.name if item.owner else 'None'}")
        item.owner.remove_item(item)  # Remove from player's inventory
        print(f"Equipping {item.name} to {self.name}")
        self.items.append(item) # Add to character's equipped items
        item.on_equip(self)
    
    def unequip_item(self, item):
        if item in self.items:
            self.items.remove(item)
            item.on_unequip(self)

    def attack_target(self, target, attack):
        attack.execute(target, self)

    def is_alive(self):
        return self.health > 0

    def apply_effect(self, effect):
        self.effects.append(effect)
        effect.on_start(self)

    def remove_effect(self, effect, trigger_on_end=True):
        if effect in self.effects:
            if trigger_on_end:
                effect.on_end(self)
            else:
                effect.cleanup(self)
            self.effects.remove(effect)
