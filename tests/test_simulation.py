"""
Automated pytest tests for the Adaptive Game Difficulty Agent project.

Run with:
    ./.venv/bin/python -m pytest -v
"""
import csv
import pytest
from typing import List

# ── Imports under test ────────────────────────────────────────────────────────

from src.player import PlayerProfile, create_default_players
from src.game_simulation import GameRoundResult, simulate_round
from src.difficulty_agent import (
    AdaptiveDifficultyAgent,
    DifficultyDecision,
    get_difficulty_settings,
)
from src.experiment import (
    run_static_experiment,
    run_adaptive_experiment,
    run_comparison_experiments,
)
from main import select_player, compute_win_rates


# ── Shared helpers / fixtures ─────────────────────────────────────────────────

def make_result(victory: bool) -> GameRoundResult:
    """Minimal GameRoundResult for agent tests."""
    return GameRoundResult(
        victory=victory,
        remaining_health=100 if victory else 0,
        damage_taken=0 if victory else 100,
        accuracy=0.8,
        round_duration=30.0,
        difficulty_level=5,
        enemy_count=7,
        enemy_damage=9,
        health_pack_rate=0.28,
    )


@pytest.fixture
def average_player() -> PlayerProfile:
    """Return the average player profile."""
    return create_default_players()[1]


@pytest.fixture
def beginner_player() -> PlayerProfile:
    """Return the beginner player profile."""
    return create_default_players()[0]


@pytest.fixture
def expert_player() -> PlayerProfile:
    """Return the expert player profile."""
    return create_default_players()[2]


@pytest.fixture
def agent() -> AdaptiveDifficultyAgent:
    """Return a default AdaptiveDifficultyAgent."""
    return AdaptiveDifficultyAgent(target_win_rate=0.60, window_size=5)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PlayerProfile
# ═══════════════════════════════════════════════════════════════════════════════

class TestPlayerProfile:

    def test_valid_creation(self):
        """A fully valid PlayerProfile is created without errors."""
        p = PlayerProfile(
            name="Tester",
            skill_level=0.5,
            accuracy=0.5,
            reaction_speed=0.5,
            survival_factor=0.5,
        )
        assert p.name == "Tester"
        assert p.skill_level == 0.5

    def test_empty_name_raises(self):
        """Empty or whitespace-only name raises ValueError."""
        with pytest.raises(ValueError, match="name"):
            PlayerProfile(name="", skill_level=0.5, accuracy=0.5,
                          reaction_speed=0.5, survival_factor=0.5)

    def test_whitespace_name_raises(self):
        with pytest.raises(ValueError):
            PlayerProfile(name="   ", skill_level=0.5, accuracy=0.5,
                          reaction_speed=0.5, survival_factor=0.5)

    def test_skill_below_zero_raises(self):
        """Attribute below 0.0 raises ValueError."""
        with pytest.raises(ValueError):
            PlayerProfile(name="X", skill_level=-0.1, accuracy=0.5,
                          reaction_speed=0.5, survival_factor=0.5)

    def test_accuracy_above_one_raises(self):
        """Attribute above 1.0 raises ValueError."""
        with pytest.raises(ValueError):
            PlayerProfile(name="X", skill_level=0.5, accuracy=1.1,
                          reaction_speed=0.5, survival_factor=0.5)

    def test_reaction_speed_below_zero_raises(self):
        with pytest.raises(ValueError):
            PlayerProfile(name="X", skill_level=0.5, accuracy=0.5,
                          reaction_speed=-0.01, survival_factor=0.5)

    def test_survival_factor_above_one_raises(self):
        with pytest.raises(ValueError):
            PlayerProfile(name="X", skill_level=0.5, accuracy=0.5,
                          reaction_speed=0.5, survival_factor=1.01)

    def test_create_default_players_count(self):
        """create_default_players() returns exactly three profiles."""
        players = create_default_players()
        assert len(players) == 3

    def test_expert_has_higher_stats_than_beginner(self):
        """Expert's combined stats exceed beginner's combined stats."""
        players = create_default_players()
        beginner = players[0]
        expert   = players[2]
        beginner_total = (beginner.skill_level + beginner.accuracy +
                          beginner.reaction_speed + beginner.survival_factor)
        expert_total   = (expert.skill_level + expert.accuracy +
                          expert.reaction_speed + expert.survival_factor)
        assert expert_total > beginner_total

    def test_boundary_values_accepted(self):
        """Exact boundary values 0.0 and 1.0 are valid."""
        p = PlayerProfile(name="Bound", skill_level=0.0, accuracy=1.0,
                          reaction_speed=0.0, survival_factor=1.0)
        assert p.skill_level == 0.0
        assert p.accuracy == 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# 2. simulate_round
