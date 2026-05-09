from ai_behavior import AIBehavior
import random

class RangedBehavior(AIBehavior):

    def take_turn(self, game_manager, character):

        target = self.get_closest_enemy(game_manager, character)

        if not target:
            return
        # ATTACK IF POSSIBLE
        attacks = self.get_attacks_in_range(character, target)

        if attacks:
            attack = random.choice(attacks)
            character.attack_target(target, attack)
            return
        # DETERMINE IDEAL RANGE
        else:
            preferred_range = max(atk.range for atk in character.attacks)
            moves_remaining = (character.movement_range)

            while moves_remaining > 0:

                next_tile = (self.get_best_neighbor_for_range(character, target, preferred_range))

                if not next_tile:
                    break

                current_delta = abs(character.tile.distance_to(target.tile) - preferred_range)
                new_delta = abs(next_tile.distance_to(target.tile) - preferred_range)

                # stop if no improvement
                if new_delta >= current_delta:
                    break

                character.move(next_tile)

                moves_remaining -= 1

                # stop if attack becomes possible
                attacks = self.get_attacks_in_range(character, target)

                if attacks:
                    break
                
            if(moves_remaining != character.movement_range):
                # character moved
                game_manager.updates.append(f"{character.name} moves to tile {character.tile.q}, {character.tile.r}.")
        game_manager.end_turn()