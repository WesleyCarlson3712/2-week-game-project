import random
class AIBehavior:

    # ---------------------------------------------------------

    def take_turn(self, game_manager, character):
        raise NotImplementedError

    # ---------------------------------------------------------

    def get_enemies(self, game_manager, character):

        return [c for c in game_manager.characters if c.owner != character.owner and c.is_alive()]

    # ---------------------------------------------------------

    def get_closest_enemy(self, game_manager, character):

        enemies = self.get_enemies(game_manager, character)
        if not enemies:
            return None

        return min(enemies, key=lambda enemy: character.tile.distance_to(enemy.tile))

    # ---------------------------------------------------------

    def get_attacks_in_range(self, character, target):
        valid_attacks = []
        for attack in character.attacks:
            if (character.tile.distance_to(target.tile) <= attack.range):
                valid_attacks.append(attack)

        if not valid_attacks:
            return None

        return valid_attacks

    # ---------------------------------------------------------

    def get_best_neighbor_toward(self, character,target):

        valid_neighbors = [tile for tile in character.tile.neighbors if not tile.is_obstructed()]
        if not valid_neighbors:
            return None

        return min(valid_neighbors, key=lambda tile: tile.distance_to(target.tile))

    # ---------------------------------------------------------

    def get_best_neighbor_for_range(self, character, target, preferred_range):

        valid_neighbors = [tile for tile in character.tile.neighbors if not tile.is_obstructed()]

        if not valid_neighbors:
            return None
        
        return min(valid_neighbors, key=lambda tile: abs(tile.distance_to(target.tile) - preferred_range))