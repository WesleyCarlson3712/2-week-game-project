class Ability:
    def __init__(self, name, cooldown, ability, description = None):
        self.name = name
        self.description = description
        self.ability = ability
        self.cooldown = cooldown

    def execute(self):
        self.ability()
