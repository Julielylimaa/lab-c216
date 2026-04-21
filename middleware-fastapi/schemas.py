from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


VALID_COURSES = frozenset({"GES", "GEC", "GET", "GEP"})
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
SUBJECT_CODE_PATTERN = re.compile(r"^[A-Z]{2,10}\d{0,6}$")


class ApiError(BaseModel):
    error: str


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=254)
    course: str = Field(min_length=2, max_length=10)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        email = v.strip()
        if not EMAIL_PATTERN.match(email):
            raise ValueError("Invalid email. Use a valid address (e.g. name@domain.com).")
        return email

    @field_validator("course")
    @classmethod
    def validate_course(cls, v: str) -> str:
        course = v.strip().upper()
        if course not in VALID_COURSES:
            raise ValueError(f"Invalid course. Must be one of: {', '.join(sorted(VALID_COURSES))}.")
        return course

    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        name = v.strip()
        if not name:
            raise ValueError("Invalid name.")
        return name


class StudentPut(StudentCreate):
    pass


class StudentPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    course: str | None = Field(default=None, min_length=2, max_length=10)

    @field_validator("email")
    @classmethod
    def validate_email_optional(cls, v: str | None) -> str | None:
        if v is None:
            return None
        email = v.strip()
        if not EMAIL_PATTERN.match(email):
            raise ValueError("Invalid email. Use a valid address (e.g. name@domain.com).")
        return email

    @field_validator("course")
    @classmethod
    def validate_course_optional(cls, v: str | None) -> str | None:
        if v is None:
            return None
        course = v.strip().upper()
        if course not in VALID_COURSES:
            raise ValueError(f"Invalid course. Must be one of: {', '.join(sorted(VALID_COURSES))}.")
        return course

    @field_validator("name")
    @classmethod
    def normalize_name_optional(cls, v: str | None) -> str | None:
        if v is None:
            return None
        name = v.strip()
        if not name:
            raise ValueError("Invalid name.")
        return name


class StudentOut(BaseModel):
    id: str
    name: str
    email: str
    course: str
    subject_ids: list[str]


class SubjectCreate(BaseModel):
    code: str = Field(min_length=2, max_length=16)
    name: str = Field(min_length=1, max_length=120)

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        code = v.strip().upper()
        if not SUBJECT_CODE_PATTERN.match(code):
            raise ValueError("Invalid subject code. Example: MAT101.")
        return code

    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        name = v.strip()
        if not name:
            raise ValueError("Invalid subject name.")
        return name


class SubjectOut(BaseModel):
    id: str
    code: str
    name: str
    enrolled_count: int
    enrolled_student_ids: list[str] = Field(default_factory=list)


class DeleteStudentResponse(BaseModel):
    status: Literal["deleted"]
    id: str
