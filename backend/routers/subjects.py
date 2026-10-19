from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Subject
from schemas import SubjectCreate, SubjectUpdate, SubjectOut
from auth import get_current_user

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("/", response_model=list[SubjectOut])
def list_subjects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Subject).filter(Subject.user_id == current_user.id).all()


@router.post("/", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subject = Subject(
        user_id=current_user.id,
        name=payload.name,
        required_percent=payload.required_percent,
        baseline_conducted=payload.baseline_conducted,
        baseline_attended=payload.baseline_attended,
        baseline_date=payload.baseline_date,
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.get("/{subject_id}", response_model=SubjectOut)
def get_subject(subject_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subject = db.query(Subject).filter(
        Subject.id == subject_id, Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.patch("/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject = db.query(Subject).filter(
        Subject.id == subject_id, Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(subject, field, value)

    db.commit()
    db.refresh(subject)
    return subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subject = db.query(Subject).filter(
        Subject.id == subject_id, Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subject)
    db.commit()