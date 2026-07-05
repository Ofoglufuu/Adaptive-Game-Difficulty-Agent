"""
Reaction test module for the Adaptive Game Difficulty Agent.

Provides an interactive terminal-based reaction time measurement that
produces a reaction-based profile estimation for use in the adaptive
live demo.

All user-facing terminal output is in German; code, docstrings, and
function/variable names remain in English.
"""

import random
import statistics
import time
from dataclasses import dataclass
from typing import Optional

from src.player import PlayerProfile


# ── Constants ─────────────────────────────────────────────────────────────────

_FAST_THRESHOLD_MS: float = 150.0   # reaction_score = 1.0
_SLOW_THRESHOLD_MS: float = 500.0   # reaction_score = 0.0

_EXPERT_THRESHOLD_MS: float  = 220.0
_AVERAGE_THRESHOLD_MS: float = 350.0

_MIN_VALID_MEASUREMENTS: int = 3


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class ReactionTestResult:
    """Stores the outcome of a complete reaction test session."""

    reaction_times_ms: list
    median_reaction_time_ms: float
    reaction_score: float
    profile_category: str


# ── Core calculation functions ────────────────────────────────────────────────

def calculate_reaction_score(reaction_time_ms: float) -> float:
    """Convert a reaction time in milliseconds to a score in [0.0, 1.0].

    Linear mapping:
        - 150 ms or faster -> 1.0
        - 500 ms or slower -> 0.0
        - values in between are linearly interpolated

    Args:
        reaction_time_ms: Reaction time in milliseconds. Must be > 0.

    Returns:
        A float score clamped to [0.0, 1.0].

    Raises:
        ValueError: If reaction_time_ms <= 0.
    """
    if reaction_time_ms <= 0:
        raise ValueError(
            f"reaction_time_ms must be greater than 0, got {reaction_time_ms}."
        )

    score = (
        (_SLOW_THRESHOLD_MS - reaction_time_ms)
        / (_SLOW_THRESHOLD_MS - _FAST_THRESHOLD_MS)
    )
    return max(0.0, min(1.0, score))


def classify_reaction_time(reaction_time_ms: float) -> str:
    """Classify a reaction time into a named category.

    Categories:
        - "expert"   : below 220 ms
        - "average"  : 220 ms up to (but not including) 350 ms
        - "beginner" : 350 ms and above

    Args:
        reaction_time_ms: Reaction time in milliseconds. Must be > 0.

    Returns:
        One of "expert", "average", or "beginner".

    Raises:
        ValueError: If reaction_time_ms <= 0.
    """
    if reaction_time_ms <= 0:
        raise ValueError(
            f"reaction_time_ms must be greater than 0, got {reaction_time_ms}."
        )

    if reaction_time_ms < _EXPERT_THRESHOLD_MS:
        return "expert"
    if reaction_time_ms < _AVERAGE_THRESHOLD_MS:
        return "average"
    return "beginner"


# ── Profile creation ──────────────────────────────────────────────────────────

def create_reaction_profile(median_reaction_time_ms: float) -> PlayerProfile:
    """Create a personalized PlayerProfile based on measured reaction time.

    Only ``reaction_speed`` is personalised; the remaining attributes are
    set to typical average-player values so that the profile is not
    misrepresented as a full skill assessment.

    Args:
        median_reaction_time_ms: Median reaction time in milliseconds.
            Must be > 0.

    Returns:
        A PlayerProfile with a personalised reaction_speed.

    Raises:
        ValueError: If median_reaction_time_ms <= 0.
    """
    reaction_speed = calculate_reaction_score(median_reaction_time_ms)

    return PlayerProfile(
        name="Reaktionstest-Spieler",
        skill_level=0.60,
        accuracy=0.60,
        reaction_speed=reaction_speed,
        survival_factor=0.65,
    )


# ── Evaluation ────────────────────────────────────────────────────────────────

