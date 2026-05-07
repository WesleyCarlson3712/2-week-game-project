import menu

def show_actions_menu(game, character):
    actions_menu = menu.Menu(game, "ACTIONS", [
        ("Move", lambda: game.start_move()),
        ("Attack", lambda: show_attacks_menu(game, character)),
        ("Inventory", lambda: show_inventory_menu(game, character)),
        ("Special", lambda: show_abilities_menu(game, character)),
    ])
    game.state_stack.append("actions menu")
    game.push_menu(actions_menu)
# --------------------------------------------------------------------------------------------------
def show_attacks_menu(game, character):
    attacks_menu = menu.Menu(
    game,
    "ATTACKS",
    [
        ("Back", lambda: game.pop_menu()),
    ] + [
        (attack.name, lambda a=attack: game.execute_attack(a))
        for attack in character.attacks
    ])
    game.state_stack.append("choose attack")
    game.push_menu(attacks_menu)
# --------------------------------------------------------------------------------------------------
def show_abilities_menu(game, character):
    abilities_menu = menu.Menu(
    game,
    "ABILITIES",
    [
        ("Back", lambda: game.pop_menu()),
    ] 
    )
    if character.abilities:
        for ability in character.abilities:
            abilities_menu.options.append((ability.name, lambda a=ability: execute_ability(a)))
    game.state_stack.append("abilities menu")
    game.push_menu(abilities_menu)

    def execute_ability(game, ability):
        game.state_stack.append("confirm equip")
        game.push_menu(menu.Menu(
            game,
            ability.name,
            [
                ("Back", lambda: game.pop_menu()),
                ("Use", lambda: game.active_character.use_ability(ability))
            ] 
        ))
# --------------------------------------------------------------------------------------------------
def show_inventory_menu(game, character):
    inventory_menu = menu.Menu(
        game,
        "INVENTORY",
        [
            ("Back", lambda: game.pop_menu()),
            ("Equip Item", lambda: show_equip_menu(game, character)),
            ("Unequip Item", lambda: show_unequip_menu(game, character))
        ] 
    )
    print(character.owner.items)
    game.state_stack.append("inventory menu")
    game.push_menu(inventory_menu)

def show_equip_menu(game, character):
    equip_menu = menu.Menu(
        game,
        "EQUIP ITEM",
        [
            ("Back", lambda: game.pop_menu()),
        ] 
    )
    if character.owner.items:
        for item in character.owner.items:
            equip_menu.options.append((item.name, lambda i=item: game.confirm_equip_item(character, i)))

    game.state_stack.append("equip menu")
    game.push_menu(equip_menu)

def confirm_equip_item(self, character, item):
    print(f"Confirming equip of {item.name} for {character.name}")
    self.state_stack.append("confirm equip")
    def equip():
        character.equip_item(item)
        self.pop_menu()
        self.pop_menu()
    self.push_menu(menu.Menu(self, item.name.upper(), [("Cancel", lambda: self.pop_menu()), ("Equip", lambda: equip())]))

def show_unequip_menu(game, character):
    unequip_menu = menu.Menu(
        game,
        "UNEQUIP ITEM",
        [
            ("Back", lambda: game.pop_menu()),
        ] 
    )
    if character.items:
        for item in character.items:
            unequip_menu.options.append((item.name, lambda i=item: game.confirm_unequip_item(character, i)))
            
    game.state_stack.append("unequip menu")
    game.push_menu(unequip_menu)

def confirm_unequip_item(self, character, item):
    print(f"Confirming unequip of {item.name} for {character.name}")
    self.state_stack.append("confirm unequip")
    def unequip():
        character.unequip_item(item)
        self.pop_menu()
        self.pop_menu()
    self.push_menu(menu.Menu(self, item.name.upper(), [("Cancel", lambda: self.pop_menu()), ("Unequip", lambda: unequip())]))