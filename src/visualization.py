"""
Visualization module for the Adaptive Game Difficulty Agent.
Generates plots comparing static and adaptive difficulty systems.
"""
import os
import matplotlib.pyplot as plt
from typing import List, Dict

from src.experiment import ExperimentResult

def _ensure_dir(output_path: str) -> None:
    """Ensures the directory for the given file path exists."""
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

def _group_by_player_and_system(results: List[ExperimentResult]) -> Dict[str, Dict[str, List[ExperimentResult]]]:
    """
    Groups results by player name and then by system type.
    Returns: { player_name: { system_type: [ExperimentResult,s ...] } }
    """
    grouped = {}
    for r in results:
        if r.player_name not in grouped:
            grouped[r.player_name] = {"static": [], "adaptive": []}
        grouped[r.player_name][r.system_type].append(r)
    return grouped

def _calculate_mean_win_rates(grouped: Dict[str, Dict[str, List[ExperimentResult]]]) -> Dict[str, Dict[str, float]]:
    """Calculates mean win rates for each player and system type."""
    means = {}
    for player, systems in grouped.items():
        means[player] = {}
        for sys_type, res_list in systems.items():
            if not res_list:
                means[player][sys_type] = 0.0
            else:
                means[player][sys_type] = sum(r.overall_win_rate for r in res_list) / len(res_list)
    return means
    
def _calculate_mean_deviations(grouped: Dict[str, Dict[str, List[ExperimentResult]]]) -> Dict[str, Dict[str, float]]:
    """Calculates mean target deviations for each player and system type."""
    means = {}
    for player, systems in grouped.items():
        means[player] = {}
        for sys_type, res_list in systems.items():
            if not res_list:
                means[player][sys_type] = 0.0
            else:
                # Use 0.60 as target
                means[player][sys_type] = sum(abs(r.overall_win_rate - 0.60) for r in res_list) / len(res_list)
    return means

def plot_win_rate_comparison(results: List[ExperimentResult], output_path: str = "results/figures/win_rate_comparison.png") -> None:
    """
    Plots a grouped bar chart comparing mean win rates between static and adaptive systems.
    """
    _ensure_dir(output_path)
    grouped = _group_by_player_and_system(results)
    means = _calculate_mean_win_rates(grouped)
    
    players = list(means.keys())
    static_means = [means[p]["static"] * 100 for p in players]
    adaptive_means = [means[p]["adaptive"] * 100 for p in players]
    
    x = range(len(players))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar([p - width/2 for p in x], static_means, width, label='Static')
    ax.bar([p + width/2 for p in x], adaptive_means, width, label='Adaptive')
    
    ax.axhline(y=60, color='r', linestyle='--', label='Target Win Rate (60%)')
    
    ax.set_ylabel('Mean Win Rate (%)')
    ax.set_title('Win Rate Comparison: Static vs. Adaptive')
    ax.set_xticks(x)
    ax.set_xticklabels(players)
    ax.set_ylim(0, 105)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def plot_target_deviation(results: List[ExperimentResult], output_path: str = "results/figures/target_deviation.png") -> None:
    """
    Plots a grouped bar chart comparing mean target deviations.
    """
    _ensure_dir(output_path)
    grouped = _group_by_player_and_system(results)
    means = _calculate_mean_deviations(grouped)
    
    players = list(means.keys())
    static_means = [means[p]["static"] * 100 for p in players]
    adaptive_means = [means[p]["adaptive"] * 100 for p in players]
    
    x = range(len(players))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar([p - width/2 for p in x], static_means, width, label='Static')
    ax.bar([p + width/2 for p in x], adaptive_means, width, label='Adaptive')
    
    ax.set_ylabel('Mean Target Deviation (%)')
    ax.set_title('Target Deviation Comparison (Lower is Better)')
    ax.set_xticks(x)
    ax.set_xticklabels(players)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def plot_difficulty_progression(result: ExperimentResult, output_path: str = "results/figures/difficulty_progression.png") -> None:
    """
    Plots the progression of difficulty levels across rounds for an adaptive experiment.
    """
    if result.system_type != "adaptive":
        raise ValueError("plot_difficulty_progression requires an adaptive ExperimentResult.")
    if not result.round_results:
        raise ValueError("ExperimentResult contains no round results.")
        
    _ensure_dir(output_path)
    
    rounds = range(1, result.rounds + 1)
    difficulties = [r.difficulty_level for r in result.round_results]

    last_played_difficulty = result.round_results[-1].difficulty_level

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(rounds, difficulties, marker='o', linestyle='-', markersize=4, label='Difficulty per Round')

    ax.axhline(y=result.initial_difficulty, color='g', linestyle='--', label=f'Initial Difficulty ({result.initial_difficulty})')
    ax.axhline(y=last_played_difficulty, color='r', linestyle=':', linewidth=2, label=f'Last Played Difficulty ({last_played_difficulty})')

    if result.final_difficulty != last_played_difficulty:
        ax.axhline(y=result.final_difficulty, color='orange', linestyle='-.', linewidth=2, label=f'Next Suggested Difficulty ({result.final_difficulty})')
    
    ax.set_xlabel('Round')
    ax.set_ylabel('Difficulty Level')
    ax.set_title(f'Difficulty Progression for {result.player_name}')
    ax.set_ylim(0, 11)
    ax.set_yticks(range(1, 11))
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def plot_moving_win_rate(result: ExperimentResult, window_size: int = 10, output_path: str = "results/figures/moving_win_rate.png") -> None:
    """
    Plots the moving win rate over a specified window size for an adaptive experiment.
    """
    if result.system_type != "adaptive":
        raise ValueError("plot_moving_win_rate requires an adaptive ExperimentResult.")
    if window_size <= 0:
        raise ValueError("window_size must be > 0.")
    if not result.round_results:
        raise ValueError("ExperimentResult contains no round results.")
        
    _ensure_dir(output_path)
    
    moving_win_rates = []
    victories = [1 if r.victory else 0 for r in result.round_results]
    
    for i in range(len(victories)):
        start = max(0, i - window_size + 1)
        window = victories[start:i+1]
        moving_win_rates.append((sum(window) / len(window)) * 100)
        
    rounds = range(1, len(victories) + 1)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(rounds, moving_win_rates, linestyle='-', label=f'Moving Win Rate (window={window_size})')
    
    ax.axhline(y=60, color='r', linestyle='--', label='Target Win Rate (60%)')
    
    ax.set_xlabel('Round')
    ax.set_ylabel('Win Rate (%)')
    ax.set_title(f'Moving Win Rate for {result.player_name}')
    ax.set_ylim(-5, 105)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

