from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, Subject
from schemas import TodayPrediction, SubjectPrediction, SafeDaysOffResponse
from auth import get_current_user
from calendar_engine import get_calendar_status_for_subject, get_todays_classes, get_safe_days_off
from attendance_engine import calculate_percentage, calculate_safe_skips_semester

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/subject/{subject_id}", response_model=SubjectPrediction)
def subject_prediction(
    subject_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    subject = db.query(Subject).filter(
        Subject.id == subject_id, Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    status = get_calendar_status_for_subject(db, subject)
    current_pct = calculate_percentage(status["attended"], status["conducted"])
    safe_skips = calculate_safe_skips_semester(
        status["attended"], status["conducted"], status["remaining"], subject.required_percent
    )

    return SubjectPrediction(
        subject_id=subject.id,
        subject_name=subject.name,
        conducted=status["conducted"],
        attended=status["attended"],
        remaining=status["remaining"],
        current_percent=current_pct,
        required_percent=subject.required_percent,
        safe_skips=safe_skips,
    )


@router.get("/today", response_model=TodayPrediction)
def today_prediction(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = date.today()
    classes_today = get_todays_classes(db, current_user, today)

    results = []
    for entry in classes_today:
        subject = entry["subject"]
        status = get_calendar_status_for_subject(db, subject)
        current_pct = calculate_percentage(status["attended"], status["conducted"])
        safe_skips = calculate_safe_skips_semester(
            status["attended"], status["conducted"], status["remaining"], subject.required_percent
        )
        
        can_skip = "YES" if safe_skips >= 1 else "NO"
        if 0 < (current_pct - subject.required_percent) < 3:
            can_skip = "RISKY"

        results.append(
            SubjectPrediction(
                subject_id=subject.id,
                subject_name=subject.name,
                conducted=status["conducted"],
                attended=status["attended"],
                remaining=status["remaining"],
                current_percent=current_pct,
                required_percent=subject.required_percent,
                safe_skips=safe_skips,
                can_skip=can_skip,
                period_number=entry["period_number"],
            )
        )

    return TodayPrediction(date=today, classes=results)

@router.get("/safe-days-off", response_model=SafeDaysOffResponse)
def safe_days_off(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    days = get_safe_days_off(db, current_user)
    return SafeDaysOffResponse(days=days)