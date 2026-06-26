"""
Experiment runners for static and adaptive game difficulty simulations.
"""
from dataclasses import dataclass
from typing import List, Optional

from src.player import PlayerProfile
from src.game_simulation import GameRoundResult, simulate_round
from src.difficulty_agent import (
    DifficultyDecision,
    AdaptiveDifficultyAgent,
    get_difficulty_settings
)

@dataclass
class ExperimentResult:
    """
    Data class representing the comprehensive results of a multi-round simulation.
    """
    system_type: str
    player_name: str
    initial_difficulty: int
    target_win_rate: float
    rounds: int
    final_difficulty: int
    total_wins: int
    total_losses: int
    overall_win_rate: float
    average_remaining_health: float
    average_damage_taken: float
    average_accuracy: float
    average_round_duration: float
    difficulty_changes: int
    round_results: List[GameRoundResult]
    decisions: List[DifficultyDecision]


def _validate_common_inputs(player: PlayerProfile, rounds: int, difficulty: int) -> None:
    """Validates common inputs for experiments."""
    if player is None:
        raise ValueError("player cannot be None")
    if not isinstance(rounds, int) or rounds <= 0:
        raise ValueError(f"rounds must be > 0. Got: {rounds}")
    if not isinstance(difficulty, int) or not (1 <= difficulty <= 10):
        raise ValueError(f"difficulty must be between 1 and 10. Got: {difficulty}")

def _calculate_experiment_stats(
    system_type: str,
    player: PlayerProfile,
    initial_difficulty: int,
    target_win_rate: float,
    final_difficulty: int,
    difficulty_changes: int,
    round_results: List[GameRoundResult],
    decisions: List[DifficultyDecision]
) -> ExperimentResult:
    """Calculates summary statistics and returns an ExperimentResult."""
    rounds = len(round_results)
    total_wins = sum(1 for r in round_results if r.victory)
    total_losses = rounds - total_wins
    overall_win_rate = total_wins / rounds if rounds > 0 else 0.0
    
    avg_health = sum(r.remaining_health for r in round_results) / rounds if rounds > 0 else 0.0
    avg_damage = sum(r.damage_taken for r in round_results) / rounds if rounds > 0 else 0.0
    avg_accuracy = sum(r.accuracy for r in round_results) / rounds if rounds > 0 else 0.0
    avg_duration = sum(r.round_duration for r in round_results) / rounds if rounds > 0 else 0.0
    
    return ExperimentResult(
        system_type=system_type,
        player_name=player.name,
        initial_difficulty=initial_difficulty,
        target_win_rate=target_win_rate,
        rounds=rounds,
        final_difficulty=final_difficulty,
        total_wins=total_wins,
        total_losses=total_losses,
        overall_win_rate=overall_win_rate,
        average_remaining_health=avg_health,
        average_damage_taken=avg_damage,
        average_accuracy=avg_accuracy,
        average_round_duration=avg_duration,
        difficulty_changes=difficulty_changes,
        round_results=round_results,
        decisions=decisions
    )

def run_static_experiment(
    player: PlayerProfile,
    rounds: int,
    difficulty_level: int,
    seed: Optional[int] = None
) -> ExperimentResult:
    """
    Runs an experiment where the difficulty remains static across all rounds.
    """
    _validate_common_inputs(player, rounds, difficulty_level)
    
    settings = get_difficulty_settings(difficulty_level)
    round_results = []
    
    for i in range(rounds):
        # Reproducible seed per round
        round_seed = None if seed is None else seed + i
        res = simulate_round(
            player=player,
            difficulty_level=settings.difficulty_level,
            enemy_count=settings.enemy_count,
            enemy_damage=settings.enemy_damage,
            health_pack_rate=settings.health_pack_rate,
            seed=round_seed
        )
        round_results.append(res)
        
    return _calculate_experiment_stats(
        system_type="static",
        player=player,
        initial_difficulty=difficulty_level,
        target_win_rate=0.0, # Not applicable for static
        final_difficulty=difficulty_level,
        difficulty_changes=0,
        round_results=round_results,
        decisions=[]
    )

