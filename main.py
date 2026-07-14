"""
Live terminal demo for the Adaptive Game Difficulty Agent.

Usage:
    python main.py
    python main.py --player beginner --rounds 10 --difficulty 7 --seed 42
    python main.py --player expert  --rounds 10 --difficulty 3 --seed 42
    python main.py --reaction-test --rounds 15 --difficulty 5
    python main.py --reaction-test --reaction-attempts 7 --rounds 20 --difficulty 6
"""
import argparse
import time
from typing import List

from src.player import PlayerProfile, create_default_players
from src.game_simulation import GameRoundResult, simulate_round
from src.difficulty_agent import AdaptiveDifficultyAgent, DifficultyDecision, get_difficulty_settings
from src.reaction_test import (
    run_reaction_test,
    create_reaction_profile,
)

# ── Player selection ──────────────────────────────────────────────────────────

PLAYER_KEYS = {
    "beginner": 0,
    "average":  1,
    "expert":   2,
}


def select_player(player_type: str) -> PlayerProfile:
    """Return the PlayerProfile that matches *player_type* key."""
    players = create_default_players()
    index = PLAYER_KEYS[player_type]
    return players[index]


# ── CLI argument parsing ──────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Adaptive Game Difficulty Agent – live terminal demo.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--player",
        choices=list(PLAYER_KEYS.keys()),
        default="average",
        help="Player skill profile to use.",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=15,
        help="Number of rounds to simulate (must be > 0).",
    )
    parser.add_argument(
        "--difficulty",
        type=int,
        default=5,
        help="Starting difficulty level (1-10).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Base random seed for reproducibility.",
    )
    parser.add_argument(
        "--reaction-test",
        action="store_true",
        help="Run the reaction time test and build a personalised player profile.",
    )
    parser.add_argument(
        "--reaction-attempts",
        type=int,
        default=5,
        help="Number of reaction-time measurements to collect (minimum 3).",
    )

    args = parser.parse_args()

    # Manual validation with clear error messages
    if args.rounds <= 0:
        parser.error(f"--rounds must be greater than 0, got {args.rounds}.")
    if not (1 <= args.difficulty <= 10):
        parser.error(f"--difficulty must be between 1 and 10, got {args.difficulty}.")
    if args.reaction_attempts < 3:
        parser.error(
            f"--reaction-attempts must be >= 3, got {args.reaction_attempts}."
        )

    return args


# ── Output helpers ────────────────────────────────────────────────────────────

def _action_label(action: str) -> str:
    """Return a display label for an agent action (kept in English as spec shows)."""
    return action


def compute_win_rates(
    history: List[GameRoundResult],
    window_size: int,
) -> tuple[float, float]:
    """Return (overall_win_rate, window_win_rate) after the latest round."""
    total   = len(history)
    overall = sum(1 for r in history if r.victory) / total
    window  = history[-window_size:]
    recent  = sum(1 for r in window if r.victory) / len(window)
    return overall, recent


def print_round_line(
    round_num: int,
    difficulty: int,
    result: GameRoundResult,
    decision: DifficultyDecision,
    overall_win_rate: float,
    window_win_rate: float,
    window_size: int,
    round_num_for_label: int,
) -> None:
    """Print a single human-readable summary line for one game round."""
    outcome    = "Sieg" if result.victory else "Niederlage"
    heal_pct   = int(result.health_pack_rate * 100)
    acc_pct    = int(result.accuracy * 100)
    action_str = _action_label(decision.action)

    print(
        f"Runde {round_num:02d} | "
        f"Schwierigkeit {difficulty} | "
        f"Gegner {result.enemy_count} | "
        f"Schaden {result.enemy_damage} | "
        f"Heilung {heal_pct} % | "
        f"{outcome} | "
        f"HP {result.remaining_health} | "
        f"Trefferquote {acc_pct} % | "
        f"Agent: {action_str} | "
        f"Nächste Schwierigkeit {decision.new_level}"
    )
    actual_window = min(window_size, round_num_for_label)
    runden_label  = "Runde" if actual_window == 1 else "Runden"
    print(
        f"  Gesamtgewinnrate {overall_win_rate * 100:.1f} % | "
        f"Letzte {actual_window} {runden_label} {window_win_rate * 100:.1f} %"
    )


def print_change_reason(decision: DifficultyDecision) -> None:
    """Print the agent's reason when the difficulty actually changed."""
    if decision.previous_level < decision.new_level:
        direction = "erhöht"
    else:
        direction = "reduziert"
    print(f"→ Schwierigkeit {direction}: {decision.reason}")