def evaluate_reaction_times(reaction_times_ms: list) -> ReactionTestResult:
    """Evaluate a list of raw reaction time measurements.

    Args:
        reaction_times_ms: List of measured reaction times in milliseconds.
            Must contain at least 3 values, all greater than 0.

    Returns:
        A fully populated ReactionTestResult.

    Raises:
        ValueError: If fewer than 3 measurements are provided, or if any
            value is <= 0.
    """
    if len(reaction_times_ms) < _MIN_VALID_MEASUREMENTS:
        raise ValueError(
            f"At least {_MIN_VALID_MEASUREMENTS} measurements are required, "
            f"got {len(reaction_times_ms)}."
        )

    for value in reaction_times_ms:
        if value <= 0:
            raise ValueError(
                f"All reaction times must be > 0, got {value}."
            )

    median_ms = statistics.median(reaction_times_ms)
    score = calculate_reaction_score(median_ms)
    category = classify_reaction_time(median_ms)

    return ReactionTestResult(
        reaction_times_ms=list(reaction_times_ms),
        median_reaction_time_ms=float(median_ms),
        reaction_score=round(score, 4),
        profile_category=category,
    )


# ── Interactive test ──────────────────────────────────────────────────────────

def run_reaction_test(
    attempts: int = 5,
    min_wait_seconds: float = 1.0,
    max_wait_seconds: float = 3.0,
    seed: Optional[int] = None,
) -> ReactionTestResult:
    """Run an interactive terminal reaction test.

    The user presses Enter to start each attempt. After a random delay the
    prompt "JETZT!" is displayed. The elapsed time until the next Enter
    press is recorded.

    The random delays are generated with ``random.Random(seed)`` so that
    the waiting sequence is reproducible when a seed is provided. Human
    reaction times are naturally not reproducible.

    Args:
        attempts:          Number of reaction-time measurements to collect.
                           Must be >= 3.
        min_wait_seconds:  Minimum random delay before "JETZT!" in seconds.
                           Must be > 0.
        max_wait_seconds:  Maximum random delay before "JETZT!" in seconds.
                           Must be > 0 and >= min_wait_seconds.
        seed:              Optional seed for the random delay generator.

    Returns:
        A ReactionTestResult containing all measurements and derived stats.

    Raises:
        ValueError: If any parameter is out of range.
    """
    # ── Input validation ──────────────────────────────────────────────────────
    if attempts < _MIN_VALID_MEASUREMENTS:
        raise ValueError(
            f"attempts must be >= {_MIN_VALID_MEASUREMENTS}, got {attempts}."
        )
    if min_wait_seconds <= 0:
        raise ValueError(
            f"min_wait_seconds must be > 0, got {min_wait_seconds}."
        )
    if max_wait_seconds <= 0:
        raise ValueError(
            f"max_wait_seconds must be > 0, got {max_wait_seconds}."
        )
    if min_wait_seconds > max_wait_seconds:
        raise ValueError(
            f"min_wait_seconds ({min_wait_seconds}) must not exceed "
            f"max_wait_seconds ({max_wait_seconds})."
        )

    rng = random.Random(seed)

    print()
    print("======================================================")
    print("         REAKTIONSZEIT-TEST")
    print("======================================================")
    print()
    print(f"  Es werden {attempts} Messungen durchgefuehrt.")
    print("  Druecke Enter, um jeden Versuch zu starten.")
    print("  Wenn 'JETZT!' erscheint, druecke sofort Enter.")
    print("  Hinweis: Dies ist eine reaktionsbasierte Profileinschaetzung,")
    print("           keine wissenschaftliche Skillbewertung.")
    print()

    reaction_times_ms = []

    for attempt_num in range(1, attempts + 1):
        input(f"  Versuch {attempt_num}/{attempts} - Druecke Enter zum Starten ...")

        wait_seconds = rng.uniform(min_wait_seconds, max_wait_seconds)
        time.sleep(wait_seconds)

        print("  JETZT!", flush=True)
        t_start = time.perf_counter()
        input()
        t_end = time.perf_counter()

        elapsed_ms = (t_end - t_start) * 1000.0
        reaction_times_ms.append(elapsed_ms)
        print(f"  -> Reaktionszeit: {elapsed_ms:.0f} ms")
        print()

    # ── Evaluate all measurements ─────────────────────────────────────────────
    result = evaluate_reaction_times(reaction_times_ms)

    measurements_str = ", ".join(f"{t:.0f} ms" for t in result.reaction_times_ms)

    print("Reaktionstest abgeschlossen")
    print()
    print("Messungen:")
    print(f"  {measurements_str}")
    print()
    print(f"Median: {result.median_reaction_time_ms:.0f} ms")
    print(f"Reaktionswert: {result.reaction_score:.2f}")
    print(f"Reaktionsbasierte Profileinschaetzung: {result.profile_category}")

    return result
