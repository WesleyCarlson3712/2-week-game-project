import random


class Character:
    def __init__(self, game, name, max_health, tile, movement_range, move_cost, owner, behavior = None, attacks=None, items=None, abilities=None, resistance = None):
        self.game = game
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.tile = tile
        self.movement_range = movement_range
        self.movement_cost = move_cost
        self.owner = owner
        self.resistance = resistance
        self.behavior = behavior
        self.attacks = attacks
        self.abilities = abilities
        self.items = items if items is not None else []
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
        self.apply_cooldown(self.movement_cost)
    
    def apply_cooldown(self, cooldown):
        # using this function gives room to add discounts or increases to cooldown in the future
        self.cooldown += cooldown

    def take_damage(self, damage):
        if self.resistance:
            damage *= 1 - self.resistance
        self.health -= round(damage)

        if self.health < 0:
            self.health = 0
        self.game.updates.append(f"{self.name} takes {damage} damage.")
        if not self.is_alive():
            # Remove from tile
            if self.tile and self.tile.character is self:
                self.tile.character = None
            # Remove from game character list
            if self in self.game.characters:    
                self.game.characters.remove(self)
            if self in self.game.turn_queue:
                self.game.turn_queue.remove(self)
            self.game.updates.append(f"{self.name} has been defeated!")

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
        self.game.updates.append(f"{self.name} heals {amount} HP. ({self.health}/{self.max_health} HP)")

    def use_ability(self, ability):
        ability.execute()
        self.game.updates.append(f"{self.name} uses {ability.name}.")
        self.apply_cooldown(ability.cooldown)

    def equip_item(self, item):
        item.owner.remove_item(item)  # Remove from player's inventory
        self.items.append(item) # Add to character's equipped items
        item.on_equip(self)
    
    def unequip_item(self, item):
        if item in self.items:
            self.items.remove(item)
            self.owner.add_item(item)  # Return to player's inventory
            item.on_unequip(self)

    def attack_target(self, target, attack):
        self.game.updates.append(f"{self.name} uses {attack.name} on {target.name}.")
        attack.execute(target, self)
        self.apply_cooldown(attack.cooldown)

    def is_alive(self):
        return self.health > 0

    def apply_effect(self, effect):
        effect.start_tick = self.game.tick
        self.effects.append(effect)
        effect.on_start(self)
        self.game.updates.append(f"{self.name} is affected with {effect.name}.")

    def remove_effect(self, effect, trigger_on_end=True):
        if effect in self.effects:
            if trigger_on_end:
                effect.on_end(self)
            else:
                effect.cleanup(self)
            self.effects.remove(effect)

    def get_enemies_in_range(self, range):
        enemies_in_range = []
        for c in self.game.characters:
            if c is not self and c.owner != self.owner and c.is_alive():
                if self.tile.distance_to(c.tile) <= range:
                    enemies_in_range.append(c)
        return enemies_in_range
     