def print_summary(
    player: PlayerProfile,
    num_rounds: int,
    results: List[GameRoundResult],
    decisions: List[DifficultyDecision],
    start_difficulty: int,
    target_win_rate: float,
) -> None:
    """Print the final statistics summary after all rounds."""
    wins     = sum(1 for r in results if r.victory)
    losses   = num_rounds - wins
    win_rate = wins / num_rounds if num_rounds else 0.0

    avg_hp  = sum(r.remaining_health for r in results) / num_rounds if num_rounds else 0.0
    avg_acc = sum(r.accuracy for r in results) / num_rounds if num_rounds else 0.0
    avg_dur = sum(r.round_duration for r in results) / num_rounds if num_rounds else 0.0

    last_played_difficulty = results[-1].difficulty_level if results else start_difficulty
    next_suggested         = decisions[-1].new_level if decisions else start_difficulty

    # Count rounds where the difficulty actually changed
    real_changes = sum(1 for d in decisions if d.previous_level != d.new_level)

    width = 56
    print()
    print("=" * width)
    print("  ZUSAMMENFASSUNG")
    print("=" * width)
    print(f"  Spieler                    : {player.name}")
    print(f"  Runden                     : {num_rounds}")
    print(f"  Siege                      : {wins}")
    print(f"  Niederlagen                : {losses}")
    print(f"  Gesamtgewinnrate           : {win_rate * 100:.1f} %")
    print(f"  Zielgewinnrate             : {target_win_rate * 100:.1f} %")
    print(f"  Startschwierigkeit         : {start_difficulty}")
    print(f"  Zuletzt gespielte Schw.    : {last_played_difficulty}")
    print(f"  Nächste vorgeschl. Schw.   : {next_suggested}")
    print(f"  Echte Schwierigkeitsänd.   : {real_changes}")
    print(f"  Ø verbleibende HP          : {avg_hp:.1f}")
    print(f"  Ø Trefferquote             : {avg_acc * 100:.1f} %")
    print(f"  Ø Rundendauer              : {avg_dur:.1f} s")
    print("=" * width)


# ── Main demo loop ────────────────────────────────────────────────────────────

def run_demo(
    player: PlayerProfile,
    num_rounds: int,
    start_difficulty: int,
    seed: int,
    target_win_rate: float = 0.60,
    window_size: int = 5,
) -> None:
    """Run the full adaptive difficulty demo and print results to stdout."""
    agent = AdaptiveDifficultyAgent(
        target_win_rate=target_win_rate,
        window_size=window_size,
    )

    current_difficulty = start_difficulty
    history:   List[GameRoundResult]    = []
    decisions: List[DifficultyDecision] = []

    print()
    print(f"  Adaptive Game Difficulty Agent – Live Demo")
    print(f"  Spieler: {player.name} | Runden: {num_rounds} | "
          f"Startschwierigkeit: {start_difficulty} | Seed: {seed}")
    print("-" * 80)

    for round_num in range(1, num_rounds + 1):
        # 1. Derive game parameters from current difficulty
        settings = get_difficulty_settings(current_difficulty)

        # 2. Simulate the round with a deterministic per-round seed
        round_seed = seed + (round_num - 1)
        result = simulate_round(
            player=player,
            difficulty_level=settings.difficulty_level,
            enemy_count=settings.enemy_count,
            enemy_damage=settings.enemy_damage,
            health_pack_rate=settings.health_pack_rate,
            seed=round_seed,
        )

        # 3. Append result to history
        history.append(result)

        # 4. Agent decides next difficulty
        decision = agent.decide(current_difficulty, history)
        decisions.append(decision)

        # 5. Compute win rates from the updated history
        overall_wr, window_wr = compute_win_rates(history, window_size)

        # 6. Print round summary line
        print_round_line(
            round_num, current_difficulty, result, decision,
            overall_wr, window_wr, window_size,
            round_num_for_label=round_num,
        )

        # Print reason if difficulty actually changed
        if decision.previous_level != decision.new_level:
            print_change_reason(decision)

        # Print the extra result line with color and pause
        if result.victory:
            print("\033[92mPlayer Won!\033[0m")
        else:
            print("\033[91mPlayer Lost!\033[0m")
        
        time.sleep(1.5)

        # Advance to the next difficulty
        current_difficulty = decision.new_level

    # Final summary
    print_summary(
        player=player,
        num_rounds=num_rounds,
        results=history,
        decisions=decisions,
        start_difficulty=start_difficulty,
        target_win_rate=target_win_rate,
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = parse_args()

    if args.reaction_test:
        # ── Reaction-test mode ────────────────────────────────────────────────
        if args.player != "average":
            print(
                "Hinweis: Das Argument --player wird im Reaktionstest-Modus ignoriert."
            )

        # Run the interactive reaction test
        test_result = run_reaction_test(
            attempts=args.reaction_attempts,
            seed=args.seed,
        )

        # Build a personalised player profile from the measured reaction time
        player = create_reaction_profile(test_result.median_reaction_time_ms)

        # Display the generated profile
        print()
        print("Persönliches Profil:")
        print(f"  Name:             {player.name}")
        print(f"  Skill Level:      {player.skill_level:.2f}")
        print(f"  Accuracy:         {player.accuracy:.2f}")
        print(f"  Reaction Speed:   {player.reaction_speed:.2f}")
        print(f"  Survival Factor:  {player.survival_factor:.2f}")
        print()
        print("Die adaptive Demo wird jetzt mit diesem Profil gestartet.")

    else:
        # ── Normal mode ───────────────────────────────────────────────────────
        player = select_player(args.player)

    run_demo(
        player=player,
        num_rounds=args.rounds,
        start_difficulty=args.difficulty,
        seed=args.seed,
    )
