import menu
import menus
import player
import item
import player_characters
import random
import ability
import wave
class GameManager:
    def __init__(self, grid):
        self.grid = grid

        self.players = {
            "Player": player.Player(self, "Player"), 
            "AI": player.Player(self, "AI")
            }
        self.characters = []
        self.tick = 0

        self.menu_stack = []
        self.current_menu = None

        self.state_stack = []
        self.state = ""   # or "player_turn", "menu"
        self.active_character = None

        self.pending_attack = None
        self.pending_item = None
        self.pending_ability = None
        self.moves_taken = 0

        self.hovered_tile = None
        self.hovered_info = ("", "")
        self.updates = []

        self.turn_queue = []

        self.mouse_x = 0
        self.mouse_y = 0

        self.wave_number = 0
        self.waves = [
            wave.Wave(self, ["archer", "goblin"], "music/normal.mp3", [(211, 211, 211), (128, 128, 128), (169, 169, 169)], (26, 17, 16)),
            wave.Wave(self, ["archer", "archer", "goblin", "goblin"], None, [(211, 211, 211), (128, 128, 128), (169, 169, 169)], (26, 17, 16)),
            wave.Wave(self, ["ice_elemental_ranged", "ice_elemental_melee"], "music/ice.mp3", [(176, 224, 251), (164, 236, 242), (232, 246, 249)], (222, 235, 244)),
            wave.Wave(self, ["ice_elemental_ranged", "ice_elemental_ranged", "ice_elemental_melee", "ice_elemental_melee"], None, [(176, 224, 251), (164, 236, 242), (232, 246, 249)], (222, 235, 244)),
            wave.Wave(self, ["fire_elemental_ranged", "fire_elemental_melee"], "music/fire.mp3", [(165, 22, 0), (198, 82, 0), (160, 58, 17)], (93, 22, 0)),
            wave.Wave(self, ["fire_elemental_ranged", "fire_elemental_ranged", "fire_elemental_melee", "fire_elemental_melee"], None, [(165, 22, 0), (198, 82, 0), (160, 58, 17)], (93, 22, 0))
            ]
        

        self.items = {
            "Health ring": item.Item("Health Ring", "Increases max health by 20 points.", on_equip=lambda c: setattr(c, 'max_health', c.max_health + 20), on_unequip=lambda c: setattr(c, 'max_health', c.max_health - 20)),
            "Speed boots": item.Item("Speed Boots", "Increases max movement distance by 1.", on_equip=lambda c: setattr(c, 'movement_range', c.movement_range + 1), on_unequip=lambda c: setattr(c, 'movement_range', c.movement_range - 1)),
            # "Health potion": item.Item("Health Potion", "Heals 40 hp (used as an ability).", on_equip=lambda c: c.abilities.append(ability.Ability("Health Potion", 1, lambda: self.active_character.heal(40))), on_unequip=lambda c: c.abilities.pop()) 
        }
        self.players["Player"].add_item(self.items["Health ring"])
        self.players["Player"].add_item(self.items["Speed boots"])
        self.characters.append(player_characters.create_warrior(self))
        self.characters.append(player_characters.create_wizard(self))
        self.characters.append(player_characters.create_ranger(self))
        
        self.waves[self.wave_number].begin_wave()
        self.start_turn_cycle()
        self.update_info(self.mouse_x, self.mouse_y)

    def all_enemies_dead(self):
        for character in self.characters:
            if character.owner == self.players["AI"]:
                return False
        return True

    def get_random_tile(self, allow_obstructed=False):
        tiles = list(self.grid.tiles.values())
        if not allow_obstructed:
            tiles = [t for t in tiles if not t.is_obstructed()]
        if not tiles:
            return None
        return random.choice(tiles)

# --------------------------------------------------------------------------------------------------

    def start_move(self):
        self.state_stack.append("select tile for move")
        self.push_menu(menu.Menu(self, "MOVE", [("Cancel", lambda: self.pop_menu(), "Go back to the previous menu.")]))
    
    def execute_attack(self, attack):
        self.pending_attack = attack
        self.state_stack.append("choose attack target")
        self.push_menu(menu.Menu(self, self.pending_attack.name.upper(), [("Cancel", lambda: self.pop_menu(), "Go back to the previous menu.")]))

    def push_menu(self, menu):
        self.menu_stack.append(menu)
        self.current_menu = menu

    def pop_menu(self):
        self.pending_ability = None
        self.pending_item = None
        if self.menu_stack:
            if self.state_stack[-1] == "actions menu":
                return
            #never pop the main menu, only submenus
            self.menu_stack.pop()
            self.state_stack.pop()
            self.current_menu = self.menu_stack[-1] if self.menu_stack else None