if __name__ == "__main__":
    import os
    from src.player import create_default_players
    from src.experiment import run_comparison_experiments, run_adaptive_experiment
    
    print("--- Running Visualization Tests ---")
    
    # 1. Generate players
    players = create_default_players()
    
    # 2. Run comparative experiments
    rounds_comp = 300
    seeds_comp = [42, 123, 999]
    print("Running comparative experiments...")
    results_comp = run_comparison_experiments(
        players=players,
        rounds_per_experiment=rounds_comp,
        initial_difficulty=5,
        seeds=seeds_comp,
        output_path="results/data/temp_visualization_comp.csv"
    )
    
    # 3. Generate comparison plots
    p1 = "results/figures/win_rate_comparison.png"
    p2 = "results/figures/target_deviation.png"
    plot_win_rate_comparison(results_comp, p1)
    plot_target_deviation(results_comp, p2)
    
    # 4. Run single adaptive experiment
    rounds_adapt = 100
    average_player = players[1]
    print("Running adaptive experiment...")
    res_adapt = run_adaptive_experiment(
        player=average_player,
        rounds=rounds_adapt,
        initial_difficulty=5,
        seed=42
    )
    
    # 5. Generate progression plots
    p3 = "results/figures/difficulty_progression.png"
    p4 = "results/figures/moving_win_rate.png"
    plot_difficulty_progression(res_adapt, p3)
    plot_moving_win_rate(res_adapt, window_size=10, output_path=p4)
    
    # 6. Verifications
    print("\n--- Verifying Output ---")
    files = [p1, p2, p3, p4]
    file_sizes = {}
    for f in files:
        assert os.path.exists(f), f"File {f} was not created!"
        size = os.path.getsize(f)
        assert size > 0, f"File {f} is empty!"
        file_sizes[f] = size
        
    print("SUCCESS: All plot files generated successfully.")
    
    # 7. Testing Invalid Inputs
    print("\n--- Testing Invalid Inputs ---")
    static_res = [r for r in results_comp if r.system_type == "static"][0]
    
    try:
        plot_difficulty_progression(static_res, "tmp.png")
        print("FAIL: Expected ValueError for static result in difficulty progression.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")
        
    try:
        plot_moving_win_rate(static_res, 10, "tmp.png")
        print("FAIL: Expected ValueError for static result in moving win rate.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")

    try:
        plot_moving_win_rate(res_adapt, 0, "tmp.png")
        print("FAIL: Expected ValueError for window_size=0.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")
        
    empty_adapt = run_adaptive_experiment(average_player, 1, 5)
    empty_adapt.round_results = [] # artificially empty
    try:
        plot_difficulty_progression(empty_adapt, "tmp.png")
        print("FAIL: Expected ValueError for empty round results.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")
        
    # 8. Summary Output
    print("\n--- Visualization Summary ---")
    print("Generated Files:")
    for f, s in file_sizes.items():
        print(f"* {f} ({s / 1024:.1f} KB)")
        
    print(f"\nPlayers used: {[p.name for p in players]}")
    print(f"Rounds used (comparative): {rounds_comp}")
    print(f"Seeds used (comparative): {seeds_comp}")
    print(f"Rounds used (adaptive progression): {rounds_adapt}")
