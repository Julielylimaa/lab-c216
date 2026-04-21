from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from schemas import (
    ApiError,
    DeleteStudentResponse,
    SubjectCreate,
    SubjectOut,
    StudentCreate,
    StudentOut,
    StudentPatch,
    StudentPut,
)
from storage import NotFoundError, store

app = FastAPI(title="Middleware FastAPI - Students & Subjects")


@app.exception_handler(NotFoundError)
def handle_not_found(_, exc: NotFoundError):
    return JSONResponse(status_code=404, content=ApiError(error=str(exc)).model_dump())


def student_to_out(student: dict) -> StudentOut:
    subject_ids = store.student_subject_ids(student["id"])
    return StudentOut(
        id=student["id"],
        name=student["name"],
        email=student["email"],
        course=student["course"],
        subject_ids=subject_ids,
    )


def subject_to_out(subject: dict, include_student_ids: bool = True) -> SubjectOut:
    student_ids = store.subject_student_ids(subject["id"]) if include_student_ids else []
    return SubjectOut(
        id=subject["id"],
        code=subject["code"],
        name=subject["name"],
        enrolled_count=len(student_ids),
        enrolled_student_ids=student_ids,
    )


# GET (1/2)
@app.get("/students", response_model=list[StudentOut])
def get_students():
    students = store.list_students()
    return [student_to_out(s) for s in students]


# POST (1/2)
@app.post("/students", response_model=StudentOut, status_code=201)
def post_student(payload: StudentCreate):
    student = store.create_student(payload)
    return student_to_out(student)


# PUT (1/2)
@app.put("/students/{student_id}", response_model=StudentOut)
def put_student(student_id: str, payload: StudentPut):
    student = store.put_student(student_id, payload)
    return student_to_out(student)


# PATCH (1/2)
@app.patch("/students/{student_id}", response_model=StudentOut)
def patch_student(student_id: str, payload: StudentPatch):
    student = store.patch_student(student_id, payload)
    return student_to_out(student)


# DELETE 
@app.delete("/students/{student_id}", response_model=DeleteStudentResponse)
def delete_student(student_id: str):
    store.delete_student(student_id)
    return DeleteStudentResponse(status="deleted", id=student_id)


# GET (2/2)
@app.get("/subjects", response_model=list[SubjectOut])
def get_subjects():
    subjects = store.list_subjects()
    return [subject_to_out(s) for s in subjects]


# POST (2/2)
@app.post("/subjects", response_model=SubjectOut, status_code=201)
def post_subject(payload: SubjectCreate):
    subject = store.create_subject(payload)
    return subject_to_out(subject)


# PUT (2/2) - enroll
@app.put("/subjects/{subject_id}/enroll/{student_id}", response_model=SubjectOut)
def put_enroll(subject_id: str, student_id: str):
    store.enroll(subject_id, student_id)
    subject = store.get_subject(subject_id)
    return subject_to_out(subject)


# PATCH (2/2) - unenroll
@app.patch("/subjects/{subject_id}/unenroll/{student_id}", response_model=SubjectOut)
def patch_unenroll(subject_id: str, student_id: str):
    store.unenroll(subject_id, student_id)
    subject = store.get_subject(subject_id)
    return subject_to_out(subject)

