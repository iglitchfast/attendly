"""
Static timetable presets — opt-in shortcuts for specific classes/sections
to pre-fill their subjects + timetable instead of manual entry. Adding a
new class's preset means adding a new entry here, no migration needed.

day_of_week: Monday=0 ... Saturday=5
"""

AI_S3_PRESET = {
    "id": "ai_s3",
    "label": "AI S3",
    "warning": "Only select this if you're actually in AI S3 — subjects and periods will be pre-filled and may not match your actual attendance.",
    "subjects": [
        {"name": "Deep Learning", "required_percent": 75.0},
        {"name": "Computer Networks", "required_percent": 75.0},
        {"name": "Constitution of India", "required_percent": 75.0},
        {"name": "Networks Lab", "required_percent": 75.0},
        {"name": "Data Mining", "required_percent": 75.0},
        {"name": "Design Analysis", "required_percent": 75.0},
        {"name": "Computer Vision", "required_percent": 75.0},
        {"name": "Deep Learning Lab", "required_percent": 75.0},
    ],
    # (day_of_week, period_number, subject_name)
    "timetable": [
        (0, 1, "Deep Learning"), (0, 2, "Computer Networks"), (0, 3, "Constitution of India"),
        (0, 4, "Constitution of India"), (0, 5, "Networks Lab"), (0, 6, "Networks Lab"),

        (1, 1, "Data Mining"), (1, 2, "Design Analysis"), (1, 3, "Computer Vision"),
        (1, 4, "Computer Networks"), (1, 5, "Deep Learning"), (1, 6, "Computer Vision"),

        (2, 1, "Computer Vision"), (2, 2, "Design Analysis"), (2, 3, "Deep Learning"),
        (2, 4, "Computer Vision"), (2, 5, "Computer Networks"), (2, 6, "Design Analysis"),

        (3, 1, "Computer Networks"), (3, 2, "Data Mining"), (3, 3, "Deep Learning Lab"),
        (3, 4, "Deep Learning Lab"), (3, 5, "Computer Vision"), (3, 6, "Deep Learning"),

        (4, 1, "Design Analysis"), (4, 2, "Data Mining"), (4, 3, "Design Analysis"),
        (4, 4, "Data Mining"), (4, 5, "Deep Learning"), (4, 6, "Computer Networks"),
    ],
}

TIMETABLE_PRESETS = {
    "ai_s3": AI_S3_PRESET,
}


def get_preset(preset_id: str) -> dict:
    if preset_id not in TIMETABLE_PRESETS:
        raise ValueError(f"Unknown preset: {preset_id}")
    return TIMETABLE_PRESETS[preset_id]