# --------------------------------------------------------------------------------------------------

    def build_turn_queue(self):
        ready = [c for c in self.characters if c.cooldown == 0 and c.is_alive()]
        ready.sort(key=lambda c: c.priority, reverse=True)

        self.turn_queue = ready
        self.current_turn_index = 0

    def tick_effects(self, characters):
        for character in characters:
            for effect in character.effects:

                ticks_since_start = self.tick - effect.start_tick

                if ticks_since_start >= effect.delay:
                    if (ticks_since_start - effect.delay) % effect.interval == 0:
                        self.updates.append(f"{effect.name} triggers for {character.name}.")
                        effect.on_tick(character)
                    if ticks_since_start >= effect.delay + effect.interval * effect.activations:
                        character.remove_effect(effect)

    def process_next_turn(self):
        character = self.turn_queue[0]
        self.active_character = character

        if character.owner == self.players["Player"]:
            menus.show_actions_menu(self, character)
        elif character.owner == self.players["AI"]:
            # AI turn
            self.state_stack.append("begin enemy turn")
            self.process_ai_turn(character)
            self.end_turn()

    def process_ai_turn(self, character):
        if character.behavior:
            character.behavior.take_turn(self, character)

    def end_turn(self):
        self.state_stack.clear()
        self.menu_stack.clear()
        self.moves_taken = 0
        if self.turn_queue:
            self.turn_queue.pop(0)
            self.active_character = None
            
            def continue_to_next_turn():
                self.updates.clear()
                self.pop_menu()
                if self.turn_queue:
                    self.process_next_turn()
                else:
                    self.end_of_turn_cycle()
            self.state_stack.append("turn just ended")
            self.push_menu(menu.Menu(self, "TURN END", [("Continue", lambda: continue_to_next_turn(), "Continue to the next turn.")]))
            
        else:
            self.end_of_turn_cycle()

    def end_of_turn_cycle(self):
        self.tick += 1
        for character in self.characters:
            if character.cooldown > 0:
                character.cooldown -= 1
        self.tick_effects(self.characters)
        if self.all_enemies_dead():
                if self.wave_number < len(self.waves):
                    # self.players["Player"].add_item(self.items["Health potion"])
                    self.wave_number += 1
                    self.updates.append(f"Wave {self.wave_number + 1}")
                    self.waves[self.wave_number].begin_wave()
        self.start_turn_cycle()

    def start_turn_cycle(self):
        
        self.build_turn_queue()
        if self.turn_queue:
            def continue_to_next_turn():
                self.updates.clear()
                self.pop_menu()
                self.process_next_turn()
            if self.updates:
                self.state_stack.append("turn about to start")
                self.push_menu(menu.Menu(self, "TURN END", [("Continue", lambda: continue_to_next_turn(), "Continue to the next turn.")]))
            else:
                self.process_next_turn()
        else:
            self.end_of_turn_cycle()

