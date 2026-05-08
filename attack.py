import random

class Attack:
    def __init__(self, name, damage_min, damage_max, cooldown, range, requires_target = True,critical_chance=0, critical_multiplier=0, effects=[]):
        self.name = name
        self.damage_min = damage_min
        self.damage_max = damage_max
        self.critical_chance = critical_chance
        self.critical_multiplier = critical_multiplier
        self.cooldown = cooldown
        self.range = range
        self.requires_target = requires_target
        self.effects = effects
        self.description = ""

        
        self.description += f"Damage: {damage_min}-{damage_max}\n"
        if critical_chance > 0:
            self.description += f"Critical Chance: {critical_chance*100}%\n"
            self.description += f"Critical Multiplier: {critical_multiplier}x\n"
        self.description += f"Cooldown: {cooldown}\n"
        self.description += f"Range: {range}\n"
        for effect in effects:
            self.description += f"Effect: {effect.name}\n"


    def calculate_damage(self):
        damage = random.randint(self.damage_min, self.damage_max)
        if random.random() < self.critical_chance:
            damage *= self.critical_multiplier
        return damage

    def execute(self, target, attacker):
        damage = self.calculate_damage()
        target.take_damage(damage)
        for effect in self.effects:
            target.apply_effect(effect)

