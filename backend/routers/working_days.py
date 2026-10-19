from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, WorkingDayOverride
from schemas import WorkingDayOverrideCreate, WorkingDayOverrideOut
from auth import get_current_user

router = APIRouter(prefix="/working-days", tags=["working-days"])


@router.get("/", response_model=list[WorkingDayOverrideOut])
def list_working_day_overrides(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(WorkingDayOverride).filter(
        WorkingDayOverride.user_id == current_user.id
    ).order_by(WorkingDayOverride.date).all()


@router.post("/", response_model=WorkingDayOverrideOut, status_code=status.HTTP_201_CREATED)
def create_working_day_override(
    payload: WorkingDayOverrideCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.date.weekday() == 6:
        raise HTTPException(status_code=400, detail="Sunday can never be a working day")

    existing = db.query(WorkingDayOverride).filter(
        WorkingDayOverride.user_id == current_user.id, WorkingDayOverride.date == payload.date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Working day override already exists for this date")

    override = WorkingDayOverride(
        user_id=current_user.id,
        date=payload.date,
        follows_day_of_week=payload.follows_day_of_week,
        reason=payload.reason,
    )
    db.add(override)
    db.commit()
    db.refresh(override)
    return override


@router.delete("/{override_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_working_day_override(
    override_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    override = db.query(WorkingDayOverride).filter(
        WorkingDayOverride.id == override_id, WorkingDayOverride.user_id == current_user.id
    ).first()
    if not override:
        raise HTTPException(status_code=404, detail="Working day override not found")
    db.delete(override)
    db.commit()