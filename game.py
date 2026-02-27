"""Main game loop for the generic turn-based RPG."""

import sys
from character import Character, CLASS_TEMPLATES
from enemy import random_enemy, boss_for_floor
from combat import run_combat, award_loot
from items import SHOP_INVENTORY, Item


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BANNER = r"""
  ____  _   _ ____     _____ _   _ ____  _   _ ____  _
 |  _ \| \ | |  _ \   |_   _| | | |  _ \| \ | / ___|| |
 | | | |  \| | | | |    | | | | | | |_) |  \| \___ \| |
 | |_| | |\  | |_| |    | | | |_| |  _ <| |\  |___) |_|
 |____/|_| \_|____/     |_|  \___/|_| \_\_| \_|____/(_)

       A Generic Turn-Based RPG
"""

FLOOR_ENCOUNTERS = 3   # regular battles before the boss
TOTAL_FLOORS = 6


def _divider(char: str = "=", width: int = 50) -> str:
    return char * width


def _prompt(msg: str, options: list[str]) -> str:
    """Keep asking until a valid option is given."""
    while True:
        ans = input(f"{msg} [{'/'.join(options)}]: ").strip().lower()
        if ans in [o.lower() for o in options]:
            return ans
        print(f"  Please choose one of: {', '.join(options)}")


def _pause() -> None:
    input("\n  [Press Enter to continue] ")


# ---------------------------------------------------------------------------
# Game sections
# ---------------------------------------------------------------------------

def show_title() -> None:
    print(BANNER)
    print(_divider())


def create_character() -> Character:
    print("\n=== Create Your Character ===\n")
    name = input("Enter your hero's name: ").strip()
    if not name:
        name = "Hero"

    print("\nChoose your class:")
    classes = list(CLASS_TEMPLATES.keys())
    for i, cls_name in enumerate(classes, 1):
        tmpl = CLASS_TEMPLATES[cls_name]
        print(f"  [{i}] {cls_name} — {tmpl['description']}")

    while True:
        choice = input("  > ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(classes):
            class_name = classes[int(choice) - 1]
            break
        print(f"  Enter a number between 1 and {len(classes)}.")

    player = Character(name, class_name)
    print(f"\nWelcome, {player.name} the {player.class_name}!")
    print(player.full_stats())
    _pause()
    return player


def shop(player: Character) -> None:
    print("\n=== Wandering Merchant ===")
    print(f"  Your gold: {player.inventory.gold}")
    print()

    while True:
        print("Available items:")
        for i, item in enumerate(SHOP_INVENTORY, 1):
            print(f"  [{i}] {item.name:25s} — {item.description:25s}  Cost: {item.price}g")
        print("  [0] Leave shop")

        choice = input("  > ").strip()
        if choice == "0":
            break
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(SHOP_INVENTORY):
                item = SHOP_INVENTORY[idx]
                if player.inventory.gold >= item.price:
                    player.inventory.gold -= item.price
                    player.inventory.add(item)
                    print(f"  Bought {item.name}! (Gold left: {player.inventory.gold})")
                else:
                    print("  Not enough gold!")
                continue
        print("  Invalid choice.")


def rest(player: Character) -> None:
    print("\n=== Campfire ===")
    hp_restore = player.max_hp // 3
    mp_restore = player.max_mp // 3
    player.hp = min(player.max_hp, player.hp + hp_restore)
    player.mp = min(player.max_mp, player.mp + mp_restore)
    print(f"  You rest by the fire. Restored {hp_restore} HP and {mp_restore} MP.")
    print(f"  HP: {player.hp}/{player.max_hp}  MP: {player.mp}/{player.max_mp}")
    _pause()


def floor_intro(floor: int) -> None:
    print(f"\n{'#' * 50}")
    if floor % TOTAL_FLOORS == 0:
        print(f"  *** BOSS FLOOR {floor} ***")
    else:
        print(f"  === Dungeon Floor {floor} ===")
    print(f"{'#' * 50}\n")
    _pause()


def run_floor(player: Character, floor: int) -> bool:
    """
    Run all encounters on a dungeon floor.
    Returns True if the player survived, False otherwise.
    """
    floor_intro(floor)

    # Regular encounters
    for encounter in range(1, FLOOR_ENCOUNTERS + 1):
        print(f"\n  [Encounter {encounter}/{FLOOR_ENCOUNTERS}]")
        enemy = random_enemy(floor)
        result = run_combat(player, enemy)

        if result == "win":
            award_loot(player, enemy)
            _pause()
        elif result == "flee":
            print("  You managed to escape...")
            _pause()
        else:  # lose
            print(f"\n  {player.name} has been defeated...")
            return False

    # Optional rest/shop between floors
    print("\nAfter battling through the floor you find a crossroads.")
    print("  [1] Visit the Merchant")
    print("  [2] Rest at the campfire")
    print("  [3] Press on immediately")
    choice = input("  > ").strip()
    if choice == "1":
        shop(player)
    elif choice == "2":
        rest(player)

    # Boss encounter
    print(f"\n  A powerful guardian blocks the exit to Floor {floor + 1}!")
    boss = boss_for_floor(floor)
    result = run_combat(player, boss)
    if result == "win":
        award_loot(player, boss)
        _pause()
        return True
    elif result == "flee":
        print("  You fled from the boss! Trying to press forward anyway...")
        # Fleeing from a boss costs HP
        cost = player.max_hp // 5
        player.hp = max(1, player.hp - cost)
        print(f"  You take {cost} damage fleeing. HP: {player.hp}/{player.max_hp}")
        _pause()
        return True
    else:
        return False


def game_over(player: Character) -> None:
    print("\n" + _divider("*"))
    print("  G A M E   O V E R")
    print(_divider("*"))
    print(f"\n  {player.name} the {player.class_name} fell in battle at Level {player.level}.")
    print(f"  Better luck next time, adventurer!")


def victory() -> None:
    print("\n" + _divider("*"))
    print("  *** CONGRATULATIONS — YOU WIN! ***")
    print(_divider("*"))
    print("\n  You have conquered the dungeon and defeated every guardian.")
    print("  Your legend will be sung for ages!")


def main() -> None:
    show_title()
    player = create_character()

    for floor in range(1, TOTAL_FLOORS + 1):
        survived = run_floor(player, floor)
        if not survived:
            game_over(player)
            sys.exit(0)
        if floor < TOTAL_FLOORS:
            print(f"\n  You descend to floor {floor + 1}...")
            print(player.status_line())
            _pause()

    victory()


if __name__ == "__main__":
    main()
