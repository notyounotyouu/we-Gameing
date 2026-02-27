"""Turn-based combat engine."""

import random
from character import Character
from enemy import Enemy
from items import Item


def _divider(char: str = "-", width: int = 50) -> str:
    return char * width


def run_combat(player: Character, enemy: Enemy) -> str:
    """
    Execute a full combat encounter.

    Returns:
        "win"  — player defeated the enemy
        "lose" — player was defeated
        "flee" — player successfully fled
    """
    print(f"\n{'=' * 50}")
    print(f"  ⚔  A {enemy.name} appears! (Level {enemy.level})")
    print(f"{'=' * 50}")

    turn = 0
    while player.is_alive and enemy.is_alive:
        turn += 1
        print(f"\n--- Turn {turn} ---")
        print(enemy.status_line())
        print(player.status_line())
        print()

        # Reset per-turn flags
        enemy.stunned = False

        # --- Player phase ---
        action = _player_menu(player, enemy)
        if action == "flee":
            flee_chance = 0.4 + (player.speed - enemy.speed) * 0.04
            if random.random() < flee_chance:
                print(f"\n{player.name} successfully flees!")
                return "flee"
            print(f"\n{player.name} tried to flee but couldn't escape!")
            if not enemy.is_alive:
                break

        # --- Enemy phase (skip if stunned) ---
        if enemy.stunned:
            print(f"\n{enemy.name} is stunned and skips their turn!")
        else:
            result = enemy.choose_action(player)
            print(f"\n  > {result}")

        # Clear evasion flag after the enemy acted
        player.evading = False

    if player.is_alive:
        return "win"
    return "lose"


def _player_menu(player: Character, enemy: Enemy) -> str:
    """Display the combat menu and return the chosen action key."""
    while True:
        print("Your turn — choose an action:")
        print("  [1] Attack")
        print("  [2] Skills")
        print("  [3] Items")
        print("  [4] Flee")
        choice = input("  > ").strip()

        if choice == "1":
            msg = player.basic_attack(enemy)
            print(f"\n  > {msg}")
            return "attack"

        if choice == "2":
            result = _skill_menu(player, enemy)
            if result:
                return "skill"

        elif choice == "3":
            result = _item_menu(player)
            if result:
                return "item"

        elif choice == "4":
            return "flee"
        else:
            print("  Invalid choice — please enter 1, 2, 3, or 4.")


def _skill_menu(player: Character, enemy: Enemy) -> bool:
    """Show skill submenu. Returns True if a skill was used."""
    skills = player.skills
    print("\n  --- Skills ---")
    for i, sk in enumerate(skills, 1):
        marker = "  " if player.mp >= sk.mp_cost else "✗ "
        print(f"  [{i}] {marker}{sk.name}: {sk.description}  (MP:{sk.mp_cost})")
    print(f"  [0] Back   (MP: {player.mp}/{player.max_mp})")

    choice = input("  > ").strip()
    if choice == "0":
        return False
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(skills):
            msg = skills[idx].use(player, enemy)
            print(f"\n  > {msg}")
            return True
    print("  Invalid selection.")
    return False


def _item_menu(player: Character) -> bool:
    """Show item submenu. Returns True if an item was used."""
    items = player.inventory.unique_items()
    print("\n  --- Items ---")
    if not items:
        print("  (no items)")
        return False
    for i, (item, qty) in enumerate(items, 1):
        print(f"  [{i}] {item.name} x{qty}  — {item.description}")
    print("  [0] Back")

    choice = input("  > ").strip()
    if choice == "0":
        return False
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(items):
            item, _ = items[idx]
            msg = player.use_item(item)
            print(f"\n  > {msg}")
            return True
    print("  Invalid selection.")
    return False


def award_loot(player: Character, enemy: Enemy) -> None:
    """Grant XP and gold after a victory."""
    print(f"\n{_divider()}")
    print(f"  Victory! {enemy.name} defeated.")
    msgs = player.gain_xp(enemy.xp_reward)
    for m in msgs:
        print(f"  {m}")
    player.inventory.gold += enemy.gold_reward
    print(f"  Gained {enemy.gold_reward} gold.  (Total: {player.inventory.gold})")
    print(_divider())
