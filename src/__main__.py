from enum import Enum, auto

from type_chart.gen_6 import damage_multiplier as damage_multiplier


def _subset_gt_lt_one(
    damage_dict: dict[str, float], threshold: float, gt: bool = True
) -> dict[str, float]:
    """
    Returns a subset of the damage_dict where values are either greater than or less than the threshold.

    :param damage_dict: Dictionary with types as keys and their respective damage multipliers as values.
    :param threshold: The threshold value to compare against.
    :param gt: If True, returns values greater than the threshold; if False, returns values less than the threshold.
    :return: A dictionary with filtered types and their multipliers.
    """
    if gt:
        return {k: v for k, v in damage_dict.items() if v > threshold}
    else:
        return {k: v for k, v in damage_dict.items() if v < threshold}


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


def get_attack_damage_multiplier_or_none(
    attacker: PKType, defender: PKType
) -> float:  # Or None
    """
    Returns the damage multiplier for an attack from attacker_type to defender_type, or None if not found.

    :param attacker: The type of the attacking Pokémon (PKType).
    :param defender: The type of the defending Pokémon (PKType).
    :return: Damage multiplier as a float, or None if no multiplier is found.
    """
    attacker = attacker.name.upper()
    defender = defender.name.lower()
    return damage_multiplier.get(attacker, {}).get(
        defender, None
    )  # Return None if no multiplier found


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


def test_get_resistances():
    """
    Test function to verify the get_resistances function.
    """
    for type_ in PKType:
        resistances = get_all_notable_defender_multipliers(type_)
        print(f"{type_.name} resistances:")
        for attacker, multiplier in resistances.items():
            print(f"  {attacker.name}: {multiplier}")
        print()


def test_enum_weaknesses_and_resistances():
    """
    Test function to verify the weaknesses and resistances of each PKType.
    """
    for type_ in PKType:
        print(f"{type_.name} weaknesses: {type_.weaknesses()}")
        print(f"{type_.name} resistances: {type_.resistances()}")
        print()


def combine_types_notables(type_1: PKType, type_2: PKType):
    """
    Using two types, returns a dictionary of notable multipliers for the combined type.
    """
    combined = {}
    t1_notes = get_all_notable_defender_multipliers(type_1)
    t2_notes = get_all_notable_defender_multipliers(type_2)

    for attacker, mult in t1_notes.items():
        if attacker in t2_notes:
            combined[attacker] = mult * t2_notes[attacker]
        else:
            combined[attacker] = mult

    for attacker, mult in t2_notes.items():
        if attacker not in combined:
            combined[attacker] = mult

    return combined


def rank_types_and_combos_on_the_fly():
    result: dict[str:float] = {}
    for type_1 in PKType:
        if not type_1.name in result:
            result[type_1.name] = {}
            # Rank the type by its resistances to weaknesses ratio
            result[type_1.name] = float(len(type_1.resistances())) / len(
                type_1.weaknesses()
            )
        for type_2 in PKType:
            if type_1 == type_2:
                continue
            types = [type_1, type_2]
            # Sort to avoid duplicates like "FIRE + WATER" and "WATER + FIRE"
            types.sort(key=lambda x: x.name)
            combo = " + ".join([t.name for t in types])
            if combo in result:
                continue
            if combo not in result:
                notes = combine_types_notables(type_1, type_2)
                weaknesses = _subset_gt_lt_one(notes, 1.0, gt=True)
                resistances = _subset_gt_lt_one(notes, 1.0, gt=False)
                result[combo] = float(len(resistances)) / len(weaknesses)

    result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
    from json import dumps

    print(dumps(result, indent=4))
    return result


