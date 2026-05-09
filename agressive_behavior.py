from ai_behavior import AIBehavior
import random
class AggressiveBehavior(AIBehavior):

    def take_turn(self, game_manager, character):
        target = self.get_closest_enemy(game_manager, character)
        if not target:
            return

        # ATTACK IF POSSIBLE
        attacks = self.get_attacks_in_range(character, target)

        if attacks:
            attack = random.choice(attacks)
            character.attack_target(target, attack)
        else:
            # MOVE ONE TILE AT A TIME
            moves_remaining = character.movement_range
            while moves_remaining > 0:
                next_tile = self.get_best_neighbor_toward(character, target)
                if not next_tile:
                    break

                old_distance = (character.tile.distance_to(target.tile))
                new_distance = (next_tile.distance_to(target.tile))

                # stop if movement no longer improves
                if new_distance >= old_distance:
                    break

                character.move(next_tile)
                moves_remaining -= 1

                # stop early if attack becomes possible
                attacks = self.get_attacks_in_range(character, target)

                if attacks:
                    break
                
            if(moves_remaining != character.movement_range):
                # character moved
                game_manager.updates.append(f"{character.name} moves to tile {character.tile.q}, {character.tile.r}.")
        game_manager.end_turn()