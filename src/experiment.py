"""
Experiment runners for static and adaptive game difficulty simulations.
"""
import os
import csv
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

def run_comparison_experiments(
    players: List[PlayerProfile],
    rounds_per_experiment: int = 300,
    initial_difficulty: int = 5,
    seeds: Optional[List[int]] = None,
    output_path: str = "results/data/comparison_results.csv"
) -> List[ExperimentResult]:
    """
    Runs comparative experiments between static and adaptive difficulty systems
    and saves the summarized results into a CSV file.
    """
    if not players:
        raise ValueError("The 'players' list cannot be empty.")
    if rounds_per_experiment <= 0:
        raise ValueError(f"rounds_per_experiment must be > 0. Got: {rounds_per_experiment}")
    if not (1 <= initial_difficulty <= 10):
        raise ValueError(f"initial_difficulty must be between 1 and 10. Got: {initial_difficulty}")
    
    if seeds is None:
        seeds = [42, 123, 999]
    if not seeds:
        raise ValueError("The 'seeds' list cannot be empty.")
    for s in seeds:
        if not isinstance(s, int):
            raise ValueError(f"Invalid seed value: {s}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    all_results = []
    meta_results = [] # Stores tuple of (ExperimentResult, seed, target_deviation)
    
    # Run experiments
    for player in players:
        for seed in seeds:
            # Run static
            res_static = run_static_experiment(player, rounds_per_experiment, initial_difficulty, seed=seed)
            # Use 0.60 for calculating static deviation for comparison
            dev_static = abs(res_static.overall_win_rate - 0.60)
            
            # Run adaptive
            res_adapt = run_adaptive_experiment(player, rounds_per_experiment, initial_difficulty, seed=seed)
            dev_adapt = abs(res_adapt.overall_win_rate - res_adapt.target_win_rate)
            
            all_results.extend([res_static, res_adapt])
            meta_results.append((res_static, seed, dev_static))
            meta_results.append((res_adapt, seed, dev_adapt))

    # Write CSV
    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "system_type", "player_name", "seed", "rounds", 
            "initial_difficulty", "final_difficulty", "target_win_rate", 
            "total_wins", "total_losses", "overall_win_rate", 
            "target_deviation", "average_remaining_health", 
            "average_damage_taken", "average_accuracy", 
            "average_round_duration", "difficulty_changes"
        ])
        
        for res, seed, dev in meta_results:
            t_win_rate = 0.60 if res.system_type == "static" else res.target_win_rate
            writer.writerow([
                res.system_type,
                res.player_name,
                seed,
                res.rounds,
                res.initial_difficulty,
                res.final_difficulty,
                f"{t_win_rate:.6f}",
                res.total_wins,
                res.total_losses,
                f"{res.overall_win_rate:.6f}",
                f"{dev:.6f}",
                f"{res.average_remaining_health:.6f}",
                f"{res.average_damage_taken:.6f}",
                f"{res.average_accuracy:.6f}",
                f"{res.average_round_duration:.6f}",
                res.difficulty_changes
            ])
            
    return all_results


if __name__ == "__main__":
    from src.player import create_default_players
    
    players = create_default_players()
    print("--- Running Comparison Experiments ---")
    
    # 1. Run 300 rounds, initial diff 5, 3 seeds
    results = run_comparison_experiments(
        players=players, 
        rounds_per_experiment=300, 
        initial_difficulty=5, 
        seeds=[42, 123, 999]
    )
    
    # 2. Print Summary and Interpretation
    for p in players:
        p_name = p.name
        print(f"\nPlayer: {p_name}")
        
        stat_res = [r for r in results if r.player_name == p_name and r.system_type == "static"]
        adapt_res = [r for r in results if r.player_name == p_name and r.system_type == "adaptive"]
        
        def print_stats(res_list, sys_type):
            if not res_list: return 0.0
            avg_win_rate = sum(r.overall_win_rate for r in res_list) / len(res_list)
            target = 0.60 if sys_type == "Static" else res_list[0].target_win_rate
            avg_dev = sum(abs(r.overall_win_rate - target) for r in res_list) / len(res_list)
            avg_final_diff = sum(r.final_difficulty for r in res_list) / len(res_list)
            avg_diff_changes = sum(r.difficulty_changes for r in res_list) / len(res_list)
            
            print(f"\n{sys_type}:")
            print(f"* Mean Win Rate: {avg_win_rate * 100:.1f} %")
            print(f"* Mean Target Deviation: {avg_dev * 100:.1f} %")
            if sys_type == "Adaptive":
                print(f"* Mean Final Difficulty: {avg_final_diff:.1f}")
                print(f"* Mean Difficulty Changes: {avg_diff_changes:.1f}")
            return avg_dev
            
        stat_dev = print_stats(stat_res, "Static")
        adapt_dev = print_stats(adapt_res, "Adaptive")
        
        print("\nInterpretation:")
        if abs(stat_dev - adapt_dev) <= 0.01:
            print("Both systems perform similarly.")
        elif adapt_dev < stat_dev:
            print("Adaptive system is closer to the target win rate.")
        else:
            print("Static system is closer to the target win rate.")

    # 3. Validation and Basic Checks
    print("\n--- Validating Results ---")
    assert len(results) == 18, f"Expected 18 results, got {len(results)}"
    
    static_runs = [r for r in results if r.system_type == "static"]
    adaptive_runs = [r for r in results if r.system_type == "adaptive"]
    
    assert all(r.difficulty_changes == 0 for r in static_runs), "Static runs must have 0 changes"
    assert all(1 <= r.final_difficulty <= 10 for r in adaptive_runs), "Adaptive final difficulty must be bounded"
    
    print("SUCCESS: Tests passed.")

    # 4. Check Reproducibility with Same Seeds
    print("\n--- Testing Reproducibility ---")
    results_rep = run_comparison_experiments(players, 300, 5, [42, 123, 999], output_path="results/data/comparison_results_rep.csv")
    for r1, r2 in zip(results, results_rep):
        assert r1.overall_win_rate == r2.overall_win_rate, "Reproducibility failed"
    print("SUCCESS: Experiments are fully reproducible.")

    # 5. Invalid Inputs
    print("\n--- Testing Invalid Inputs ---")
    try:
        run_comparison_experiments([], 300, 5)
        print("FAIL: Expected ValueError for empty players.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")

    try:
        run_comparison_experiments(players, 0, 5)
        print("FAIL: Expected ValueError for rounds <= 0.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")

    try:
        run_comparison_experiments(players, 300, 5, seeds=[])
        print("FAIL: Expected ValueError for empty seeds.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")