# ═══════════════════════════════════════════════════════════════════════════════

class TestSimulateRound:

    def test_same_seed_produces_identical_results(self, average_player):
        """Two calls with the same seed must return identical results."""
        r1 = simulate_round(average_player, 5, 7, 9, 0.28, seed=42)
        r2 = simulate_round(average_player, 5, 7, 9, 0.28, seed=42)
        assert r1 == r2

    def test_different_seeds_may_differ(self, average_player):
        """Different seeds should not be required to differ, but the mechanism works."""
        r1 = simulate_round(average_player, 5, 7, 9, 0.28, seed=1)
        r2 = simulate_round(average_player, 5, 7, 9, 0.28, seed=999)
        # At least the seed parameter is consumed without error
        assert r1 is not None and r2 is not None

    def test_remaining_health_bounds(self, average_player):
        """remaining_health stays between 0 and 100 for many seeds."""
        for seed in range(20):
            r = simulate_round(average_player, 5, 7, 9, 0.28, seed=seed)
            assert 0 <= r.remaining_health <= 100

    def test_damage_taken_bounds(self, average_player):
        """damage_taken stays between 0 and 100 for many seeds."""
        for seed in range(20):
            r = simulate_round(average_player, 5, 7, 9, 0.28, seed=seed)
            assert 0 <= r.damage_taken <= 100

    def test_accuracy_bounds(self, average_player):
        """accuracy stays between 0.0 and 1.0."""
        for seed in range(20):
            r = simulate_round(average_player, 5, 7, 9, 0.28, seed=seed)
            assert 0.0 <= r.accuracy <= 1.0

    def test_round_duration_positive(self, average_player):
        """round_duration must be greater than 0."""
        r = simulate_round(average_player, 5, 7, 9, 0.28, seed=42)
        assert r.round_duration > 0

    def test_invalid_difficulty_zero(self, average_player):
        """difficulty_level = 0 raises ValueError."""
        with pytest.raises(ValueError):
            simulate_round(average_player, 0, 7, 9, 0.28)

    def test_invalid_difficulty_eleven(self, average_player):
        """difficulty_level = 11 raises ValueError."""
        with pytest.raises(ValueError):
            simulate_round(average_player, 11, 7, 9, 0.28)

    def test_invalid_enemy_count_zero(self, average_player):
        """enemy_count = 0 raises ValueError."""
        with pytest.raises(ValueError):
            simulate_round(average_player, 5, 0, 9, 0.28)

    def test_invalid_enemy_damage_zero(self, average_player):
        """enemy_damage = 0 raises ValueError."""
        with pytest.raises(ValueError):
            simulate_round(average_player, 5, 7, 0, 0.28)

    def test_invalid_health_pack_rate_negative(self, average_player):
        """health_pack_rate < 0 raises ValueError."""
        with pytest.raises(ValueError):
            simulate_round(average_player, 5, 7, 9, -0.1)

    def test_invalid_health_pack_rate_above_one(self, average_player):
        """health_pack_rate > 1 raises ValueError."""
        with pytest.raises(ValueError):
            simulate_round(average_player, 5, 7, 9, 1.5)

    def test_result_fields_match_inputs(self, average_player):
        """Result records the exact difficulty, enemy_count, and enemy_damage used."""
        r = simulate_round(average_player, 5, 7, 9, 0.28, seed=0)
        assert r.difficulty_level == 5
        assert r.enemy_count == 7
        assert r.enemy_damage == 9


