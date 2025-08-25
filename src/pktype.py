"""
Enum for each Pokemon type.
"""

from enum import Enum, auto

type_code = {
    "NORMAL": "NRM",
    "FIRE": "FIR",
    "WATER": "WTR",
    "GRASS": "GRS",
    "BUG": "BUG",
    "POISON": "PSN",
    "ELECTRIC": "ELC",
    "GROUND": "GRD",
    "FIGHTING": "FGT",
    "PSYCHIC": "PSY",
    "ROCK": "RCK",
    "GHOST": "GHT",
    "ICE": "ICE",
    "DRAGON": "DRG",
    "DARK": "DRK",
    "STEEL": "STL",
    "FLYING": "FLY",
    "FAIRY": "FRY",
}


class PKType(Enum):
    NORMAL = auto()
    FIRE = auto()
    WATER = auto()
    ELECTRIC = auto()
    GRASS = auto()
    ICE = auto()
    FIGHTING = auto()
    POISON = auto()
    GROUND = auto()
    FLYING = auto()
    PSYCHIC = auto()
    BUG = auto()
    ROCK = auto()
    GHOST = auto()
    DRAGON = auto()
    DARK = auto()
    STEEL = auto()
    FAIRY = auto()

    def code(self) -> str:
        return type_code[self.name]

    def resistances(self) -> dict["PKType", float]:
        """
        Returns a dictionary of damage multipliers for this type that are less than one.

        :return: A dictionary with types as keys and their respective damage multipliers as values.
        """
        # return {PKType[attacker]: multiplier for attacker, multiplier in mults.items() if multiplier < 1.0}
        mults = get_all_notable_defender_multipliers(self)
        result = {}
        for attacker, mult in mults.items():
            if mult < 1.0:
                result[attacker] = mult
        return result

    def weaknesses(self) -> dict["PKType", float]:
        """
        Returns a dictionary of damage multipliers for this type that are greater than one.

        :return: A dictionary with types as keys and their respective damage multipliers as values.
        """
        mults = get_all_notable_defender_multipliers(self)
        result = {}
        for attacker, mult in mults.items():
            if mult > 1.0:
                result[attacker] = mult
        return result


# Flips the damage multiplier to get the defending type's perspective.
# Flipped veresion of the get_attack_damage_multiplier function.
def get_all_notable_defender_multipliers(
    defender: PKType, all: bool = False
) -> dict[PKType, float]:
    """
    Returns a dictionary of damage multipliers for a defending Pokémon type against all attacking types.

    :param defender: The type of the defending Pokémon (PKType).
    :return: A dictionary with attacking types as keys and their respective damage multipliers as values.
    """
    result = {}
    for attacker in PKType:
        multiplier = get_attack_damage_multiplier(attacker, defender)
        if all or (multiplier != 1.0):
            # Only include types that have a multiplier other than 1.0
            result.update({attacker: multiplier})
    return result
    # return {attacker: get_attack_damage_multiplier(PKType[attacker], defender) for attacker in PKType.__members__}


def get_attack_damage_multiplier(attacker: PKType, defender: PKType) -> float:
    """
    Returns the damage multiplier for an attack from attacker_type to defender_type.

    :param attacker_type: The type of the attacking Pokémon (PKType).
    :param defender_type: The type of the defending Pokémon (PKType).
    :return: Damage multiplier as a float.
    """
    attacker = attacker.name.upper()
    defender = defender.name.lower()
    return damage_multiplier.get(attacker, {}).get(
        defender, 1.0
    )  # Default to 1.0 if no multiplier found
