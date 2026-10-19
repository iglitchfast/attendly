"""
Walks the semester calendar (from semesters.py, not user-entered dates)
using the timetable + static holiday list + working-day overrides to
compute, per subject:
  - conducted-so-far (baseline + calendar-derived classes since baseline)
  - remaining classes left in the semester

Sundays are never working days — no setting needed. Saturdays are working
only via an explicit WorkingDayOverride, which also specifies which
weekday's timetable to follow that day.

Same assumption as before: attended-so-far = baseline_attended + every
calendar-derived class since the baseline date (full attendance assumed
going forward until a "mark missed" feature exists).
"""

from datetime import date, timedelta
from sqlalchemy.orm import Session

from models import User, Subject, TimetableEntry, WorkingDayOverride
from semesters import get_semester


def get_semester_dates(user: User) -> tuple[date, date, set[date]]:
    """Returns (start, end, holiday_set) for the user's selected semester."""
    if not user.selected_semester:
        raise ValueError("User has not selected a semester yet")
    sem = get_semester(user.selected_semester)
    if not sem["start"] or not sem["end"]:
        raise ValueError(f"Semester '{user.selected_semester}' has no configured dates yet")
    return sem["start"], sem["end"], set(sem["holidays"])


def get_working_day_override(db: Session, user: User, on_date: date) -> WorkingDayOverride | None:
    return db.query(WorkingDayOverride).filter(
        WorkingDayOverride.user_id == user.id, WorkingDayOverride.date == on_date
    ).first()


def is_working_day(user: User, on_date: date, holidays: set[date], override: WorkingDayOverride | None) -> bool:
    """
    Working-day rules, in priority order:
      1. Static holiday -> never working, even if someone tried to override it.
      2. Explicit WorkingDayOverride -> working.
      3. Sunday -> never working.
      4. Saturday -> working only if overridden (handled above); otherwise off.
      5. Monday-Friday -> always working.
    """
    if on_date in holidays:
        return False
    if override:
        return True
    weekday = on_date.weekday()  # Monday=0 ... Sunday=6
    if weekday == 6:  # Sunday
        return False
    if weekday == 5:  # Saturday, no override present
        return False
    return True  # Mon-Fri


def get_scheduled_entries_for_day(
    db: Session, user: User, on_date: date, holidays: set[date]
) -> list[TimetableEntry]:
    """Timetable entries that apply on this date, if it's a working day.
    For an overridden Saturday, uses the override's follows_day_of_week
    instead of the actual date's weekday."""
    override = get_working_day_override(db, user, on_date)

    if not is_working_day(user, on_date, holidays, override):
        return []

    effective_weekday = override.follows_day_of_week if override else on_date.weekday()

    return db.query(TimetableEntry).filter(
        TimetableEntry.user_id == user.id,
        TimetableEntry.day_of_week == effective_weekday,
    ).order_by(TimetableEntry.period_number).all()


def count_classes_for_subject_between(
    db: Session, user: User, subject_id: int, start_date: date, end_date: date, holidays: set[date]
) -> int:
    """Inclusive count of how many times subject_id appears on the
    effective timetable across working days from start_date to end_date."""
    if start_date > end_date:
        return 0

    count = 0
    current = start_date
    while current <= end_date:
        entries = get_scheduled_entries_for_day(db, user, current, holidays)
        count += sum(1 for e in entries if e.subject_id == subject_id)
        current += timedelta(days=1)
    return count


def get_calendar_status_for_subject(db: Session, subject: Subject) -> dict:
    """Returns {conducted, attended, remaining} for a single subject,
    combining the stored baseline with calendar-derived classes."""
    user = db.query(User).filter(User.id == subject.user_id).first()
    sem_start, sem_end, holidays = get_semester_dates(user)
    today = date.today()

    baseline_date = subject.baseline_date or sem_start
    conducted_since_baseline = count_classes_for_subject_between(
        db, user, subject.id, baseline_date + timedelta(days=1), today, holidays
    )

    conducted = subject.baseline_conducted + conducted_since_baseline
    attended = subject.baseline_attended + conducted_since_baseline

    remaining = count_classes_for_subject_between(
        db, user, subject.id, today + timedelta(days=1), sem_end, holidays
    )

    return {"conducted": conducted, "attended": attended, "remaining": remaining}


def get_todays_classes(db: Session, user: User, on_date: date) -> list[dict]:
    """List of {subject, period_number} scheduled for on_date."""
    _, _, holidays = get_semester_dates(user)
    entries = get_scheduled_entries_for_day(db, user, on_date, holidays)
    result = []
    for entry in entries:
        subject = db.query(Subject).filter(Subject.id == entry.subject_id).first()
        if subject:
            result.append({"subject": subject, "period_number": entry.period_number})
    return result


def get_safe_days_off(db: Session, user: User) -> list[dict]:
    """
    Walks every remaining working day in the semester and flags which ones
    are fully safe to take off entirely — i.e. skipping every class
    scheduled that day still leaves every affected subject with >=1 safe
    skip remaining, calculated as if that day (and no other) were missed.
    """
    from attendance_engine import calculate_safe_skips_semester

    sem_start, sem_end, holidays = get_semester_dates(user)
    today = date.today()

    subjects = db.query(Subject).filter(Subject.user_id == user.id).all()
    subject_status = {s.id: get_calendar_status_for_subject(db, s) for s in subjects}
    subject_by_id = {s.id: s for s in subjects}

    results = []
    current = today + timedelta(days=1)
    while current <= sem_end:
        entries = get_scheduled_entries_for_day(db, user, current, holidays)
        if entries:
            day_is_safe = True
            for entry in entries:
                subject = subject_by_id.get(entry.subject_id)
                if not subject:
                    continue
                status = subject_status[subject.id]
                # if we skip this one specific class, does the subject still clear the bar?
                hypothetical_remaining = status["remaining"] - 1
                skips_if_this_missed = calculate_safe_skips_semester(
                    status["attended"], status["conducted"], hypothetical_remaining, subject.required_percent
                )
                # subject must still be able to afford at least 0 further skips
                # after this one is used, i.e. it must have had >=1 available before.
                current_safe_skips = calculate_safe_skips_semester(
                    status["attended"], status["conducted"], status["remaining"], subject.required_percent
                )
                if current_safe_skips < 1:
                    day_is_safe = False
                    break

            results.append({
                "date": current,
                "safe_to_skip_entirely": day_is_safe,
                "subject_count": len(entries),
            })
        current += timedelta(days=1)

    return results