"""
Class that take into account mono-typing and duo-typing.
"""
from pktype import PKType, get_all_notable_defender_multipliers


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


if __name__ == "__main__":
    CombinedPKType.print_all_types_and_combos(
        filter=PKType.NORMAL,
        sort="weak",  # None=Rank, 'res'=#Resistances desc, 'weak'=#Weaknesses asc.
    )
