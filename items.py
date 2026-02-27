"""Items and inventory for the RPG."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Item:
    name: str
    description: str
    hp_restore: int = 0
    mp_restore: int = 0
    price: int = 0

    def use(self, target) -> str:
        msgs = []
        if self.hp_restore:
            healed = min(self.hp_restore, target.max_hp - target.hp)
            target.hp += healed
            msgs.append(f"{target.name} restored {healed} HP.")
        if self.mp_restore:
            restored = min(self.mp_restore, target.max_mp - target.mp)
            target.mp += restored
            msgs.append(f"{target.name} restored {restored} MP.")
        return " ".join(msgs) if msgs else "Nothing happened."

    def __str__(self) -> str:
        parts = [self.name, f"({self.description})"]
        if self.hp_restore:
            parts.append(f"+{self.hp_restore} HP")
        if self.mp_restore:
            parts.append(f"+{self.mp_restore} MP")
        return " ".join(parts)


# Pre-defined item catalogue
HEALTH_POTION = Item(
    name="Health Potion",
    description="Restores 50 HP",
    hp_restore=50,
    price=30,
)
GREAT_HEALTH_POTION = Item(
    name="Great Health Potion",
    description="Restores 120 HP",
    hp_restore=120,
    price=70,
)
MANA_POTION = Item(
    name="Mana Potion",
    description="Restores 30 MP",
    mp_restore=30,
    price=25,
)
ELIXIR = Item(
    name="Elixir",
    description="Restores 80 HP and 50 MP",
    hp_restore=80,
    mp_restore=50,
    price=100,
)

SHOP_INVENTORY: list[Item] = [
    HEALTH_POTION,
    GREAT_HEALTH_POTION,
    MANA_POTION,
    ELIXIR,
]


class Inventory:
    def __init__(self) -> None:
        self._items: list[Item] = []
        self.gold: int = 50  # starting gold

    def add(self, item: Item, qty: int = 1) -> None:
        for _ in range(qty):
            self._items.append(item)

    def remove(self, item: Item) -> bool:
        for i, it in enumerate(self._items):
            if it.name == item.name:
                self._items.pop(i)
                return True
        return False

    def count(self, item: Item) -> int:
        return sum(1 for it in self._items if it.name == item.name)

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def unique_items(self) -> list[tuple[Item, int]]:
        seen: dict[str, tuple[Item, int]] = {}
        for item in self._items:
            if item.name in seen:
                seen[item.name] = (item, seen[item.name][1] + 1)
            else:
                seen[item.name] = (item, 1)
        return list(seen.values())

    def __str__(self) -> str:
        if self.is_empty():
            return "  (empty)"
        lines = []
        for item, qty in self.unique_items():
            lines.append(f"  {item.name} x{qty} — {item.description}")
        lines.append(f"  Gold: {self.gold}")
        return "\n".join(lines)
