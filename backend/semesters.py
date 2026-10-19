"""
Static semester calendars. Not user-editable — these are fixed per
semester based on the college's official academic calendar. Adding a
new semester means adding a new entry here, not a database migration.
"""

from datetime import date

ODD_SEMESTER = {
    "label": "Odd Semester",
    "start": date(2026, 7, 1),
    "end": date(2026, 11, 30),
    "holidays": [
        date(2026, 7, 5), date(2026, 7, 11), date(2026, 7, 12), date(2026, 7, 19),
        date(2026, 7, 26), date(2026, 8, 2), date(2026, 8, 8), date(2026, 8, 9),
        date(2026, 8, 12), date(2026, 8, 15), date(2026, 8, 16), date(2026, 8, 23),
        date(2026, 8, 25), date(2026, 8, 26), date(2026, 8, 27), date(2026, 8, 28),
        date(2026, 8, 30), date(2026, 9, 4), date(2026, 9, 6), date(2026, 9, 12),
        date(2026, 9, 13), date(2026, 9, 20), date(2026, 9, 21), date(2026, 9, 27),
        date(2026, 10, 2), date(2026, 10, 4), date(2026, 10, 10), date(2026, 10, 11),
        date(2026, 10, 18), date(2026, 10, 20), date(2026, 10, 21), date(2026, 10, 25),
        date(2026, 11, 1), date(2026, 11, 8), date(2026, 11, 14), date(2026, 11, 15),
        date(2026, 11, 22), date(2026, 11, 29),
    ],
}

# Placeholder — fill in once Even Semester's dates/holidays are confirmed.
EVEN_SEMESTER = {
    "label": "Even Semester",
    "start": None,
    "end": None,
    "holidays": [],
}

SEMESTERS = {
    "odd": ODD_SEMESTER,
    "even": EVEN_SEMESTER,
}


def get_semester(key: str) -> dict:
    if key not in SEMESTERS:
        raise ValueError(f"Unknown semester key: {key}")
    return SEMESTERS[key]