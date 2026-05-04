from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse

from schemas import (
    AlunoCreate,
    AlunoOut,
    AlunoPatch,
    ApiError,
    DeleteAlunoResponse,
    ResetAlunosResponse,
    SubjectCreate,
    SubjectOut,
)
from storage import NotFoundError, store

app = FastAPI(title="Middleware FastAPI - Alunos & Disciplinas")

alunos_router = APIRouter(prefix="/api/v1/alunos", tags=["alunos"])


@app.exception_handler(NotFoundError)
def handle_not_found(_, exc: NotFoundError):
    return JSONResponse(status_code=404, content=ApiError(error=str(exc)).model_dump())


def aluno_to_out(student: dict) -> AlunoOut:
    subject_ids = store.student_subject_ids(student["id"])
    return AlunoOut(
        id=student["id"],
        nome=student["nome"],
        email=student["email"],
        curso=student["curso"],
        matricula=student["matricula"],
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


@alunos_router.post("/", response_model=AlunoOut, status_code=201)
def post_aluno(payload: AlunoCreate):
    student = store.create_student(payload)
    return aluno_to_out(student)


@alunos_router.get("/", response_model=list[AlunoOut])
def get_alunos():
    students = store.list_students()
    return [aluno_to_out(s) for s in students]


@alunos_router.get("/{aluno_id}", response_model=AlunoOut)
def get_aluno(aluno_id: str):
    student = store.get_student(aluno_id)
    return aluno_to_out(student)


@alunos_router.patch("/{aluno_id}", response_model=AlunoOut)
def patch_aluno(aluno_id: str, payload: AlunoPatch):
    student = store.patch_student(aluno_id, payload)
    return aluno_to_out(student)


@alunos_router.delete("/", response_model=ResetAlunosResponse)
def delete_all_alunos():
    removidos = store.clear_all_students()
    return ResetAlunosResponse(status="reset", removidos=removidos)


@alunos_router.delete("/{aluno_id}", response_model=DeleteAlunoResponse)
def delete_aluno(aluno_id: str):
    store.delete_student(aluno_id)
    return DeleteAlunoResponse(status="deleted", id=aluno_id)


app.include_router(alunos_router)


@app.get("/subjects", response_model=list[SubjectOut])
def get_subjects():
    subjects = store.list_subjects()
    return [subject_to_out(s) for s in subjects]


@app.post("/subjects", response_model=SubjectOut, status_code=201)
def post_subject(payload: SubjectCreate):
    subject = store.create_subject(payload)
    return subject_to_out(subject)


@app.put("/subjects/{subject_id}/enroll/{aluno_id}", response_model=SubjectOut)
def put_enroll(subject_id: str, aluno_id: str):
    store.enroll(subject_id, aluno_id)
    subject = store.get_subject(subject_id)
    return subject_to_out(subject)


@app.patch("/subjects/{subject_id}/unenroll/{aluno_id}", response_model=SubjectOut)
def patch_unenroll(subject_id: str, aluno_id: str):
    store.unenroll(subject_id, aluno_id)
    subject = store.get_subject(subject_id)
    return subject_to_out(subject)
