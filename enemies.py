import attack
import effect
import character
from agressive_behavior import AggressiveBehavior
from ranged_behavior import RangedBehavior

# Enemy type definitions (templates/factories)

def create_goblin(game, tile, owner):
    return character.Character(
        game, "Goblin", 80, tile, 4, 10, owner, behavior=AggressiveBehavior(),
        attacks=[attack.Attack("Club Smash", 15, 25, cooldown=50, range=1, critical_chance= 0.1, critical_multiplier= 1.4)]
    )

def create_archer(game, tile, owner):
    return character.Character(
        game, "Archer", 60, tile, 3, 10, owner, behavior=RangedBehavior(),
        attacks=[attack.Attack("Arrow Shot", 13, 19, cooldown=60, range=4, critical_chance= 0.2, critical_multiplier= 1.5)]
    )

def create_ice_elemental_ranged(game, tile, owner):
    return character.Character(
        game, "Ice Elemental", 70, tile, 3, 17, owner, behavior=RangedBehavior(),
        attacks=[attack.Attack("Freeze", 10, 20, cooldown=60, range=4)],
        effects=[effect.Effect(game, "Freezing", activations=1, interval=1, on_tick=lambda c: c.apply_cooldown(15))]
    )
def create_ice_elemental_melee(game, tile, owner):
    return character.Character(
        game, "Ice Elemental", 100, tile, 4, 12, owner, behavior=AggressiveBehavior(),
        attacks=[attack.Attack("Freeze", 15, 25, cooldown=50, range=1)],
        effects=[effect.Effect(game, "Freezing", activations=1, interval=1, on_tick=lambda c: c.apply_cooldown(10))]
    )
def create_fire_elemental_ranged(game, tile, owner):
    return character.Character(
        game, "Fire Elemental", 70, tile, 3, 17, owner, behavior=RangedBehavior(),
        attacks=[attack.Attack("Burn", 7, 15, cooldown=60, range=4)],
        effects=[effect.Effect(game, "Burning", activations=5, interval=20, on_tick=lambda c: c.take_damage(5))]
    )
def create_fire_elemental_melee(game, tile, owner):
    return character.Character(
        game, "Fire Elemental", 100, tile, 4, 12, owner, behavior=AggressiveBehavior(),
        attacks=[attack.Attack("Burn", 15, 25, cooldown=50, range=1)],
        effects=[effect.Effect(game, "Burning", activations=5, interval=20, on_tick=lambda c: c.take_damage(5))]
    )

enemy_types = {
    "goblin": create_goblin,
    "archer": create_archer,
    "ice_elemental_ranged": create_ice_elemental_ranged,
    "ice_elemental_melee": create_ice_elemental_melee,
    "fire_elemental_ranged": create_fire_elemental_ranged,
    "fire_elemental_melee": create_fire_elemental_melee
}
