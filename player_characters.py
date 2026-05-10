import attack
import effect
import character
import ability
import random
def create_warrior(game):
    def rage_on_start(character):
        character.movement_range += 2
        character.resistance += 0.2
    def rage_cleanup(character):
        character.movement_range -= 2
        character.resistance -= 20.

    return character.Character(
        game, "Warrior", 150, game.get_random_tile(), 3, 15, game.players["Player"], 
            attacks=[
                attack.Attack("Slash", 25, 40, cooldown=50, range=1, 
                    effects=[
                        effect.Effect(game, "Bleeding", 10, 2, delay=10, on_tick=lambda c: c.take_damage(random.choice(range(4, 10, 1))))
                        ]),
                attack.Attack("Throw Axe", 30, 35, cooldown=60, range=2)
                ], abilities=[
                    ability.Ability("Rage", 20, lambda: game.active_character.apply_effect(
                            effect.Effect(game, "Rage", 100, 2, on_start = lambda c: rage_on_start(c), cleanup = lambda: rage_cleanup())
                        ), "Increases movement range by 2 and resistance by 20%% for 100 ticks.")
                    ])

def create_wizard(game):
    def heal_adjacent(game):
        for tile in game.active_character.tile.neighbors:
            if tile.character:
                if tile.character.owner.name == game.active_character.owner.name:
                    tile.character.heal(30)
        game.active_character.heal(30)
    return character.Character(
        game, "Wizard", 100, game.get_random_tile(), 3, 20, game.players["Player"],
            attacks=[
                attack.Attack("Fireball", 15, 25, cooldown=60, range=4, 
                    effects=[
                        effect.Effect(game, "Burning", 20, 3, on_tick=lambda c: c.take_damage(random.choice(range(10, 21, 1))))
                    ]),
                attack.Attack("Ice Blast", 30, 35, cooldown=50, range=3, 
                    effects=[
                        effect.Effect(game, "Freezing", 1, 1, on_start=lambda c: c.apply_cooldown(random.choice(range(5, 16, 1))))
                    ]),
                ], abilities=[
                    ability.Ability("Heal", 50, lambda: heal_adjacent(game), "Heals self and adjacent allies by 30 points.")
                    ])

def create_ranger(game):
    def slowed_on_start(character):
        character.movement_range -= 1
        character.movement_cost += 10
    def slowed_cleanup(character):
        character.movement_range += 1
        character.movement_cost == 10

    return character.Character(
        game, "Ranger", 80, game.get_random_tile(), 3, 15, game.players["Player"],
            attacks=[
                attack.Attack("Distance Shot", 20, 40, cooldown=60, range=5, critical_chance=0.5, critical_multiplier=2),

                attack.Attack("Crippling Shot", 40, 50, cooldown=50, range=3,
                    effects=[
                        effect.Effect(game, "Sloweness", 80, 2,on_start=lambda c: slowed_on_start(c), cleanup=lambda c: slowed_cleanup(c))
                    ])
            ])