"""
Difficulty modeling to translate difficulty levels into game parameters
and adaptive logic to adjust difficulty based on player performance.
"""
from dataclasses import dataclass
from typing import List

from src.game_simulation import GameRoundResult

@dataclass
class DifficultySettings:
    """
    Data class representing the game parameters for a specific difficulty level.
    """
    difficulty_level: int
    enemy_count: int
    enemy_damage: int
    health_pack_rate: float

def get_difficulty_settings(difficulty_level: int) -> DifficultySettings:
    """
    Translates a difficulty level (1-10) into concrete game parameters.
    """
    if not isinstance(difficulty_level, int) or not (1 <= difficulty_level <= 10):
        raise ValueError(f"difficulty_level must be an integer between 1 and 10. Got: {difficulty_level}")

    enemy_count = 3 + (difficulty_level - 1) * 1
    enemy_damage = 5 + (difficulty_level - 1) * 1
    health_pack_rate = max(0.0, 0.40 - (difficulty_level - 1) * 0.03)

    return DifficultySettings(
        difficulty_level=difficulty_level,
        enemy_count=enemy_count,
        enemy_damage=enemy_damage,
        health_pack_rate=round(health_pack_rate, 2)
    )

@dataclass
class DifficultyDecision:
    """
    Represents a decision made by the AdaptiveDifficultyAgent.
    """
    previous_level: int
    new_level: int
    action: str  # "increase", "decrease", "keep"
    reason: str
    recent_win_rate: float
    consecutive_wins: int
    consecutive_losses: int

class AdaptiveDifficultyAgent:
    """
    Analyzes recent game rounds to adaptively change the game's difficulty.
    """
    def __init__(
        self, 
        target_win_rate: float = 0.60, 
        window_size: int = 5, 
        min_difficulty: int = 1, 
        max_difficulty: int = 10
    ):
        if not (0.0 <= target_win_rate <= 1.0):
            raise ValueError(f"target_win_rate must be between 0.0 and 1.0. Got {target_win_rate}")
        if window_size <= 0:
            raise ValueError(f"window_size must be > 0. Got {window_size}")
        if min_difficulty < 1:
            raise ValueError(f"min_difficulty must be >= 1. Got {min_difficulty}")
        if max_difficulty > 10:
            raise ValueError(f"max_difficulty must be <= 10. Got {max_difficulty}")
        if min_difficulty > max_difficulty:
            raise ValueError("min_difficulty cannot be greater than max_difficulty.")
            
        self.target_win_rate = target_win_rate
        self.window_size = window_size
        self.min_difficulty = min_difficulty
        self.max_difficulty = max_difficulty

    def decide(self, current_level: int, recent_results: List[GameRoundResult]) -> DifficultyDecision:
        """
        Decides whether to increase, decrease, or keep the difficulty based on recent performance.
        """
        if not (self.min_difficulty <= current_level <= self.max_difficulty):
            raise ValueError(f"current_level {current_level} is out of bounds [{self.min_difficulty}, {self.max_difficulty}]")

        if not recent_results:
            return DifficultyDecision(
                previous_level=current_level,
                new_level=current_level,
                action="keep",
                reason="Difficulty kept because no recent results are available.",
                recent_win_rate=0.0,
                consecutive_wins=0,
                consecutive_losses=0
            )

        # Consider only the last `window_size` results
        window = recent_results[-self.window_size:]
        
        # Calculate consecutive wins/losses at the end of the window
        consecutive_wins = 0
        consecutive_losses = 0
        
        for result in reversed(window):
            if result.victory:
                if consecutive_losses > 0:
                    break
                consecutive_wins += 1
            else:
                if consecutive_wins > 0:
                    break
                consecutive_losses += 1

        # Calculate win rate in the window
        wins = sum(1 for r in window if r.victory)
        win_rate = wins / len(window)

        # Decision Logic
        action = "keep"
        reason = "Difficulty kept because player performance is within the target range."
        
        if consecutive_losses >= 3:
            action = "decrease"
            reason = "Difficulty decreased after three consecutive losses."
        elif consecutive_wins >= 3 and win_rate > self.target_win_rate:
            action = "increase"
            reason = "Difficulty increased after three consecutive wins and high win rate."
        elif win_rate <= self.target_win_rate - 0.20:
            action = "decrease"
            reason = "Difficulty decreased because the recent win rate is below the target range."
        elif win_rate >= self.target_win_rate + 0.20:
            action = "increase"
            reason = "Difficulty increased because the recent win rate is above the target range."

        # Apply action and limits
        new_level = current_level
        if action == "increase":
            new_level = min(self.max_difficulty, current_level + 1)
        elif action == "decrease":
            new_level = max(self.min_difficulty, current_level - 1)
            
        # Re-evaluate action in case boundary prevented a change
        if new_level == current_level and action != "keep":
            action = "keep"
            reason += f" (Boundary reached, kept at {current_level})"

        return DifficultyDecision(
            previous_level=current_level,
            new_level=new_level,
            action=action,
            reason=reason,
            recent_win_rate=win_rate,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses
        )

if __name__ == "__main__":
    def create_mock_result(victory: bool) -> GameRoundResult:
        return GameRoundResult(
            victory=victory, remaining_health=100 if victory else 0, damage_taken=0, 
            accuracy=1.0, round_duration=10.0, difficulty_level=5, 
            enemy_count=1, enemy_damage=1, health_pack_rate=0.0
        )

    agent = AdaptiveDifficultyAgent(target_win_rate=0.60, window_size=5)
    
    print("--- 1. Empty Results ---")
    decision = agent.decide(5, [])
    print(f"Action: {decision.action}, Reason: {decision.reason}")
    assert decision.action == "keep"

    print("\n--- 2. Three Consecutive Losses ---")
    results = [create_mock_result(False)] * 3
    decision = agent.decide(5, results)
    print(f"Action: {decision.action}, Reason: {decision.reason}")
    assert decision.action == "decrease"

    print("\n--- 3. Three Consecutive Wins ---")
    results = [create_mock_result(True)] * 3
    decision = agent.decide(5, results)
    print(f"Action: {decision.action}, Reason: {decision.reason}")
    assert decision.action == "increase"

    print("\n--- 4. Mixed Results Near Target ---")
    # 3 wins, 2 losses = 60% win rate
    results = [
        create_mock_result(True),
        create_mock_result(False),
        create_mock_result(True),
        create_mock_result(False),
        create_mock_result(True)
    ]
    decision = agent.decide(5, results)
    print(f"Action: {decision.action}, Reason: {decision.reason}")
    assert decision.action == "keep"

    print("\n--- 5. Lower Boundary Test ---")
    results = [create_mock_result(False)] * 3
    decision = agent.decide(1, results)
    print(f"Action: {decision.action}, New Level: {decision.new_level}, Reason: {decision.reason}")
    assert decision.new_level == 1
    assert decision.action == "keep"

    print("\n--- 6. Upper Boundary Test ---")
    results = [create_mock_result(True)] * 3
    decision = agent.decide(10, results)
    print(f"Action: {decision.action}, New Level: {decision.new_level}, Reason: {decision.reason}")
    assert decision.new_level == 10
    assert decision.action == "keep"

    print("\n--- 7. Invalid Inputs ---")
    try:
        AdaptiveDifficultyAgent(target_win_rate=1.5)
        print("FAIL: Expected ValueError for target_win_rate")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")

    try:
        AdaptiveDifficultyAgent(min_difficulty=5, max_difficulty=3)
        print("FAIL: Expected ValueError for min > max")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")

    try:
        agent.decide(15, [])
        print("FAIL: Expected ValueError for current_level out of bounds")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")
