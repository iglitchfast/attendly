from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, ConfigDict


# --- Auth ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    selected_semester: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


# --- Semester selection ---

class SemesterSelect(BaseModel):
    semester: Literal["odd", "even"]


class SemesterInfo(BaseModel):
    key: str
    label: str
    start: Optional[date] = None
    end: Optional[date] = None
    holiday_count: int


# --- Subjects ---

class SubjectCreate(BaseModel):
    name: str
    required_percent: float = 75.0
    baseline_conducted: int = 0
    baseline_attended: int = 0
    baseline_date: Optional[date] = None


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    required_percent: Optional[float] = None
    baseline_conducted: Optional[int] = None
    baseline_attended: Optional[int] = None
    baseline_date: Optional[date] = None


class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    required_percent: float
    baseline_conducted: int
    baseline_attended: int
    baseline_date: Optional[date] = None


# --- Timetable ---

class TimetableEntryCreate(BaseModel):
    subject_id: int
    day_of_week: int  # 0=Mon ... 5=Sat (6/Sunday not accepted)
    period_number: int


class TimetableEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    day_of_week: int
    period_number: int
    
# --- Timetable presets ---

class PresetInfo(BaseModel):
    id: str
    label: str
    warning: str


class ApplyPresetRequest(BaseModel):
    preset_id: str


class ApplyPresetResponse(BaseModel):
    subjects_created: int
    timetable_entries_created: int


# --- Working day overrides (ad-hoc Saturdays etc.) ---

class WorkingDayOverrideCreate(BaseModel):
    date: date
    follows_day_of_week: int  # which weekday's timetable this date should use
    reason: Optional[str] = None


class WorkingDayOverrideOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    follows_day_of_week: int
    reason: Optional[str] = None


# --- Predictions ---

class SubjectPrediction(BaseModel):
    subject_id: int
    subject_name: str
    conducted: int
    attended: int
    remaining: int
    current_percent: float
    required_percent: float
    safe_skips: int
    can_skip: Optional[Literal["YES", "NO", "RISKY"]] = None
    period_number: Optional[int] = None


class TodayPrediction(BaseModel):
    date: date
    classes: list[SubjectPrediction]


class SafeDayOff(BaseModel):
    date: date
    safe_to_skip_entirely: bool
    subject_count: int


class SafeDaysOffResponse(BaseModel):
    days: list[SafeDayOff]