class CombinedPKType:
    def __init__(self, type_1: PKType, type_2: PKType = None):
        # Be peremissive with type_2 being None for single types.
        # Also permit type_2 as the same type as type_1.
        types = [type_1]
        no_second_type = type_2 is None or type_1 == type_2
        if not no_second_type:
            types.append(type_2)
        types.sort(key=lambda x: x.name)  # Sort to ensure consistent ordering
        self.types = types
        self.name = " + ".join([t.name for t in types])
        self.res = self.resistances()
        self.weak = self.weaknesses()

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(tuple(self.types))

    def __eq__(self, other):
        if not isinstance(other, CombinedPKType):
            return False
        return self.types == other.types

    def __repr__(self):
        return f"CombinedPKType({', '.join(t.name for t in self.types)})"

    def as_table_row_values(self):
        return [
            self.ratio(),
            self.name,
            len(self.resistances()),
            len(self.weaknesses()),
            self.resistances(),
            self.weaknesses(),
        ]

    def print_as_table_row_verbose(self):
        resistances = ", ".join(
            [f"{k.name} ({v})" for k, v in self.resistances().items()]
        )
        weaknesses = ", ".join(
            [f"{k.name} ({v})" for k, v in self.weaknesses().items()]
        )
        return f"{self.ratio():<5.2f} | {self.name:<20} | {len(self.resistances()):<4} | {len(self.weaknesses()):<4} | {resistances:<59} | {weaknesses:<30}"

    def print_as_table_row_quiet(self):
        resistances = ", ".join([f"{k.name}" for k in self.resistances().keys()])
        weaknesses = ", ".join([f"{k.name}" for k in self.weaknesses().keys()])
        return f"{self.ratio():<5.2f} | {self.name:<20} | {len(self.resistances()):<4} | {len(self.weaknesses()):<4} | {resistances:<59} | {weaknesses:<30}"

    def print_as_table_row_codes(self):
        resistances = ", ".join([f"{k.code()}" for k in self.resistances().keys()])
        weaknesses = ", ".join([f"{k.code()}" for k in self.weaknesses().keys()])
        return f"{self.ratio():<5.2f} | {self.name:<20} | {len(self.resistances()):<4} | {len(self.weaknesses()):<4} | {resistances:<59} | {weaknesses:<30}"

    @staticmethod
    def header():
        """
        Returns the header for the combined type table.
        """
        return f"{'Ratio':<5} | {'Type':<20} | {'Res':<4} | {'Weak':<4} | {'Resistances Details':<59} | {'Weaknesses Details':<30}"

    @staticmethod
    def all_combos(sort: str = None):
        all = set()
        for type_1 in PKType:
            for type_2 in PKType:
                combo = CombinedPKType(type_1, type_2)
                all.add(combo)
        all = list(all)
        if sort == "res":
            all.sort(key=lambda x: len(x.res), reverse=True)
        elif sort == "weak":
            all.sort(key=lambda x: len(x.weak))
        else:  # sort in [None, 'ratio', 'rank']:
            all.sort(key=lambda x: x.ratio(), reverse=True)
        return all

    @staticmethod
    def print_all_types_and_combos(filter: PKType = None, sort: str = None):
        """
        Prints all types and their combinations in a table format.
        Args:
            filter: all results will include this type
            sort: 'res' for most resistances, 'weak' for least weaknesses; defaults to best ration of res/weak.
        """
        print(f"{'#':<4} | ", end="")
        print(CombinedPKType.header())
        print("-" * 123)
        all = CombinedPKType.all_combos(sort)
        combo: CombinedPKType
        for i, combo in enumerate(all, 1):
            if filter and filter not in combo.types:
                continue
            print(f"{i:<4} | ", end="")
            # print(combo.print_as_table_row_verbose())
            # print(combo.print_as_table_row_quiet())
            print(combo.print_as_table_row_codes())

    def resistances(self):
        """
        Returns a dictionary of resistances for the combined type.
        """
        if len(self.types) == 1:
            return self.types[0].resistances()
        else:
            notes = combine_types_notables(self.types[0], self.types[1])
            return _subset_gt_lt_one(notes, 1.0, gt=False)

    def weaknesses(self):
        """
        Returns a dictionary of weaknesses for the combined type.
        """
        if len(self.types) == 1:
            return self.types[0].weaknesses()
        else:
            notes = combine_types_notables(self.types[0], self.types[1])
            return _subset_gt_lt_one(notes, 1.0, gt=True)

    def ratio(self):
        return float(len(self.resistances())) / len(self.weaknesses())


def rank_all_types_and_combined_types():
    """
    Ranks all types and their combinations based on the ratio of resistances to weaknesses.
    """
    result = {}
    for type_ in PKType:
        result[type_.name] = CombinedPKType(type_).ratio()

    for type_1 in PKType:
        for type_2 in PKType:
            if type_1 == type_2:
                continue
            combo = CombinedPKType(type_1, type_2)
            result[combo.name] = combo.ratio()

    result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
    from json import dumps

    print(dumps(result, indent=4))
    return result


if __name__ == "__main__":
    # first = rank_types_and_combos_on_the_fly()
    # second = rank_all_types_and_combined_types()
    # if first != second:
    #     print("The two ranking methods produced different results!")
    # else:
    #     print("Both ranking methods produced the same results.")
    # Big print.
    CombinedPKType.print_all_types_and_combos(
        filter=PKType.NORMAL,
        sort="weak",  # None=Rank, 'res'=#Resistances desc, 'weak'=#Weaknesses asc.
    )