# ═══════════════════════════════════════════════════════════════════════════════
# 3. get_difficulty_settings
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetDifficultySettings:

    def test_all_levels_produce_valid_settings(self):
        """Levels 1–10 all return a DifficultySettings without error."""
        for level in range(1, 11):
            s = get_difficulty_settings(level)
            assert s.difficulty_level == level
            assert s.enemy_count > 0
            assert s.enemy_damage > 0
            assert 0.0 <= s.health_pack_rate <= 1.0

    def test_enemy_count_non_decreasing(self):
        """enemy_count must not decrease as difficulty rises."""
        counts = [get_difficulty_settings(d).enemy_count for d in range(1, 11)]
        for i in range(len(counts) - 1):
            assert counts[i] <= counts[i + 1]

    def test_enemy_damage_non_decreasing(self):
        """enemy_damage must not decrease as difficulty rises."""
        damages = [get_difficulty_settings(d).enemy_damage for d in range(1, 11)]
        for i in range(len(damages) - 1):
            assert damages[i] <= damages[i + 1]

    def test_health_pack_rate_non_increasing(self):
        """health_pack_rate must not increase as difficulty rises."""
        rates = [get_difficulty_settings(d).health_pack_rate for d in range(1, 11)]
        for i in range(len(rates) - 1):
            assert rates[i] >= rates[i + 1]

    def test_identical_difficulty_gives_identical_settings(self):
        """Two calls with the same level return equal objects."""
        s1 = get_difficulty_settings(5)
        s2 = get_difficulty_settings(5)
        assert s1 == s2

    def test_difficulty_zero_raises(self):
        """Level 0 raises ValueError."""
        with pytest.raises(ValueError):
            get_difficulty_settings(0)

    def test_difficulty_eleven_raises(self):
        """Level 11 raises ValueError."""
        with pytest.raises(ValueError):
            get_difficulty_settings(11)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. AdaptiveDifficultyAgent
# ═══════════════════════════════════════════════════════════════════════════════

class TestAdaptiveDifficultyAgent:

    def test_empty_results_keep(self, agent):
        """No history → agent keeps difficulty."""
        d = agent.decide(5, [])
        assert d.action == "keep"
        assert d.new_level == 5

    def test_three_consecutive_losses_decrease(self, agent):
        """Three straight losses → decrease."""
        results = [make_result(False)] * 3
        d = agent.decide(5, results)
        assert d.action == "decrease"
        assert d.new_level == 4

    def test_three_consecutive_wins_high_rate_increase(self, agent):
        """Three straight wins with win-rate above target → increase."""
        results = [make_result(True)] * 3
        d = agent.decide(5, results)
        assert d.action == "increase"
        assert d.new_level == 6

    def test_mixed_results_near_target_keep(self, agent):
        """3W/2L in window (60 % win rate) → keep."""
        results = [
            make_result(True),
            make_result(False),
            make_result(True),
            make_result(False),
            make_result(True),
        ]
        d = agent.decide(5, results)
        assert d.action == "keep"
        assert d.new_level == 5

    def test_lower_boundary_not_exceeded(self, agent):
        """Three losses at level 1 must not go below 1."""
        results = [make_result(False)] * 3
        d = agent.decide(1, results)
        assert d.new_level == 1

    def test_upper_boundary_not_exceeded(self, agent):
        """Three wins at level 10 must not exceed 10."""
        results = [make_result(True)] * 3
        d = agent.decide(10, results)
        assert d.new_level == 10

    def test_difficulty_changes_by_at_most_one(self, agent):
        """Any single decision changes the level by at most ±1."""
        for result_seq in [
            [make_result(True)] * 5,
            [make_result(False)] * 5,
        ]:
            d = agent.decide(5, result_seq)
            assert abs(d.new_level - d.previous_level) <= 1

    def test_invalid_target_win_rate_raises(self):
        """target_win_rate outside [0, 1] raises ValueError."""
        with pytest.raises(ValueError):
            AdaptiveDifficultyAgent(target_win_rate=1.5)

    def test_invalid_window_size_raises(self):
        """window_size <= 0 raises ValueError."""
        with pytest.raises(ValueError):
            AdaptiveDifficultyAgent(window_size=0)

    def test_invalid_min_difficulty_raises(self):
        """min_difficulty > max_difficulty raises ValueError."""
        with pytest.raises(ValueError):
            AdaptiveDifficultyAgent(min_difficulty=8, max_difficulty=4)

    def test_current_level_out_of_bounds_raises(self, agent):
        """current_level outside [min, max] raises ValueError."""
        with pytest.raises(ValueError):
            agent.decide(15, [])

    def test_decision_contains_reason(self, agent):
        """Every decision carries a non-empty reason string."""
        d = agent.decide(5, [make_result(True)] * 3)
        assert isinstance(d.reason, str)
        assert len(d.reason) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# 5. run_static_experiment / run_adaptive_experiment
