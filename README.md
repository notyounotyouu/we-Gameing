# haha-fun-DnD-ish

A generic turn-based RPG written in Python.

## How to Play

Requires **Python 3.10+** (no external dependencies).

```bash
python game.py
```

## Features

| Feature | Details |
|---|---|
| **Character classes** | Warrior · Mage · Rogue, each with unique stats and skills |
| **Turn-based combat** | Attack, use Skills, use Items, or Flee |
| **Skills** | Heavy Strike, Shield Bash (Warrior) · Fireball, Ice Shard (Mage) · Backstab, Smoke Bomb (Rogue) |
| **Enemies** | Goblin · Orc · Troll · Dark Knight · Dragon (boss) |
| **Items** | Health Potion · Great Health Potion · Mana Potion · Elixir |
| **Merchant & Campfire** | Buy items or rest between floors |
| **Progression** | Gain XP, level up, stats increase automatically |
| **Dungeon** | 6 floors, each with 3 random encounters + a boss |

## Game Structure

```
game.py      — main loop (character creation, floors, shop, game over)
character.py — player character, stats, skills, leveling
enemy.py     — enemy types and AI
combat.py    — turn-based combat engine
items.py     — item definitions and inventory
```
