"""Player character classes and skills."""

import random
from dataclasses import dataclass, field
from typing import Callable, Optional

from items import Inventory, Item


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

@dataclass
class Skill:
    name: str
    description: str
    mp_cost: int
    effect: Callable  # effect(user, target) -> str

    def use(self, user, target) -> str:
        if user.mp < self.mp_cost:
            return f"Not enough MP to use {self.name}!"
        user.mp -= self.mp_cost
        return self.effect(user, target)


def _heavy_strike(user, target) -> str:
    dmg = max(1, user.attack * 2 - target.defense // 2)
    target.hp -= dmg
    return f"{user.name} delivers a Heavy Strike for {dmg} damage!"


def _shield_bash(user, target) -> str:
    dmg = max(1, user.attack - target.defense)
    stun = random.random() < 0.4
    target.hp -= dmg
    msg = f"{user.name} bashes with their shield for {dmg} damage!"
    if stun:
        target.stunned = True
        msg += " The enemy is stunned!"
    return msg


def _fireball(user, target) -> str:
    dmg = max(1, user.magic_attack * 3 - target.defense // 3)
    target.hp -= dmg
    return f"{user.name} hurls a Fireball for {dmg} magic damage!"


def _ice_shard(user, target) -> str:
    dmg = max(1, user.magic_attack * 2 - target.defense // 4)
    target.hp -= dmg
    slow = random.random() < 0.5
    msg = f"{user.name} fires an Ice Shard for {dmg} magic damage!"
    if slow:
        target.speed = max(1, target.speed - 3)
        msg += " The enemy is slowed!"
    return msg


def _backstab(user, target) -> str:
    crit = random.random() < 0.6
    dmg = max(1, user.attack * 2 - target.defense // 2)
    if crit:
        dmg = int(dmg * 1.5)
        msg = f"{user.name} backstabs for a CRITICAL {dmg} damage!"
    else:
        msg = f"{user.name} backstabs for {dmg} damage!"
    target.hp -= dmg
    return msg


def _smoke_bomb(user, target) -> str:
    user.evading = True
    return f"{user.name} throws a smoke bomb and prepares to evade!"


# Skill catalogues per class
WARRIOR_SKILLS = [
    Skill("Heavy Strike", "A powerful melee attack (2x ATK)", 10, _heavy_strike),
    Skill("Shield Bash", "Bash the enemy; 40% chance to stun", 8, _shield_bash),
]

MAGE_SKILLS = [
    Skill("Fireball", "Devastating fire magic (3x M.ATK)", 15, _fireball),
    Skill("Ice Shard", "Ice magic; 50% chance to slow enemy", 10, _ice_shard),
]

ROGUE_SKILLS = [
    Skill("Backstab", "High-damage attack; 60% critical chance", 10, _backstab),
    Skill("Smoke Bomb", "Next enemy attack has 75% chance to miss", 8, _smoke_bomb),
]


# ---------------------------------------------------------------------------
# Character classes
# ---------------------------------------------------------------------------

CLASS_TEMPLATES = {
    "Warrior": {
        "hp": 120, "mp": 30,
        "attack": 18, "defense": 12, "speed": 8,
        "magic_attack": 4,
        "skills": WARRIOR_SKILLS,
        "description": "A tough melee fighter with high HP and defense.",
    },
    "Mage": {
        "hp": 70, "mp": 80,
        "attack": 7, "defense": 5, "speed": 10,
        "magic_attack": 22,
        "skills": MAGE_SKILLS,
        "description": "A fragile but powerful spellcaster.",
    },
    "Rogue": {
        "hp": 90, "mp": 50,
        "attack": 15, "defense": 8, "speed": 16,
        "magic_attack": 6,
        "skills": ROGUE_SKILLS,
        "description": "A swift trickster who excels at critical strikes.",
    },
}


class Character:
    """Player-controlled character."""

    XP_PER_LEVEL = 100

    def __init__(self, name: str, class_name: str) -> None:
        template = CLASS_TEMPLATES[class_name]
        self.name = name
        self.class_name = class_name
        self.level = 1
        self.xp = 0

        self.max_hp: int = template["hp"]
        self.hp: int = self.max_hp
        self.max_mp: int = template["mp"]
        self.mp: int = self.max_mp

        self.attack: int = template["attack"]
        self.defense: int = template["defense"]
        self.speed: int = template["speed"]
        self.magic_attack: int = template["magic_attack"]

        self.skills: list[Skill] = template["skills"]
        self.inventory: Inventory = Inventory()

        # Status flags
        self.stunned: bool = False
        self.evading: bool = False

        # Give one starter potion
        from items import HEALTH_POTION
        self.inventory.add(HEALTH_POTION)

    # ------------------------------------------------------------------
    # Combat helpers
    # ------------------------------------------------------------------

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def basic_attack(self, target) -> str:
        dmg = max(1, self.attack - target.defense // 2 + random.randint(-2, 3))
        crit = random.random() < 0.1
        if crit:
            dmg = int(dmg * 1.5)
            target.hp -= dmg
            return f"{self.name} attacks {target.name} for a CRITICAL {dmg} damage!"
        target.hp -= dmg
        return f"{self.name} attacks {target.name} for {dmg} damage."

    def use_item(self, item: Item) -> str:
        if not self.inventory.remove(item):
            return f"You don't have {item.name}."
        return item.use(self)

    # ------------------------------------------------------------------
    # Progression
    # ------------------------------------------------------------------

    def gain_xp(self, amount: int) -> list[str]:
        msgs = []
        self.xp += amount
        msgs.append(f"{self.name} gained {amount} XP.")
        while self.xp >= self.XP_PER_LEVEL * self.level:
            self.xp -= self.XP_PER_LEVEL * self.level
            self._level_up()
            msgs.append(
                f"*** {self.name} leveled up to LEVEL {self.level}! ***"
            )
        return msgs

    def _level_up(self) -> None:
        self.level += 1
        self.max_hp += 15
        self.hp = self.max_hp
        self.max_mp += 8
        self.mp = self.max_mp
        self.attack += 3
        self.defense += 2
        self.magic_attack += 3
        self.speed += 1

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def status_line(self) -> str:
        return (
            f"{self.name} [{self.class_name} Lv.{self.level}] "
            f"HP:{self.hp}/{self.max_hp}  MP:{self.mp}/{self.max_mp}  "
            f"XP:{self.xp}/{self.XP_PER_LEVEL * self.level}"
        )

    def full_stats(self) -> str:
        lines = [
            f"=== {self.name} ({self.class_name}) ===",
            f"  Level : {self.level}",
            f"  XP    : {self.xp} / {self.XP_PER_LEVEL * self.level}",
            f"  HP    : {self.hp} / {self.max_hp}",
            f"  MP    : {self.mp} / {self.max_mp}",
            f"  ATK   : {self.attack}",
            f"  DEF   : {self.defense}",
            f"  M.ATK : {self.magic_attack}",
            f"  SPD   : {self.speed}",
            "  Skills:",
        ]
        for sk in self.skills:
            lines.append(f"    - {sk.name}: {sk.description} (MP:{sk.mp_cost})")
        lines.append("  Inventory:")
        lines.append(str(self.inventory))
        return "\n".join(lines)
