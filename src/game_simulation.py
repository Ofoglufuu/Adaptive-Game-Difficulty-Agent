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

    # Use a local random instance if seed is provided
    rng = random.Random(seed) if seed is not None else random

    # Difficulty penalty reduces win chance as difficulty increases (0.0 at Diff 1, 0.45 at Diff 10)
    difficulty_penalty = (difficulty_level - 1) * 0.05

    # Threat score representing the raw danger of enemies
    threat_score = (enemy_count * enemy_damage) / 100.0

    # Combine player attributes into meaningful metrics
    offensive_power = (player.skill_level * 0.6) + (player.accuracy * 0.4)
    defensive_power = (player.reaction_speed * 0.5) + (player.survival_factor * 0.5)

    # Health packs give a direct bonus
    health_bonus = health_pack_rate * 0.4

    # Calculate win probability:
    # Player strengths + health bonus + base chance (0.2) - threat - difficulty penalty
    win_probability = (offensive_power * 0.7) + (defensive_power * 0.3) + health_bonus - (threat_score * 0.15) - difficulty_penalty + 0.2
    
    # Ensure it's between 5% and 95% to maintain a random element
    win_probability = max(0.05, min(0.95, win_probability))
    
    victory = rng.random() < win_probability
    
    # Plausible health and damage calculation
    base_damage = threat_score * 40.0 
    damage_mitigation = (defensive_power + health_pack_rate) * 20.0
    damage_multiplier = 1.0 + (difficulty_level * 0.05)
    
    raw_damage = (base_damage - damage_mitigation) * damage_multiplier + rng.uniform(-10.0, 10.0)
    
    if victory:
        damage_taken = int(max(0, min(99, raw_damage)))
        remaining_health = 100 - damage_taken
    else:
        damage_taken = 100
        remaining_health = 0
    
    # Round accuracy varies around player's base accuracy, negatively affected by difficulty
    acc_variance = rng.uniform(-0.1, 0.1)
    round_accuracy = max(0.0, min(1.0, player.accuracy - (difficulty_level * 0.01) + acc_variance))
    
    # Round duration based on enemies and difficulty, reduced by reaction speed
    base_duration = rng.uniform(30.0, 60.0)
    time_penalty = enemy_count * 2.0 * (1 + difficulty_level * 0.1)
    time_reduction = player.reaction_speed * 20.0
    round_duration = max(10.0, base_duration + time_penalty - time_reduction)

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
    beginner = players[0]
    average = players[1]
    expert = players[2]
    
    ec, ed, hpr = 10, 10, 0.2
    
    print("--- 1. Single Round Difficulty Comparison (Same Player & Seed) ---")
    res_d1 = simulate_round(average, 1, ec, ed, hpr, seed=100)
    res_d5 = simulate_round(average, 5, ec, ed, hpr, seed=100)
    res_d10 = simulate_round(average, 10, ec, ed, hpr, seed=100)
    print(f"Difficulty 1:  Victory={res_d1.victory}, HP={res_d1.remaining_health}, Dmg={res_d1.damage_taken}")
    print(f"Difficulty 5:  Victory={res_d5.victory}, HP={res_d5.remaining_health}, Dmg={res_d5.damage_taken}")
    print(f"Difficulty 10: Victory={res_d10.victory}, HP={res_d10.remaining_health}, Dmg={res_d10.damage_taken}")

    print("\n--- 2. Statistical Test: Difficulty Levels (1000 Rounds) ---")
    def test_win_rate(player, dl, ec, ed, hpr, iterations=1000):
        wins = sum(1 for _ in range(iterations) if simulate_round(player, dl, ec, ed, hpr).victory)
        return (wins / iterations) * 100.0

    print(f"Win Rate (Average Player, Diff 1):  {test_win_rate(average, 1, ec, ed, hpr):.1f}%")
    print(f"Win Rate (Average Player, Diff 5):  {test_win_rate(average, 5, ec, ed, hpr):.1f}%")
    print(f"Win Rate (Average Player, Diff 10): {test_win_rate(average, 10, ec, ed, hpr):.1f}%")

    print("\n--- 3. Statistical Test: Player Profiles (1000 Rounds) ---")
    dl_test = 5
    print(f"Win Rate (Beginner, Diff 5): {test_win_rate(beginner, dl_test, ec, ed, hpr):.1f}%")
    print(f"Win Rate (Average, Diff 5):  {test_win_rate(average, dl_test, ec, ed, hpr):.1f}%")
    print(f"Win Rate (Expert, Diff 5):   {test_win_rate(expert, dl_test, ec, ed, hpr):.1f}%")

    print("\n--- 4. Statistical Test: Health Pack Rate (1000 Rounds) ---")
    print(f"Win Rate (Average, Diff 5, HPR=0.0): {test_win_rate(average, dl_test, ec, ed, 0.0):.1f}%")
    print(f"Win Rate (Average, Diff 5, HPR=0.8): {test_win_rate(average, dl_test, ec, ed, 0.8):.1f}%")

    print("\n--- 5. Seed Reproducibility ---")
    res1 = simulate_round(average, dl_test, ec, ed, hpr, seed=42)
    res2 = simulate_round(average, dl_test, ec, ed, hpr, seed=42)
    print(f"Run 1 (Seed 42): Victory={res1.victory}, HP={res1.remaining_health}")
    print(f"Run 2 (Seed 42): Victory={res2.victory}, HP={res2.remaining_health}")
    if res1 == res2:
        print("SUCCESS: Identical results with same seed.")
    else:
        print("FAIL: Results differ despite same seed!")

    print("\n--- 6. Invalid Inputs ---")
    try:
        simulate_round(average, difficulty_level=0, enemy_count=ec, enemy_damage=ed, health_pack_rate=hpr)
        print("FAIL: Expected ValueError for difficulty_level.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")

    try:
        simulate_round(average, difficulty_level=dl_test, enemy_count=ec, enemy_damage=ed, health_pack_rate=1.5)
        print("FAIL: Expected ValueError for health_pack_rate.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")
