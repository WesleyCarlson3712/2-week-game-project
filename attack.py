import random

class Attack:
    def __init__(self, name, damage_min, damage_max, cooldown, range=1, critical_chance=0, critical_multiplier=0, effects=[]):
        self.name = name
        self.damage_min = damage_min
        self.damage_max = damage_max
        self.critical_chance = critical_chance
        self.critical_multiplier = critical_multiplier
        self.cooldown = cooldown
        self.range = range
        self.effects = effects

    def calculate_damage(self):
        damage = random.randint(self.damage_min, self.damage_max)
        if random.random() < self.critical_chance:
            damage *= self.critical_multiplier
        return damage

    def execute(self, target, attacker):
        damage = self.calculate_damage()
        target.take_damage(damage)
        attacker.apply_cooldown(self.cooldown)
        for effect in self.effects:
            target.apply_effect(effect)