# ═══════════════════════════════════════════════════════════════════════════════

class TestRunStaticExperiment:

    def test_correct_round_count(self, average_player):
        """Result contains exactly the requested number of rounds."""
        result = run_static_experiment(average_player, rounds=10,
                                       difficulty_level=5, seed=42)
        assert result.rounds == 10
        assert len(result.round_results) == 10

    def test_final_difficulty_equals_start(self, average_player):
        """Static experiment never changes difficulty."""
        result = run_static_experiment(average_player, rounds=10,
                                       difficulty_level=7, seed=42)
        assert result.final_difficulty == 7

    def test_no_difficulty_changes(self, average_player):
        """difficulty_changes is always 0 for static runs."""
        result = run_static_experiment(average_player, rounds=20,
                                       difficulty_level=5, seed=42)
        assert result.difficulty_changes == 0

    def test_no_decisions(self, average_player):
        """Static runs have an empty decisions list."""
        result = run_static_experiment(average_player, rounds=10,
                                       difficulty_level=5, seed=42)
        assert result.decisions == []

    def test_reproducible_with_same_seed(self, average_player):
        """Same seed produces identical overall_win_rate."""
        r1 = run_static_experiment(average_player, 15, 5, seed=77)
        r2 = run_static_experiment(average_player, 15, 5, seed=77)
        assert r1.overall_win_rate == r2.overall_win_rate
        assert r1.total_wins == r2.total_wins


class TestRunAdaptiveExperiment:

    def test_correct_round_count(self, average_player):
        """Result contains exactly the requested number of rounds."""
        result = run_adaptive_experiment(average_player, rounds=10,
                                         initial_difficulty=5, seed=42)
        assert result.rounds == 10
        assert len(result.round_results) == 10

    def test_decisions_count_matches_rounds(self, average_player):
        """One agent decision per round."""
        result = run_adaptive_experiment(average_player, rounds=10,
                                         initial_difficulty=5, seed=42)
        assert len(result.decisions) == 10

    def test_final_difficulty_in_bounds(self, average_player):
        """Final difficulty stays within [1, 10]."""
        result = run_adaptive_experiment(average_player, rounds=30,
                                         initial_difficulty=5, seed=42)
        assert 1 <= result.final_difficulty <= 10

    def test_reproducible_with_same_seed(self, average_player):
        """Same seed produces identical results."""
        r1 = run_adaptive_experiment(average_player, 20, 5, seed=42)
        r2 = run_adaptive_experiment(average_player, 20, 5, seed=42)
        assert r1.overall_win_rate == r2.overall_win_rate
        assert r1.final_difficulty == r2.final_difficulty

    def test_beginner_high_difficulty_gets_adapted(self, beginner_player):
        """Beginner starting at difficulty 9 should get at least one reduction."""
        result = run_adaptive_experiment(beginner_player, rounds=20,
                                         initial_difficulty=9, seed=42)
        assert result.difficulty_changes >= 1

    def test_expert_low_difficulty_may_increase(self, expert_player):
        """Expert starting at difficulty 1 should receive at least one increase."""
        result = run_adaptive_experiment(expert_player, rounds=15,
                                         initial_difficulty=1, seed=42)
        assert result.difficulty_changes >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# 6. run_comparison_experiments
# ═══════════════════════════════════════════════════════════════════════════════

