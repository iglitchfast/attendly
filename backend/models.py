from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # "odd" or "even" — picked once on the landing page, drives which
    # static semester calendar (see semesters.py) the engine uses.
    selected_semester = Column(String, nullable=True)

    subjects = relationship("Subject", back_populates="owner", cascade="all, delete-orphan")
    timetable_entries = relationship("TimetableEntry", back_populates="owner", cascade="all, delete-orphan")
    working_day_overrides = relationship("WorkingDayOverride", back_populates="owner", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    required_percent = Column(Float, nullable=False, default=75.0)

    baseline_conducted = Column(Integer, nullable=False, default=0)
    baseline_attended = Column(Integer, nullable=False, default=0)
    baseline_date = Column(Date, nullable=True)

    owner = relationship("User", back_populates="subjects")
    timetable_entries = relationship("TimetableEntry", back_populates="subject", cascade="all, delete-orphan")


class TimetableEntry(Base):
    __tablename__ = "timetable_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)

    day_of_week = Column(Integer, nullable=False)  # Monday=0 ... Saturday=5 (Sunday never scheduled)
    period_number = Column(Integer, nullable=False)

    owner = relationship("User", back_populates="timetable_entries")
    subject = relationship("Subject", back_populates="timetable_entries")


class WorkingDayOverride(Base):
    """
    An otherwise-off date (typically a Saturday) turned into a working day.
    follows_day_of_week tells the calendar engine which weekday's timetable
    to apply on that date (e.g. this Saturday runs Monday's schedule).
    """
    __tablename__ = "working_day_overrides"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    date = Column(Date, nullable=False)
    follows_day_of_week = Column(Integer, nullable=False)  # which weekday's timetable to use
    reason = Column(String, nullable=True)

    owner = relationship("User", back_populates="working_day_overrides")