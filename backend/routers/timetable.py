from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, TimetableEntry, Subject
from schemas import (
    TimetableEntryCreate, TimetableEntryOut,
    PresetInfo, ApplyPresetRequest, ApplyPresetResponse,
)
from auth import get_current_user
from timetable_presets import TIMETABLE_PRESETS, get_preset

router = APIRouter(prefix="/timetable", tags=["timetable"])


@router.get("/", response_model=list[TimetableEntryOut])
def get_timetable(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(TimetableEntry).filter(
        TimetableEntry.user_id == current_user.id
    ).order_by(TimetableEntry.day_of_week, TimetableEntry.period_number).all()


@router.post("/", response_model=TimetableEntryOut, status_code=status.HTTP_201_CREATED)
def set_timetable_slot(
    payload: TimetableEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.day_of_week == 6:
        raise HTTPException(status_code=400, detail="Sunday is never a scheduled day")
    if not (0 <= payload.day_of_week <= 6):
        raise HTTPException(status_code=400, detail="day_of_week must be 0 (Mon) through 5 (Sat)")

    subject = db.query(Subject).filter(
        Subject.id == payload.subject_id, Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # One subject per day/period slot per user — overwrite if it exists
    entry = db.query(TimetableEntry).filter(
        TimetableEntry.user_id == current_user.id,
        TimetableEntry.day_of_week == payload.day_of_week,
        TimetableEntry.period_number == payload.period_number,
    ).first()

    if entry:
        entry.subject_id = payload.subject_id
    else:
        entry = TimetableEntry(
            user_id=current_user.id,
            day_of_week=payload.day_of_week,
            period_number=payload.period_number,
            subject_id=payload.subject_id,
        )
        db.add(entry)

    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timetable_slot(entry_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    entry = db.query(TimetableEntry).filter(
        TimetableEntry.id == entry_id, TimetableEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Timetable entry not found")
    db.delete(entry)
    db.commit()
    
@router.get("/presets", response_model=list[PresetInfo])
def list_presets():
    return [
        PresetInfo(id=p["id"], label=p["label"], warning=p["warning"])
        for p in TIMETABLE_PRESETS.values()
    ]


@router.post("/apply-preset", response_model=ApplyPresetResponse)
def apply_preset(
    payload: ApplyPresetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        preset = get_preset(payload.preset_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Preset not found")

    # Only fill in subjects/timetable if the user hasn't already set any up —
    # prevents silently duplicating or clobbering manual entries.
    existing_subjects = db.query(Subject).filter(Subject.user_id == current_user.id).count()
    existing_entries = db.query(TimetableEntry).filter(TimetableEntry.user_id == current_user.id).count()
    if existing_subjects > 0 or existing_entries > 0:
        raise HTTPException(
            status_code=400,
            detail="You already have subjects or timetable entries. Presets can only be applied to a fresh account.",
        )

    name_to_subject = {}
    for subj_data in preset["subjects"]:
        subject = Subject(
            user_id=current_user.id,
            name=subj_data["name"],
            required_percent=subj_data["required_percent"],
            baseline_conducted=0,
            baseline_attended=0,
            baseline_date=None,
        )
        db.add(subject)
        db.flush()  # get subject.id before commit
        name_to_subject[subj_data["name"]] = subject

    entries_created = 0
    for day_of_week, period_number, subject_name in preset["timetable"]:
        subject = name_to_subject.get(subject_name)
        if not subject:
            continue
        entry = TimetableEntry(
            user_id=current_user.id,
            subject_id=subject.id,
            day_of_week=day_of_week,
            period_number=period_number,
        )
        db.add(entry)
        entries_created += 1

    db.commit()

    return ApplyPresetResponse(
        subjects_created=len(name_to_subject),
        timetable_entries_created=entries_created,
    )