class TestRunComparisonExperiments:

    @pytest.fixture
    def three_players(self) -> List[PlayerProfile]:
        return create_default_players()

    def test_expected_experiment_count(self, three_players, tmp_path):
        """3 players × 2 seeds × 2 systems = 12 ExperimentResult objects."""
        csv_file = str(tmp_path / "out.csv")
        results = run_comparison_experiments(
            three_players,
            rounds_per_experiment=20,
            initial_difficulty=5,
            seeds=[42, 77],
            output_path=csv_file,
        )
        assert len(results) == 12  # 3 players × 2 seeds × 2 types

    def test_csv_file_is_created(self, three_players, tmp_path):
        """Output CSV must be written to the given path."""
        csv_file = str(tmp_path / "results.csv")
        run_comparison_experiments(
            three_players, 20, 5, seeds=[42], output_path=csv_file
        )
        assert (tmp_path / "results.csv").exists()

    def test_csv_has_header(self, three_players, tmp_path):
        """CSV first row must be the column header."""
        csv_file = str(tmp_path / "results.csv")
        run_comparison_experiments(
            three_players, 20, 5, seeds=[42], output_path=csv_file
        )
        with open(csv_file, encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
        assert "system_type" in header
        assert "player_name" in header

    def test_static_runs_have_zero_changes(self, three_players, tmp_path):
        """All static ExperimentResults must have difficulty_changes == 0."""
        csv_file = str(tmp_path / "out.csv")
        results = run_comparison_experiments(
            three_players, 20, 5, seeds=[42], output_path=csv_file
        )
        static_results = [r for r in results if r.system_type == "static"]
        assert all(r.difficulty_changes == 0 for r in static_results)

    def test_adaptive_final_difficulty_in_bounds(self, three_players, tmp_path):
        """All adaptive final difficulties remain between 1 and 10."""
        csv_file = str(tmp_path / "out.csv")
        results = run_comparison_experiments(
            three_players, 20, 5, seeds=[42], output_path=csv_file
        )
        adaptive_results = [r for r in results if r.system_type == "adaptive"]
        assert all(1 <= r.final_difficulty <= 10 for r in adaptive_results)

    def test_empty_players_raises(self, tmp_path):
        """Empty players list raises ValueError."""
        with pytest.raises(ValueError):
            run_comparison_experiments([], 20, 5,
                                       output_path=str(tmp_path / "x.csv"))

    def test_rounds_zero_raises(self, three_players, tmp_path):
        """rounds_per_experiment = 0 raises ValueError."""
        with pytest.raises(ValueError):
            run_comparison_experiments(three_players, 0, 5,
                                       output_path=str(tmp_path / "x.csv"))

    def test_invalid_difficulty_raises(self, three_players, tmp_path):
        """initial_difficulty = 11 raises ValueError."""
        with pytest.raises(ValueError):
            run_comparison_experiments(three_players, 20, 11,
                                       output_path=str(tmp_path / "x.csv"))

    def test_empty_seeds_raises(self, three_players, tmp_path):
        """Empty seeds list raises ValueError."""
        with pytest.raises(ValueError):
            run_comparison_experiments(three_players, 20, 5, seeds=[],
                                       output_path=str(tmp_path / "x.csv"))

    def test_reproducible_with_same_seeds(self, three_players, tmp_path):
        """Two runs with the same seeds produce identical overall_win_rates."""
        f1 = str(tmp_path / "r1.csv")
        f2 = str(tmp_path / "r2.csv")
        res1 = run_comparison_experiments(three_players, 20, 5, [42, 77],
                                          output_path=f1)
        res2 = run_comparison_experiments(three_players, 20, 5, [42, 77],
                                          output_path=f2)
        for r1, r2 in zip(res1, res2):
            assert r1.overall_win_rate == r2.overall_win_rate


# ═══════════════════════════════════════════════════════════════════════════════
# 7. main.py helpers
# ═══════════════════════════════════════════════════════════════════════════════

class TestSelectPlayer:

    def test_beginner(self):
        """select_player('beginner') returns a low-skill profile."""
        p = select_player("beginner")
        assert isinstance(p, PlayerProfile)
        assert p.skill_level < 0.5

    def test_average(self):
        """select_player('average') returns a mid-skill profile."""
        p = select_player("average")
        assert isinstance(p, PlayerProfile)
        assert 0.4 <= p.skill_level <= 0.8

    def test_expert(self):
        """select_player('expert') returns a high-skill profile."""
        p = select_player("expert")
        assert isinstance(p, PlayerProfile)
        assert p.skill_level > 0.7

    def test_invalid_key_raises(self):
        """Unknown player key raises KeyError (dict lookup)."""
        with pytest.raises(KeyError):
            select_player("god_mode")


class TestComputeWinRates:

    def _history(self, pattern: List[bool]) -> List[GameRoundResult]:
        return [make_result(v) for v in pattern]

    def test_all_wins(self):
        """100 % win history → both rates are 1.0."""
        h = self._history([True] * 5)
        overall, window = compute_win_rates(h, window_size=5)
        assert overall == pytest.approx(1.0)
        assert window == pytest.approx(1.0)

    def test_all_losses(self):
        """0 % win history → both rates are 0.0."""
        h = self._history([False] * 5)
        overall, window = compute_win_rates(h, window_size=5)
        assert overall == pytest.approx(0.0)
        assert window == pytest.approx(0.0)

    def test_mixed_overall_rate(self):
        """2 wins out of 4 rounds → overall_win_rate = 0.5."""
        h = self._history([True, False, True, False])
        overall, _ = compute_win_rates(h, window_size=5)
        assert overall == pytest.approx(0.5)

    def test_window_smaller_than_history(self):
        """Window covers only the last N rounds, not all of them."""
        # First 5 losses, last 5 wins → window rate should be 1.0
        h = self._history([False] * 5 + [True] * 5)
        overall, window = compute_win_rates(h, window_size=5)
        assert overall == pytest.approx(0.5)
        assert window == pytest.approx(1.0)

    def test_window_larger_than_history(self):
        """When history is shorter than window, window covers all rounds."""
        h = self._history([True, False])  # 2 rounds, window_size=5
        overall, window = compute_win_rates(h, window_size=5)
        assert overall == pytest.approx(0.5)
        assert window == pytest.approx(0.5)

    def test_single_win(self):
        """Single winning round → both rates are 1.0."""
        h = self._history([True])
        overall, window = compute_win_rates(h, window_size=5)
        assert overall == pytest.approx(1.0)
        assert window == pytest.approx(1.0)

    def test_single_loss(self):
        """Single losing round -> both rates are 0.0."""
        h = self._history([False])
        overall, window = compute_win_rates(h, window_size=5)
        assert overall == pytest.approx(0.0)
        assert window == pytest.approx(0.0)


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Reaction test – calculate_reaction_score
# ═══════════════════════════════════════════════════════════════════════════════

from src.reaction_test import (
    calculate_reaction_score,
    classify_reaction_time,
    create_reaction_profile,
    evaluate_reaction_times,
    run_reaction_test,
    ReactionTestResult,
)


class TestCalculateReactionScore:

    def test_fast_threshold_returns_one(self):
        """150 ms returns exactly 1.0."""
        assert calculate_reaction_score(150.0) == pytest.approx(1.0)

    def test_slow_threshold_returns_zero(self):
        """500 ms returns exactly 0.0."""
        assert calculate_reaction_score(500.0) == pytest.approx(0.0)

    def test_midpoint_returns_approx_half(self):
        """325 ms (midpoint) returns approximately 0.5."""
        assert calculate_reaction_score(325.0) == pytest.approx(0.5, abs=1e-6)

    def test_below_fast_threshold_clamped_to_one(self):
        """Values faster than 150 ms remain clamped at 1.0."""
        assert calculate_reaction_score(50.0) == pytest.approx(1.0)
        assert calculate_reaction_score(1.0) == pytest.approx(1.0)

    def test_above_slow_threshold_clamped_to_zero(self):
        """Values slower than 500 ms remain clamped at 0.0."""
        assert calculate_reaction_score(600.0) == pytest.approx(0.0)
        assert calculate_reaction_score(1000.0) == pytest.approx(0.0)

    def test_zero_raises(self):
        """0 ms raises ValueError."""
        with pytest.raises(ValueError):
            calculate_reaction_score(0.0)

    def test_negative_raises(self):
        """Negative values raise ValueError."""
        with pytest.raises(ValueError):
            calculate_reaction_score(-1.0)


# ═══════════════════════════════════════════════════════════════════════════════
# 9. Reaction test – classify_reaction_time
# ═══════════════════════════════════════════════════════════════════════════════

class TestClassifyReactionTime:

    def test_219_is_expert(self):
        """219 ms is below the 220 ms expert threshold."""
        assert classify_reaction_time(219.0) == "expert"

    def test_220_is_average(self):
        """220 ms is the lower boundary of the average range."""
        assert classify_reaction_time(220.0) == "average"

    def test_349_is_average(self):
        """349 ms is just below the 350 ms beginner threshold."""
        assert classify_reaction_time(349.0) == "average"

    def test_350_is_beginner(self):
        """350 ms is the lower boundary of the beginner range."""
        assert classify_reaction_time(350.0) == "beginner"

    def test_zero_raises(self):
        """0 ms raises ValueError."""
        with pytest.raises(ValueError):
            classify_reaction_time(0.0)

    def test_negative_raises(self):
        """Negative values raise ValueError."""
        with pytest.raises(ValueError):
            classify_reaction_time(-10.0)


# ═══════════════════════════════════════════════════════════════════════════════
# 10. Reaction test – evaluate_reaction_times
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvaluateReactionTimes:

    def test_median_calculated_correctly(self):
        """Median of [200, 300, 400] is 300."""
        result = evaluate_reaction_times([200.0, 300.0, 400.0])
        assert result.median_reaction_time_ms == pytest.approx(300.0)

    def test_result_contains_all_measurements(self):
        """reaction_times_ms list matches the input exactly."""
        times = [250.0, 270.0, 260.0]
        result = evaluate_reaction_times(times)
        assert result.reaction_times_ms == times

    def test_score_in_valid_range(self):
        """reaction_score is always between 0.0 and 1.0."""
        for times in [
            [100.0, 120.0, 130.0],
            [300.0, 350.0, 320.0],
            [600.0, 700.0, 650.0],
        ]:
            result = evaluate_reaction_times(times)
            assert 0.0 <= result.reaction_score <= 1.0

    def test_category_is_correct(self):
        """Category matches the median value."""
        # median = 200 -> expert
        result = evaluate_reaction_times([180.0, 200.0, 220.0])
        # median of [180, 200, 220] is 200, which is < 220 -> expert
        assert result.profile_category == "expert"

    def test_category_average(self):
        """Median in [220, 350) -> average."""
        result = evaluate_reaction_times([220.0, 280.0, 340.0])
        assert result.profile_category == "average"

    def test_category_beginner(self):
        """Median >= 350 -> beginner."""
        result = evaluate_reaction_times([350.0, 400.0, 450.0])
        assert result.profile_category == "beginner"

    def test_fewer_than_three_measurements_raises(self):
        """Fewer than 3 measurements raise ValueError."""
        with pytest.raises(ValueError):
            evaluate_reaction_times([200.0, 300.0])

    def test_empty_list_raises(self):
        """Empty list raises ValueError."""
        with pytest.raises(ValueError):
            evaluate_reaction_times([])

    def test_zero_measurement_raises(self):
        """A measurement of 0 raises ValueError."""
        with pytest.raises(ValueError):
            evaluate_reaction_times([200.0, 0.0, 300.0])

    def test_negative_measurement_raises(self):
        """A negative measurement raises ValueError."""
        with pytest.raises(ValueError):
            evaluate_reaction_times([200.0, -50.0, 300.0])


# ═══════════════════════════════════════════════════════════════════════════════
# 11. Reaction test – create_reaction_profile
# ═══════════════════════════════════════════════════════════════════════════════

class TestCreateReactionProfile:

    def test_returns_player_profile_type(self):
        """Returns an instance of PlayerProfile."""
        from src.player import PlayerProfile as PP
        profile = create_reaction_profile(300.0)
        assert isinstance(profile, PP)

    def test_name_is_correct(self):
        """Profile name must be 'Reaktionstest-Spieler'."""
        profile = create_reaction_profile(300.0)
        assert profile.name == "Reaktionstest-Spieler"

    def test_reaction_speed_matches_calculated_value(self):
        """reaction_speed equals calculate_reaction_score for the given time."""
        ms = 325.0
        profile = create_reaction_profile(ms)
        expected = calculate_reaction_score(ms)
        assert profile.reaction_speed == pytest.approx(expected)

    def test_skill_level_is_fixed(self):
        """skill_level is always 0.60."""
        assert create_reaction_profile(300.0).skill_level == pytest.approx(0.60)

    def test_accuracy_is_fixed(self):
        """accuracy is always 0.60."""
        assert create_reaction_profile(300.0).accuracy == pytest.approx(0.60)

    def test_survival_factor_is_fixed(self):
        """survival_factor is always 0.65."""
        assert create_reaction_profile(300.0).survival_factor == pytest.approx(0.65)

    def test_invalid_reaction_time_raises(self):
        """Passing 0 or negative raises ValueError."""
        with pytest.raises(ValueError):
            create_reaction_profile(0.0)
        with pytest.raises(ValueError):
            create_reaction_profile(-100.0)


# ═══════════════════════════════════════════════════════════════════════════════
# 12. Reaction test – run_reaction_test (with monkeypatching)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRunReactionTest:
    """Tests for the interactive terminal function.

    time.sleep is replaced with a no-op so tests do not actually wait.
    time.perf_counter is replaced to simulate deterministic elapsed times.
    builtins.input is replaced with a function that returns empty strings.
    """

    def _make_perf_counter(self, elapsed_seconds: float):
        """Return a callable that alternates between 0.0 and elapsed_seconds."""
        calls = [0]

        def fake_perf_counter():
            result = 0.0 if calls[0] % 2 == 0 else elapsed_seconds
            calls[0] += 1
            return result

        return fake_perf_counter

    def test_correct_number_of_measurements(self, monkeypatch):
        """Result contains exactly as many measurements as attempts."""
        monkeypatch.setattr("builtins.input", lambda *args, **kwargs: "")
        monkeypatch.setattr("time.sleep", lambda _: None)
        monkeypatch.setattr(
            "time.perf_counter", self._make_perf_counter(0.25)
        )

        result = run_reaction_test(attempts=3, seed=0)
        assert len(result.reaction_times_ms) == 3

    def test_returned_result_is_valid(self, monkeypatch):
        """Returned object is a ReactionTestResult with consistent data."""
        monkeypatch.setattr("builtins.input", lambda *args, **kwargs: "")
        monkeypatch.setattr("time.sleep", lambda _: None)
        monkeypatch.setattr(
            "time.perf_counter", self._make_perf_counter(0.30)
        )

        result = run_reaction_test(attempts=4, seed=1)

        assert isinstance(result, ReactionTestResult)
        assert result.median_reaction_time_ms > 0
        assert 0.0 <= result.reaction_score <= 1.0
        assert result.profile_category in ("expert", "average", "beginner")

    def test_too_few_attempts_raises(self):
        """attempts < 3 raises ValueError before any I/O occurs."""
        with pytest.raises(ValueError):
            run_reaction_test(attempts=2)

    def test_zero_min_wait_raises(self):
        """min_wait_seconds = 0 raises ValueError."""
        with pytest.raises(ValueError):
            run_reaction_test(min_wait_seconds=0.0)

    def test_zero_max_wait_raises(self):
        """max_wait_seconds = 0 raises ValueError."""
        with pytest.raises(ValueError):
            run_reaction_test(max_wait_seconds=0.0)

    def test_min_greater_than_max_raises(self):
        """min_wait_seconds > max_wait_seconds raises ValueError."""
        with pytest.raises(ValueError):
            run_reaction_test(min_wait_seconds=3.0, max_wait_seconds=1.0)

