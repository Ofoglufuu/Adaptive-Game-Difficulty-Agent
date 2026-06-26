"""
Game simulation logic for a single round.
"""
import random
from dataclasses import dataclass
from typing import Optional

from src.player import PlayerProfile

@dataclass
class GameRoundResult:
    """
    Data class representing the outcome of a single simulated game round.
    """
    victory: bool
    remaining_health: int
    damage_taken: int
    accuracy: float
    round_duration: float
    difficulty_level: int
    enemy_count: int
    enemy_damage: int
    health_pack_rate: float

def simulate_round(
    player: PlayerProfile,
    difficulty_level: int,
    enemy_count: int,
    enemy_damage: int,
    health_pack_rate: float,
    seed: Optional[int] = None
) -> GameRoundResult:
    """
    Simulates a single game round based on player profile and difficulty parameters.
    """
    if not (1 <= difficulty_level <= 10):
        raise ValueError(f"difficulty_level must be between 1 and 10. Got {difficulty_level}")
    if enemy_count <= 0:
        raise ValueError(f"enemy_count must be > 0. Got {enemy_count}")
    if enemy_damage <= 0:
        raise ValueError(f"enemy_damage must be > 0. Got {enemy_damage}")
    if not (0.0 <= health_pack_rate <= 1.0):
        raise ValueError(f"health_pack_rate must be between 0.0 and 1.0. Got {health_pack_rate}")

    # Use a local random instance if seed is provided to not alter global state
    rng = random.Random(seed) if seed is not None else random

    # Simple probability model
    base_threat = (enemy_count * enemy_damage) / 100.0
    player_strength = player.skill_level * 0.7 + player.survival_factor * 0.3
    health_advantage = health_pack_rate * 0.5
    
    # Win probability logic
    win_probability = player_strength + health_advantage - (base_threat * 0.3)
    win_probability = max(0.05, min(0.95, win_probability))
    
    victory = rng.random() < win_probability
    
    # Plausible remaining health and damage based on outcome
    if victory:
        # Player wins with some health left
        remaining_health = int(rng.uniform(10, 100) * player.survival_factor)
        remaining_health = max(1, min(100, remaining_health))
        damage_taken = 100 - remaining_health + int(health_pack_rate * rng.uniform(0, 50))
    else:
        # Player loses, meaning 0 health
        remaining_health = 0
        damage_taken = 100 + int(health_pack_rate * rng.uniform(0, 50))
        
    damage_taken = min(100, damage_taken)
    
    # Accuracy variance
    acc_variance = rng.uniform(-0.1, 0.1)
    round_accuracy = max(0.0, min(1.0, player.accuracy + acc_variance))
    
    # Round duration based on enemies
    base_duration = rng.uniform(30.0, 120.0)
    round_duration = base_duration + (enemy_count * 5.0)

    return GameRoundResult(
        victory=victory,
        remaining_health=remaining_health,
        damage_taken=damage_taken,
        accuracy=round_accuracy,
        round_duration=round_duration,
        difficulty_level=difficulty_level,
        enemy_count=enemy_count,
        enemy_damage=enemy_damage,
        health_pack_rate=health_pack_rate
    )

if __name__ == "__main__":
    from src.player import create_default_players
    
    players = create_default_players()
    
    # Example difficulty parameters
    dl, ec, ed, hpr = 5, 10, 10, 0.2
    
    print("--- Testing Player Types (Same Parameters) ---")
    for p in players:
        res = simulate_round(p, dl, ec, ed, hpr)
        print(f"[{p.name}] Victory: {res.victory}, HP: {res.remaining_health}, Acc: {res.accuracy:.2f}")

    print("\n--- Testing Seed Reproducibility ---")
    average_player = players[1]
    res1 = simulate_round(average_player, dl, ec, ed, hpr, seed=42)
    res2 = simulate_round(average_player, dl, ec, ed, hpr, seed=42)
    print(f"Run 1 (Seed 42): Victory={res1.victory}, Duration={res1.round_duration:.2f}, HP={res1.remaining_health}")
    print(f"Run 2 (Seed 42): Victory={res2.victory}, Duration={res2.round_duration:.2f}, HP={res2.remaining_health}")
    
    if res1 == res2:
        print("SUCCESS: Identical results with same seed.")
    else:
        print("FAIL: Results differ despite same seed!")

    print("\n--- Testing Invalid Inputs ---")
    try:
        simulate_round(average_player, difficulty_level=11, enemy_count=10, enemy_damage=10, health_pack_rate=0.2)
        print("FAIL: Expected ValueError for difficulty_level.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")

    try:
        simulate_round(average_player, difficulty_level=5, enemy_count=10, enemy_damage=10, health_pack_rate=1.5)
        print("FAIL: Expected ValueError for health_pack_rate.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")
