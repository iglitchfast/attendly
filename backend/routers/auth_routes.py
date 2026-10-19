from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, UserOut, Token, SemesterSelect, SemesterInfo
from auth import hash_password, verify_password, create_access_token, get_current_user
from semesters import SEMESTERS

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/semesters", response_model=list[SemesterInfo])
def list_semesters():
    result = []
    for key, sem in SEMESTERS.items():
        result.append(SemesterInfo(
            key=key,
            label=sem["label"],
            start=sem["start"],
            end=sem["end"],
            holiday_count=len(sem["holidays"]),
        ))
    return result


@router.patch("/me/semester", response_model=UserOut)
def select_semester(
    payload: SemesterSelect,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sem = SEMESTERS.get(payload.semester)
    if not sem or not sem["start"] or not sem["end"]:
        raise HTTPException(status_code=400, detail="Selected semester is not configured yet")

    current_user.selected_semester = payload.semester
    db.commit()
    db.refresh(current_user)
    return current_user