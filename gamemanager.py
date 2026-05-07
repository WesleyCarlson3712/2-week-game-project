import menu
import menus
import attack
import effect
import character
import player
import item
import time
class GameManager:
    def __init__(self, grid):
        self.grid = grid

        self.players = {
            "Player": player.Player(self, "Player"), 
            "AI": player.Player(self, "AI")
            }
        self.players["Player"].add_item(item.Item("Health Ring", on_equip=lambda c: setattr(c, 'max_health', c.max_health + 20), on_unequip=lambda c: setattr(c, 'max_health', c.max_health - 20)))
        self.players["Player"].add_item(item.Item("Speed Boots", on_equip=lambda c: setattr(c, 'movement_range', c.movement_range + 1), on_unequip=lambda c: setattr(c, 'movement_range', c.movement_range - 1)))
        self.characters = []
        self.tick = 0

        self.menu_stack = []
        self.current_menu = None

        self.state_stack = []
        self.state = ""   # or "player_turn", "menu"
        self.active_character = None

        self.pending_attack = None
        self.moves_taken = 0

        self.hovered_tile = None
        self.hovered_info = ("info", "this window shows info about the currently hovered thing")

        self.turn_queue = []

        self.characters.append(character.Character("john", 100, self.grid.tiles[(0, 0)], 3, 10, self.players["Player"], attacks=[
            attack.Attack("Slash", 20, 25, cooldown=2, range=1),
            attack.Attack("Fireball", 30, 35, cooldown=3, range=3, effects=[effect.Effect("Burn", activations=5, interval=1, on_tick=lambda c: c.take_damage(5))])
        ]))
        self.characters.append(character.Character("lisa", 100, self.grid.tiles[(1, 0)], 4, 10, self.players["Player"], attacks=[
            attack.Attack("Stomp", 25, 30, cooldown=2, range=2)
        ]))
        self.characters.append(character.Character("duck", 100, self.grid.tiles[(1, 1)], 5, 10, self.players["Player"], attacks=[
            attack.Attack("Heal", 30, 35, cooldown=3, range=1)
        ]))
        self.characters.append(character.Character("goblin", 80, self.grid.tiles[(-1, 0)], 3, 10, self.players["AI"], attacks=[
            attack.Attack("Club Smash", 15, 20, cooldown=2, range=1)
        ]))
        self.start_turn_cycle()


    def confirm_equip_item(self, character, item):
        print(f"Confirming equip of {item.name} for {character.name}")
        self.state_stack.append("confirm equip")
        def equip():
            character.equip_item(item)
            self.pop_menu()
            self.pop_menu()
        self.push_menu(menu.Menu(self, item.name.upper(), [("Cancel", lambda: self.pop_menu()), ("Equip", lambda: equip())]))

    def confirm_unequip_item(self, character, item):
        print(f"Confirming unequip of {item.name} for {character.name}")
        self.state_stack.append("confirm unequip")
        def unequip():
            character.unequip_item(item)
            self.pop_menu()
            self.pop_menu()
        self.push_menu(menu.Menu(self, item.name.upper(), [("Cancel", lambda: self.pop_menu()), ("Unequip", lambda: unequip())]))

    def start_move(self, character):
        self.state_stack.append("select tile for move")
        self.push_menu(menu.Menu(self, "MOVE", [("Cancel", lambda: self.pop_menu())]))
    
    def execute_attack(self, attack):
        self.pending_attack = attack
        self.state_stack.append("choose attack target")
        self.push_menu(menu.Menu(self, self.pending_attack.name.upper(), [("Cancel", lambda: self.pop_menu())]))

    def build_turn_queue(self):
        ready = [c for c in self.characters if c.cooldown == 0 and c.is_alive()]
        ready.sort(key=lambda c: c.priority, reverse=True)

        self.turn_queue = ready
        self.current_turn_index = 0

    def push_menu(self, menu):
        self.menu_stack.append(menu)
        self.current_menu = menu
        print(self.state_stack)
        print([menu.header for menu in self.menu_stack])

    def pop_menu(self):
        if self.menu_stack:
            if self.state_stack[-1] == "actions menu":
                return
            #never pop the main menu, only submenus
            self.menu_stack.pop()
            self.state_stack.pop()
            self.current_menu = self.menu_stack[-1] if self.menu_stack else None
            print(self.state_stack)
            print([menu.header for menu in self.menu_stack])

    def tick_effects(self, characters):
        for character in characters:
            for effect in character.effects:

                ticks_since_start = self.tick - effect.start_tick

                if ticks_since_start >= effect.delay:
                    if ticks_since_start - effect.delay % effect.interval == 0:
                        effect.on_tick(character)
                    if ticks_since_start >= effect.delay + effect.interval * effect.activations:
                        character.remove_effect(effect)

    def process_next_turn(self):
        print (f"Cooldowns: {[ (c.name, c.cooldown, c.health, c.is_alive()) for c in self.characters ]}")
        character = self.turn_queue[0]
        print(f"Processing turn for {character.name}")
        print(f"tile: {character.tile.q}, {character.tile.r}")

        if character.owner == self.players["Player"]:
            self.active_character = character
            menus.show_actions_menu(self, character)
        elif character.owner == self.players["AI"]:
            # AI turn
            # self.run_ai(character)
            self.process_ai_turn(character)
            self.end_turn()

    def process_ai_turn(self, character):
        # Very basic AI: if it can attack, it attacks. Otherwise, it moves towards the closest player character.
        player_characters = [c for c in self.characters if c.owner == self.players["Player"] and c.is_alive()]
        if not player_characters:
            return  # No targets left

        target = min(player_characters, key=lambda c: character.tile.distance_to(c.tile))

        # Check if we can attack
        for attack in character.attacks:
            if character.tile.distance_to(target.tile) <= attack.range:
                print(f"{character.name} attacks {target.name} with {attack.name}")
                character.attack_target(target, attack)
                return

        # Move towards target
        # This is a placeholder for pathfinding logic. For now, it just tries to move closer on the q axis.
        if target.tile.q < character.tile.q:
            new_tile = self.grid.tiles.get((character.tile.q - 1, character.tile.r))
        elif target.tile.q > character.tile.q:
            new_tile = self.grid.tiles.get((character.tile.q + 1, character.tile.r))
        else:
            new_tile = None

        if new_tile and not new_tile.is_obstructed():
            print(f"{character.name} moves from ({character.tile.q}, {character.tile.r}) to ({new_tile.q}, {new_tile.r})")
            character.move(new_tile)

    def end_turn(self):
        print(f"Ending turn")
        self.state_stack.clear()
        self.menu_stack.clear()
        self.moves_taken = 0
        if self.turn_queue:
            self.turn_queue.pop(0)
            self.active_character = None
            
        if self.turn_queue:
            print(f"Next up: {self.turn_queue[0].name}")
            self.process_next_turn()
        else:
            print("End of turn cycle")
            for character in self.characters:
                if character.cooldown > 0:
                    character.cooldown -= 1
            self.tick_effects(self.characters)
            self.start_turn_cycle()

    def start_turn_cycle(self):
        print(f"Starting turn cycle {self.tick}")
        
        self.tick += 1
        self.build_turn_queue()
        if self.turn_queue:
            self.process_next_turn()
        else:
            self.end_turn()

    def on_mouse_press(self, x, y, button, modifiers):

        q, r = self.grid.pixel_to_hex(x, y)
        tile = self.grid.tiles.get((q, r))
        print(f"Clicked on tile: {q}, {r}" if (q, r) in self.grid.tiles else "Clicked outside of grid")

        option_index = self.current_menu.get_option_index_at(x, y)
        if option_index is not None:
            self.current_menu.select()
            return

        if self.state_stack[-1] == "select tile for move" and self.active_character:
            if tile and tile in self.active_character.tile.neighbors and not tile.is_obstructed():
                self.active_character.move(tile)
                self.moves_taken += 1
                if self.moves_taken >= self.active_character.movement_range:
                    self.end_turn()
                if self.moves_taken == 1:
                    self.push_menu(menu.Menu(self, "MOVE", [("Done", lambda: self.end_turn())]))

        elif self.state_stack[-1] == "choose attack target" and self.pending_attack:
            if tile and self.active_character.tile.distance_to(tile) <= self.pending_attack.range:
                if self.pending_attack.requires_target:
                    if not tile.character or tile.character.owner == self.active_character.owner:
                        return
                self.active_character.attack_target(tile.character, self.pending_attack)
                self.pending_attack = None
                self.pop_menu()
                self.end_turn()

    def on_mouse_motion(self, x, y, dx, dy):
        self.update_info(x, y)
        q, r = self.grid.pixel_to_hex(x, y)
        tile = self.grid.tiles.get((q, r))

        option_index = self.current_menu.get_option_index_at(x, y)
        if option_index is not None:
            self.current_menu.selected_index = option_index
        else:
            self.current_menu.selected_index = None

    def update_info(self, mouse_x, mouse_y):
        q, r = self.grid.pixel_to_hex(mouse_x, mouse_y)
        tile = self.grid.tiles.get((q, r))

        if tile:
            if tile.character:
                character = tile.character
                info = ""
                info += f"Health: {character.health}/{character.max_health}\n"
                info += f"Movement Range: {character.movement_range}\n"
                info += f"Movement Cost: {character.move_cost}\n"
                if character.attacks:
                    info += "Attacks: "
                    info += ", ".join(attack.name for attack in character.attacks)
                if character.items:
                    info += "\nItems: "
                    info += ", ".join(item.name for item in character.items)
                if character.abilities:
                    info += "\nAbilities: "
                    info += ", ".join(ability.name for ability in character.abilities)
                self.hovered_info = (character.name.upper(), info)

            else:
                self.hovered_info = (f"Tile ({q}, {r})", "This tile is empty.")
        else:
            self.hovered_info = ("Out of bounds", "You are hovering outside of the grid.")