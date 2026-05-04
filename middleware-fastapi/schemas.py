from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


ALUNO_CURSOS = frozenset({"GES", "GEC"})
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
SUBJECT_CODE_PATTERN = re.compile(r"^[A-Z]{2,10}\d{0,6}$")


class ApiError(BaseModel):
    error: str


class AlunoCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=254)
    curso: str = Field(min_length=3, max_length=3)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        email = v.strip()
        if not EMAIL_PATTERN.match(email):
            raise ValueError("E-mail inválido. Use um endereço válido (ex.: nome@dominio.com).")
        return email

    @field_validator("curso")
    @classmethod
    def validate_curso(cls, v: str) -> str:
        curso = v.strip().upper()
        if curso not in ALUNO_CURSOS:
            raise ValueError(f"Curso inválido. Use um de: {', '.join(sorted(ALUNO_CURSOS))}.")
        return curso

    @field_validator("nome")
    @classmethod
    def normalize_nome(cls, v: str) -> str:
        nome = v.strip()
        if not nome:
            raise ValueError("Nome inválido.")
        return nome


class AlunoPatch(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    curso: str | None = Field(default=None, min_length=3, max_length=3)

    @field_validator("email")
    @classmethod
    def validate_email_optional(cls, v: str | None) -> str | None:
        if v is None:
            return None
        email = v.strip()
        if not EMAIL_PATTERN.match(email):
            raise ValueError("E-mail inválido. Use um endereço válido (ex.: nome@dominio.com).")
        return email

    @field_validator("curso")
    @classmethod
    def validate_curso_optional(cls, v: str | None) -> str | None:
        if v is None:
            return None
        curso = v.strip().upper()
        if curso not in ALUNO_CURSOS:
            raise ValueError(f"Curso inválido. Use um de: {', '.join(sorted(ALUNO_CURSOS))}.")
        return curso

    @field_validator("nome")
    @classmethod
    def normalize_nome_optional(cls, v: str | None) -> str | None:
        if v is None:
            return None
        nome = v.strip()
        if not nome:
            raise ValueError("Nome inválido.")
        return nome


class AlunoOut(BaseModel):
    id: str
    nome: str
    email: str
    curso: str
    matricula: int
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


class DeleteAlunoResponse(BaseModel):
    status: Literal["deleted"]
    id: str


class ResetAlunosResponse(BaseModel):
    status: Literal["reset"]
    removidos: int
