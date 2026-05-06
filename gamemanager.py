import menu
import menus
import attack
import effect
import character
import player
import item
import arcade
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
        #replace state with state stack
        self.state = "idle"   # or "player_turn", "menu"
        self.active_character = None

        self.pending_attack = None
        self.moves_taken = 0

        self.hovered_tile = None

        self.turn_queue = []

        self.characters.append(character.Character("john", 100, self.grid.tiles[(0, 0)], 3, 10, self.players["Player"], attacks=[
            attack.Attack("Slash", 20, 25, cooldown=2),
            attack.Attack("Fireball", 30, 35, cooldown=3, effects=[effect.Effect("Burn", activations=5, interval=1, on_tick=lambda c: c.take_damage(5))])
        ]))
        self.characters.append(character.Character("lisa", 100, self.grid.tiles[(1, 0)], 4, 10, self.players["Player"], attacks=[
            attack.Attack("Stomp", 25, 30, cooldown=2)
        ]))
        self.characters.append(character.Character("duck", 100, self.grid.tiles[(1, 1)], 5, 10, self.players["Player"], attacks=[
            attack.Attack("Heal", 30, 35, cooldown=3)
        ]))
        self.start_turn_cycle()


    def confirm_equip_item(self, character, item):
        print(f"Confirming equip of {item.name} for {character.name}")
        self.state_stack.append("confirm equip")
        self.push_menu(menu.Menu(self, item.name.upper(), [("Cancel", lambda: self.pop_menu()), ("Equip", lambda: character.equip_item(item))]))

    def confirm_unequip_item(self, character, item):
        print(f"Confirming unequip of {item.name} for {character.name}")
        self.state_stack.append("confirm unequip")
        self.push_menu(menu.Menu(self, item.name.upper(), [("Cancel", lambda: self.pop_menu()), ("Unequip", lambda: character.unequip_item(item))]))

    def start_move(self, character):
        self.state_stack.append("select tile for move")
        self.push_menu(menu.Menu(self, "MOVE", [("Cancel", lambda: self.pop_menu())]))
    
    def execute_attack(self, attack):
        self.pending_attack = attack
        self.state_stack.append("choose attack target")
        self.push_menu(menu.Menu(self, self.pending_attack.name.upper(), [("Cancel", lambda: self.pop_menu())]))
        #show attack range on grid

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
            self.run_ai(character)
            self.end_turn()

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

            if tile and tile.character:
                self.active_character.attack_target(tile.character, self.pending_attack)
                self.pending_attack = None
                self.pop_menu()
                self.end_turn()

    def on_mouse_motion(self, x, y, dx, dy):
        q, r = self.grid.pixel_to_hex(x, y)
        tile = self.grid.tiles.get((q, r))

        option_index = self.current_menu.get_option_index_at(x, y)
        if option_index is not None:
            self.current_menu.selected_index = option_index
        else:
            self.current_menu.selected_index = None
            
    def on_key_press(self, key):
        pass