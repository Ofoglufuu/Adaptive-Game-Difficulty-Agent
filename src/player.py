"""
Player modeling for the Adaptive Game Difficulty Agent.
"""
from typing import List

class PlayerProfile:
    """
    Represents a player with specific skills and attributes.
    All numeric attributes must be between 0.0 and 1.0.
    """

    def __init__(self, name: str, skill_level: float, accuracy: float, 
                 reaction_speed: float, survival_factor: float):
        self._validate_name(name)
        self.name = name
        
        self._validate_metric(skill_level, "skill_level")
        self.skill_level = skill_level
        
        self._validate_metric(accuracy, "accuracy")
        self.accuracy = accuracy
        
        self._validate_metric(reaction_speed, "reaction_speed")
        self.reaction_speed = reaction_speed
        
        self._validate_metric(survival_factor, "survival_factor")
        self.survival_factor = survival_factor

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name or not name.strip():
            raise ValueError("Player name cannot be empty.")

    @staticmethod
    def _validate_metric(value: float, metric_name: str) -> None:
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"{metric_name} must be between 0.0 and 1.0. Got: {value}")

    def __str__(self) -> str:
        return (f"PlayerProfile(name='{self.name}', "
                f"skill={self.skill_level:.2f}, "
                f"accuracy={self.accuracy:.2f}, "
                f"reaction={self.reaction_speed:.2f}, "
                f"survival={self.survival_factor:.2f})")


def create_default_players() -> List[PlayerProfile]:
    """
    Creates and returns a list of predefined default player profiles.
    """
    return [
        PlayerProfile(
            name="Anfänger",
            skill_level=0.35,
            accuracy=0.30,
            reaction_speed=0.25,
            survival_factor=0.40
        ),
        PlayerProfile(
            name="durchschnittlicher Spieler",
            skill_level=0.60,
            accuracy=0.60,
            reaction_speed=0.55,
            survival_factor=0.65
        ),
        PlayerProfile(
            name="erfahrener Spieler",
            skill_level=0.85,
            accuracy=0.85,
            reaction_speed=0.80,
            survival_factor=0.90
        )
    ]

if __name__ == "__main__":
    print("--- Default Players ---")
    players = create_default_players()
    for p in players:
        print(p)

    print("\n--- Testing Invalid Inputs ---")
    try:
        PlayerProfile(name="", skill_level=0.5, accuracy=0.5, reaction_speed=0.5, survival_factor=0.5)
        print("FAIL: Expected ValueError for empty name.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")

    try:
        PlayerProfile(name="InvalidPlayer", skill_level=1.5, accuracy=0.5, reaction_speed=0.5, survival_factor=0.5)
        print("FAIL: Expected ValueError for skill_level > 1.0.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")

    try:
        PlayerProfile(name="InvalidPlayer", skill_level=0.5, accuracy=-0.2, reaction_speed=0.5, survival_factor=0.5)
        print("FAIL: Expected ValueError for accuracy < 0.0.")
    except ValueError as e:
        print(f"SUCCESS (Expected Error): {e}")
