"""
Core attendance math. Pure functions, no DB/framework dependencies —
unit-testable in isolation. Mirrors frontend/js/attendance-math.js exactly,
so keep both in sync if you change the formulas here.
"""

import math


def calculate_percentage(attended: int, conducted: int) -> float:
    """Attendance % so far. Returns 0 if no classes conducted yet."""
    if conducted <= 0:
        return 0.0
    return round((attended / conducted) * 100, 2)


def calculate_safe_skips(attended: int, conducted: int, required_percent: float) -> int:
    """
    Max number of upcoming classes (of this subject) that can be skipped
    without attended/(conducted + x) dropping below required_percent.

    Solve for x:
        attended / (conducted + x) >= required_percent / 100
        attended * 100 >= required_percent * (conducted + x)
        x <= (attended * 100 / required_percent) - conducted
    """
    if required_percent <= 0:
        return 10**6  # no requirement, effectively unlimited
    if conducted <= 0:
        return 0  # nothing conducted yet, nothing to safely skip

    max_x = (attended * 100 / required_percent) - conducted
    return max(0, math.floor(max_x))


def classes_needed_to_recover(attended: int, conducted: int, required_percent: float) -> int:
    """
    If currently below required_percent, how many consecutive classes must be
    attended (each one incrementing both attended and conducted) to reach it.

    Solve for smallest non-negative integer n:
        (attended + n) / (conducted + n) >= required_percent / 100
    """
    if required_percent <= 0:
        return 0

    current = calculate_percentage(attended, conducted)
    if current >= required_percent:
        return 0

    n = 0
    while True:
        projected = calculate_percentage(attended + n, conducted + n)
        if projected >= required_percent:
            return n
        n += 1
        if n > 100000:  # safety valve, should never realistically hit this
            return n
        
def calculate_safe_skips_semester(attended: int, conducted: int, remaining: int, required_percent: float) -> int:
    """
    Semester-aware safe skips: out of the classes remaining, how many can
    be missed while still hitting required_percent by semester end,
    assuming every other remaining class is attended.
    """
    total_classes = conducted + remaining
    if total_classes <= 0 or required_percent <= 0:
        return remaining

    min_attended_needed = math.ceil((required_percent / 100) * total_classes)
    must_attend_of_remaining = max(0, min_attended_needed - attended)
    return max(0, remaining - must_attend_of_remaining)