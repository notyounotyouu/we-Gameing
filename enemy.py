"""Enemy types and AI."""

import random
from dataclasses import dataclass, field
from typing import Callable


class Enemy:
    def __init__(
        self,
        name: str,
        hp: int,
        attack: int,
        defense: int,
        speed: int,
        xp_reward: int,
        gold_reward: int,
        level: int = 1,
    ) -> None:
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.magic_attack = attack  # simple default
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.level = level

        # Status flags (same interface as Character)
        self.stunned: bool = False
        self.evading: bool = False

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def choose_action(self, target) -> str:
        """Simple AI: random choice between attack and a special move."""
        roll = random.random()
        if roll < 0.65:
            return self._basic_attack(target)
        return self._special_action(target)

    def _basic_attack(self, target) -> str:
        if target.evading and random.random() < 0.75:
            target.evading = False
            return f"{self.name} attacks but {target.name} evades!"
        dmg = max(1, self.attack - target.defense // 2 + random.randint(-2, 3))
        target.hp -= dmg
        return f"{self.name} attacks {target.name} for {dmg} damage."

    def _special_action(self, target) -> str:
        """Override in subclasses for unique specials; default is a strong hit."""
        dmg = max(1, int(self.attack * 1.4) - target.defense // 3)
        target.hp -= dmg
        return f"{self.name} uses a powerful attack on {target.name} for {dmg} damage!"

    def status_line(self) -> str:
        bar_len = 20
        filled = int(bar_len * self.hp / self.max_hp)
        bar = "█" * filled + "░" * (bar_len - filled)
        return f"{self.name} [Lv.{self.level}]  HP: [{bar}] {self.hp}/{self.max_hp}"


# ---------------------------------------------------------------------------
# Concrete enemy types
# ---------------------------------------------------------------------------

class Goblin(Enemy):
    def __init__(self, level: int = 1) -> None:
        scale = 1 + (level - 1) * 0.2
        super().__init__(
            name="Goblin",
            hp=int(30 * scale),
            attack=int(8 * scale),
            defense=int(3 * scale),
            speed=12,
            xp_reward=int(30 * scale),
            gold_reward=random.randint(5, 15),
            level=level,
        )

    def _special_action(self, target) -> str:
        # Quick double hit
        dmg1 = max(1, self.attack - target.defense // 2)
        dmg2 = max(1, self.attack // 2 - target.defense // 3)
        target.hp -= dmg1 + dmg2
        return (
            f"{self.name} strikes twice: {dmg1} + {dmg2} = "
            f"{dmg1 + dmg2} total damage!"
        )


class Orc(Enemy):
    def __init__(self, level: int = 1) -> None:
        scale = 1 + (level - 1) * 0.2
        super().__init__(
            name="Orc",
            hp=int(60 * scale),
            attack=int(14 * scale),
            defense=int(8 * scale),
            speed=6,
            xp_reward=int(55 * scale),
            gold_reward=random.randint(10, 25),
            level=level,
        )

    def _special_action(self, target) -> str:
        dmg = max(1, int(self.attack * 1.8) - target.defense // 2)
        target.hp -= dmg
        return f"{self.name} RAGES and smashes {target.name} for {dmg} damage!"


class Troll(Enemy):
    def __init__(self, level: int = 1) -> None:
        scale = 1 + (level - 1) * 0.2
        super().__init__(
            name="Troll",
            hp=int(90 * scale),
            attack=int(12 * scale),
            defense=int(10 * scale),
            speed=4,
            xp_reward=int(80 * scale),
            gold_reward=random.randint(15, 35),
            level=level,
        )

    def choose_action(self, target) -> str:
        # Trolls regenerate 5 HP every other turn
        if random.random() < 0.3:
            heal = min(8, self.max_hp - self.hp)
            self.hp += heal
            return f"{self.name} regenerates {heal} HP! (HP: {self.hp}/{self.max_hp})"
        return super().choose_action(target)


class DarkKnight(Enemy):
    def __init__(self, level: int = 1) -> None:
        scale = 1 + (level - 1) * 0.2
        super().__init__(
            name="Dark Knight",
            hp=int(75 * scale),
            attack=int(16 * scale),
            defense=int(14 * scale),
            speed=9,
            xp_reward=int(100 * scale),
            gold_reward=random.randint(20, 45),
            level=level,
        )

    def _special_action(self, target) -> str:
        dmg = max(1, int(self.attack * 1.6) - target.defense // 4)
        target.hp -= dmg
        return (
            f"{self.name} channels dark energy and strikes {target.name} "
            f"for {dmg} shadow damage!"
        )


class Dragon(Enemy):
    """Boss enemy."""

    def __init__(self, level: int = 1) -> None:
        scale = 1 + (level - 1) * 0.3
        super().__init__(
            name="Dragon",
            hp=int(200 * scale),
            attack=int(22 * scale),
            defense=int(15 * scale),
            speed=10,
            xp_reward=int(250 * scale),
            gold_reward=random.randint(60, 120),
            level=level,
        )
        self._breath_cooldown = 0

    def choose_action(self, target) -> str:
        self._breath_cooldown -= 1
        if self._breath_cooldown <= 0 and random.random() < 0.4:
            self._breath_cooldown = 2
            dmg = max(1, int(self.attack * 2) - target.defense // 4)
            target.hp -= dmg
            return (
                f"The {self.name} BREATHES FIRE engulfing {target.name} "
                f"for {dmg} fire damage!"
            )
        return super().choose_action(target)


# ---------------------------------------------------------------------------
# Enemy pool by dungeon floor
# ---------------------------------------------------------------------------

def enemies_for_floor(floor: int) -> list[type]:
    """Return a weighted pool of enemy classes appropriate for the floor."""
    if floor <= 2:
        return [Goblin, Goblin, Goblin, Orc]
    if floor <= 4:
        return [Goblin, Orc, Orc, Troll]
    if floor <= 6:
        return [Orc, Troll, DarkKnight]
    return [Troll, DarkKnight, Dragon]


def random_enemy(floor: int) -> Enemy:
    pool = enemies_for_floor(floor)
    cls = random.choice(pool)
    enemy_level = max(1, floor // 2 + 1)
    return cls(level=enemy_level)


def boss_for_floor(floor: int) -> Enemy:
    """Return a boss enemy scaled to the floor."""
    level = max(1, floor)
    return Dragon(level=level)
