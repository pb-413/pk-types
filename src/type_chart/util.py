"""
Utilities for working with type charts.
"""
from .gen_6 import damage_multiplier as gen_6_chart


def get_attack_damage_multiplier(
        attacker: str, defender: str, damage_multiplier: dict = gen_6_chart
) -> float:
    """
    Returns the damage multiplier for an attack from attacker_type to defender_type.

    Does not account for multiple types.

    :param attacker_type: The type of the attacking Pokémon (PKType.name).
    :param defender_type: The type of the defending Pokémon (PKType.name).
    :return: Damage multiplier as a float.
    """
    attacker = attacker.upper()
    defender = defender.lower()
    return damage_multiplier.get(attacker, {}).get(
        defender, 1.0
    )  # Default to 1.0 if no multiplier found


def get_attack_damage_multiplier_or_none(
    attacker: str, defender: str, damage_multiplier: dict = gen_6_chart
) -> float:  # Or None
    """
    Returns the damage multiplier for an attack from attacker_type to defender_type, or None if not found.

    :param attacker: The type of the attacking Pokémon (PKType.name).
    :param defender: The type of the defending Pokémon (PKType.name).
    :return: Damage multiplier as a float, or None if no multiplier is found.
    """
    attacker = attacker.upper()
    defender = defender.lower()
    return damage_multiplier.get(attacker, {}).get(
        defender, None
    )  # Return None if no multiplier found