def run_adaptive_experiment(
    player: PlayerProfile,
    rounds: int,
    initial_difficulty: int,
    agent: Optional[AdaptiveDifficultyAgent] = None,
    seed: Optional[int] = None
) -> ExperimentResult:
    """
    Runs an experiment where an agent adaptively changes the difficulty.
    """
    _validate_common_inputs(player, rounds, initial_difficulty)
    
    if agent is None:
        agent = AdaptiveDifficultyAgent()
        
    current_difficulty = initial_difficulty
    round_results = []
    decisions = []
    difficulty_changes = 0
    
    for i in range(rounds):
        settings = get_difficulty_settings(current_difficulty)
        
        # Reproducible seed per round
        round_seed = None if seed is None else seed + i
        
        # Simulate round
        res = simulate_round(
            player=player,
            difficulty_level=settings.difficulty_level,
            enemy_count=settings.enemy_count,
            enemy_damage=settings.enemy_damage,
            health_pack_rate=settings.health_pack_rate,
            seed=round_seed
        )
        round_results.append(res)
        
        # Agent decides next round's difficulty based on history so far
        decision = agent.decide(current_difficulty, round_results)
        decisions.append(decision)
        
        if decision.action != "keep" and decision.new_level != decision.previous_level:
            difficulty_changes += 1
            
        current_difficulty = decision.new_level
        
    return _calculate_experiment_stats(
        system_type="adaptive",
        player=player,
        initial_difficulty=initial_difficulty,
        target_win_rate=agent.target_win_rate,
        final_difficulty=current_difficulty,
        difficulty_changes=difficulty_changes,
        round_results=round_results,
        decisions=decisions
    )

if __name__ == "__main__":
    from src.player import create_default_players
    
    def print_summary(res: ExperimentResult, title: str):
        print(f"\n{title}:")
        print(f"* Player: {res.player_name}")
        print(f"* Rounds: {res.rounds}")
        print(f"* Win Rate: {res.overall_win_rate * 100.0:.1f} %")
        if res.system_type == "adaptive":
            print(f"* Initial Difficulty: {res.initial_difficulty}")
        print(f"* Final Difficulty: {res.final_difficulty}")
        print(f"* Difficulty Changes: {res.difficulty_changes}")

    players = create_default_players()
    beginner = players[0]
    average = players[1]
    expert = players[2]
    
    print("--- Running Manual Tests ---")

    # 1. Static Experiment
    res_static = run_static_experiment(average, 20, 5, seed=42)
    print_summary(res_static, "Static Experiment")
    assert len(res_static.round_results) == 20
    assert res_static.final_difficulty == 5
    assert res_static.difficulty_changes == 0
    assert len(res_static.decisions) == 0

    # 2. Adaptive Experiment (Beginner)
    res_adapt_beg = run_adaptive_experiment(beginner, 30, 7, seed=42)
    print_summary(res_adapt_beg, "Adaptive Experiment (Beginner)")
    assert len(res_adapt_beg.round_results) == 30
    assert len(res_adapt_beg.decisions) == 30
    assert res_adapt_beg.difficulty_changes > 0
    assert 1 <= res_adapt_beg.final_difficulty <= 10
    
    # 3. Adaptive Experiment (Expert)
    res_adapt_exp = run_adaptive_experiment(expert, 30, 3, seed=42)
    print_summary(res_adapt_exp, "Adaptive Experiment (Expert)")
    assert res_adapt_exp.final_difficulty > 3
    assert res_adapt_exp.difficulty_changes > 0

    # 4. Reproducibility
    res_adapt_rep = run_adaptive_experiment(beginner, 30, 7, seed=42)
    assert res_adapt_beg == res_adapt_rep, "Reproducibility test failed! Results are not identical."
    print("\nSUCCESS: Reproducibility test passed.")

    # 5. Invalid Inputs
    print("\n--- Testing Invalid Inputs ---")
    try:
        run_static_experiment(average, 0, 5)
        print("FAIL: Expected ValueError for rounds=0")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")

    try:
        run_adaptive_experiment(average, 10, 11)
        print("FAIL: Expected ValueError for initial_difficulty=11")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")

    try:
        run_static_experiment(None, 10, 5)
        print("FAIL: Expected ValueError for player=None")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")