# --------------------------------------------------------------------------------------------------

    def on_mouse_press(self, x, y, button, modifiers):

        q, r = self.grid.pixel_to_hex(x, y)
        tile = self.grid.tiles.get((q, r))

        option_index = self.current_menu.get_option_index_at(x, y)
        if option_index is not None:
            self.current_menu.select()
            return

        if self.state_stack[-1] == "select tile for move" and self.active_character:
            if tile and tile in self.active_character.tile.neighbors and not tile.is_obstructed():
                self.active_character.move(tile)
                self.moves_taken += 1
                if self.moves_taken >= self.active_character.movement_range:
                    self.updates.append(f"{self.active_character.name} moves to tile {self.active_character.tile.q}, {self.active_character.tile.r}.")
                    self.end_turn()
                if self.moves_taken == 1:
                    def done_moving(game):
                        game.updates.append(f"{game.active_character.name} moves to tile {self.active_character.tile.q}, {self.active_character.tile.r}.")
                        game.end_turn()
                    self.push_menu(menu.Menu(self, "MOVE", [("Done", lambda: done_moving(self), "End turn.")]))

        elif self.state_stack[-1] == "choose attack target" and self.pending_attack:
            if tile and self.active_character.tile.distance_to(tile) <= self.pending_attack.range:
                if self.pending_attack.requires_target:
                    if not tile.character or tile.character.owner == self.active_character.owner:
                        return
                self.active_character.attack_target(tile.character, self.pending_attack)
                self.pending_attack = None
                self.pop_menu()
                self.end_turn()

    def update_selected_option(self, x, y):
        option_index = self.current_menu.get_option_index_at(x, y)
        if option_index is not None:
            self.current_menu.selected_index = option_index
        else:
            self.current_menu.selected_index = None

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def update_info(self, mouse_x, mouse_y):
        q, r = self.grid.pixel_to_hex(mouse_x, mouse_y)
        tile = self.grid.tiles.get((q, r))
        header = ""
        info = ""
        def display_character_stats(self, character):
            header = character.name.upper()
            info = ""
            info += f"Health: {character.health}/{character.max_health}\n"
            info += f"Cooldown: {character.cooldown}\n"
            info += f"Movement Range: {character.movement_range}\n"
            info += f"Movement Cost: {character.movement_cost}\n"
            if character.attacks:
                info += "Attacks: "
                info += ", ".join(attack.name for attack in character.attacks)
            if character.items:
                info += "\nItems: "
                info += ", ".join(item.name for item in character.items)
            if character.abilities:
                info += "\nAbilities: "
                info += ", ".join(ability.name for ability in character.abilities)
            if character.effects:
                info += "\nEffects: "
                info += ", ".join(effect.name for effect in character.effects)
            return header, info
        
        def display_default_info(self):
            # if you are hovering over neither a menu option or a tile
            header = "" 
            info = ""
            if self.state_stack[-1] == "turn about to start" or self.state_stack[-1] == "turn just ended":
                header = "UPDATES"
                info = "\n".join(self.updates) if self.updates else "No updates."
            else:
                if self.state_stack:
                    header, info = display_character_stats(self, self.active_character)

                    if self.state_stack[-1] == "select tile for move":
                        header = "MOVE"
                        info = f"Green tiles are reachable in one move.\n\
                            Yellow tiles can be reached this turn\n\
                            Movement cost: {self.active_character.movement_cost}\n\
                            Movement range: {self.active_character.movement_range}"
                    elif self.state_stack[-1] == "choose attack":
                        header = "ATTACK"
                        info = "Choose attack." if self.active_character.attacks else "No attacks available." 
                    elif self.state_stack[-1] == "choose attack target":
                        header = self.pending_attack.name
                        info = self.pending_attack.description
                        if not self.active_character.get_enemies_in_range(self.pending_attack.range):
                            info += "\nNO ENEMIES IN RANGE"

                    elif self.state_stack[-1] == "abilities menu":
                        header = "ABILITIES"
                        info = "Choose ability." if self.active_character.abilities else "No abilities available."
                    elif self.state_stack[-1] == "confirm use ability":
                        header = self.pending_ability.name
                        info = self.pending_ability.description

                    elif self.state_stack[-1] == "inventory menu":
                        header = "INVENTORY"
                        info = "Equip items from your party's collective inventory, or unequip items."
                    elif self.state_stack[-1] == "equip menu":
                        header = "EQUIP ITEM"
                        info = "Choose an item to equip." if self.active_character.owner.items else "Inventory empty; no items to equip."
                    elif self.state_stack[-1] == "confirm equip":
                        header = self.pending_item.name
                        info = self.pending_item.description
                    elif self.state_stack[-1] == "unequip menu":
                        header = "UNEQUIP ITEM"
                        info = "Choose an item to equip." if self.active_character.items else "Inventory empty. no items to unequip."
                    elif self.state_stack[-1] == "unconfirm equip":
                        header = self.pending_item.name
                        info = self.pending_item.description
            return header, info

        if tile:
            # if you are hovering over a tile
            if tile.character:
                header, info = display_character_stats(self, tile.character)
                
            else:
                if self.state_stack[-1] == "select tile for move":
                    header = f"Tile ({tile.q}, {tile.r})"
                    character = self.active_character
                    reachable_tiles = {}
                    for (reachable_tile, distance) in character.tile.reachable_tiles(character.movement_range - self.moves_taken):
                        reachable_tiles[(reachable_tile.q, reachable_tile.r)] = distance
                    if (tile.q, tile.r) in reachable_tiles:
                        distance = reachable_tiles[(tile.q, tile.r)]
                        if distance == 1:
                            info = f"Move to tile\n\
                                Cooldown: {character.movement_cost}"
                        else:
                            info = f"Tile reachable in {distance} moves.\n\
                                Cooldown to travel to tile: {distance * character.movement_cost}"
                    else:
                        info = "Tile out of range"
                else:
                    header, info = display_default_info(self)

        elif self.current_menu and self.current_menu.selected_index is not None:
            # if you are hovering over a menu option
                option_text, _, description = self.current_menu.options[self.current_menu.selected_index]
                header = option_text.upper()
                info = description
   
        else:
            header, info = display_default_info(self)
            
        self.hovered_info = (header, info)