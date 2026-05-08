import menu

def show_actions_menu(game, character):
    actions_menu = menu.Menu(game, "ACTIONS", [
        ("Move", lambda: game.start_move(), "Move to a different tile."),
        ("Attack", lambda: show_attacks_menu(game, character), "Use an attack."),
        ("Inventory", lambda: show_inventory_menu(game, character), "Access your inventory."),
        ("Abilities", lambda: show_abilities_menu(game, character), "Use an ability.")
    ])
    game.state_stack.append("actions menu")
    game.push_menu(actions_menu)
# --------------------------------------------------------------------------------------------------
def show_attacks_menu(game, character):
    attacks_menu = menu.Menu(
    game,
    "ATTACKS",
    [
        ("Back", lambda: game.pop_menu(), "Go back to the previous menu."),
    ] + [
        (attack.name, lambda a=attack: game.execute_attack(a), attack.description)
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
        ("Back", lambda: game.pop_menu(), "Go back to the previous menu."),
    ] 
    )
    if character.abilities:
        for ability in character.abilities:
            abilities_menu.options.append((ability.name, lambda a=ability: execute_ability(game, a, character), ability.description))
    game.state_stack.append("abilities menu")
    game.push_menu(abilities_menu)

def execute_ability(game, ability, character):
    def use_ability(game, ability, character):
        character.use_ability(ability)
        game.end_turn()
    game.state_stack.append("confirm use ability")
    game.push_menu(menu.Menu(
        game,
        ability.name,
        [
            ("Back", lambda: game.pop_menu(), "Go back to the previous menu."),
            ("Use", lambda: use_ability(game, ability, character), "Use ability.")
        ] 
    ))
# --------------------------------------------------------------------------------------------------
def show_inventory_menu(game, character):
    inventory_menu = menu.Menu(
        game,
        "INVENTORY",
        [
            ("Back", lambda: game.pop_menu(), "Go back to the previous menu."),
            ("Equip Item", lambda: show_equip_menu(game, character), "Equip items to this character."),
            ("Unequip Item", lambda: show_unequip_menu(game, character), "Unquip items from this character.")
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
            ("Back", lambda: game.pop_menu(), "Go back to the previous menu."),
        ] 
    )
    if character.owner.items:
        for item in character.owner.items:
            equip_menu.options.append((item.name, lambda i=item: confirm_equip_item(game, character, i), item.description))

    game.state_stack.append("equip menu")
    game.push_menu(equip_menu)

def confirm_equip_item(game, character, item):
    game.state_stack.append("confirm equip")
    def equip():
        character.equip_item(item)
        game.pop_menu()
        game.pop_menu()
    game.push_menu(menu.Menu(game, item.name.upper(), [("Cancel", lambda: game.pop_menu(), "Go back to the previous menu."), ("Equip", lambda: equip(), "Equip this item.")]))

def show_unequip_menu(game, character):
    unequip_menu = menu.Menu(
        game,
        "UNEQUIP ITEM",
        [
            ("Back", lambda: game.pop_menu(), "Go back to the previous menu."),
        ] 
    )
    if character.items:
        for item in character.items:
            unequip_menu.options.append((item.name, lambda i=item: confirm_unequip_item(game, character, i), item.description))
            
    game.state_stack.append("unequip menu")
    game.push_menu(unequip_menu)

def confirm_unequip_item(game, character, item):
    print(f"Confirming unequip of {item.name} for {character.name}")
    game.state_stack.append("confirm unequip")
    def unequip():
        character.unequip_item(item)
        game.pop_menu()
        game.pop_menu()
    game.push_menu(menu.Menu(game, item.name.upper(), [("Cancel", lambda: game.pop_menu(), "Go back to the previous menu."), ("Unequip", lambda: unequip(), "Unequip this item.")]))