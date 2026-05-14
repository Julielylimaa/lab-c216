#!/usr/bin/env python3
"""Insere alunos, disciplinas e matrículas extras no PostgreSQL.

Usa `storage.store` (mesma regra de IDs/matrículas da API).
Idempotente: ignora e-mails e códigos de disciplina já existentes.

Uso (com o banco no ar):
  export DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5432/middleware
  python seed_data.py
"""

from __future__ import annotations

from database import SessionLocal, init_db
from models import Enrollment, Student, Subject
from schemas import AlunoCreate, SubjectCreate
from sqlalchemy import select
from storage import store

ALUNOS_SEED: list[tuple[str, str, str]] = [
    ("Beatriz Almeida", "beatriz.almeida.seed@example.com", "GES"),
    ("Carlos Mendes", "carlos.mendes.seed@example.com", "GES"),
    ("Daniela Rocha", "daniela.rocha.seed@example.com", "GES"),
    ("Eduardo Pires", "eduardo.pires.seed@example.com", "GES"),
    ("Fernanda Costa", "fernanda.costa.seed@example.com", "GEC"),
    ("Gabriel Nunes", "gabriel.nunes.seed@example.com", "GEC"),
    ("Helena Dias", "helena.dias.seed@example.com", "GEC"),
    ("Igor Martins", "igor.martins.seed@example.com", "GEC"),
]

DISCIPLINAS_SEED: list[tuple[str, str]] = [
    ("PROG1", "Programação I"),
    ("BD201", "Banco de Dados"),
    ("REDES", "Redes de Computadores"),
    ("SO101", "Sistemas Operacionais"),
]


def _email_existe(email: str) -> bool:
    with SessionLocal() as s:
        return s.scalar(select(Student.id).where(Student.email == email)) is not None


def _disciplina_por_codigo(code: str) -> Subject | None:
    with SessionLocal() as s:
        return s.scalar(select(Subject).where(Subject.code == code))


def _ja_matriculado(subject_id: str, aluno_id: str) -> bool:
    with SessionLocal() as s:
        return (
            s.scalar(
                select(Enrollment.aluno_id).where(
                    Enrollment.subject_id == subject_id,
                    Enrollment.aluno_id == aluno_id,
                )
            )
            is not None
        )


def main() -> None:
    init_db()
    criados_alunos = 0
    for nome, email, curso in ALUNOS_SEED:
        if _email_existe(email):
            continue
        store.create_student(AlunoCreate(nome=nome, email=email, curso=curso))
        criados_alunos += 1

    criados_disc = 0
    subject_ids: list[str] = []
    for code, name in DISCIPLINAS_SEED:
        row = _disciplina_por_codigo(code)
        if row is not None:
            subject_ids.append(row.id)
            continue
        d = store.create_subject(SubjectCreate(code=code, name=name))
        subject_ids.append(d["id"])
        criados_disc += 1

    # Algumas matrículas em disciplina (primeiros alunos GES/GEC da listagem atual)
    alunos = store.list_students()
    if not subject_ids:
        subject_ids = [s["id"] for s in store.list_subjects()]

    matriculas = 0
    if alunos and subject_ids:
        pares = [
            (alunos[0]["id"], subject_ids[0]),
            (alunos[1 % len(alunos)]["id"], subject_ids[0]),
            (alunos[0]["id"], subject_ids[1 % len(subject_ids)]),
        ]
        if len(alunos) > 2 and len(subject_ids) > 1:
            pares.append((alunos[2]["id"], subject_ids[1]))
        for aluno_id, sub_id in pares:
            if _ja_matriculado(sub_id, aluno_id):
                continue
            store.enroll(sub_id, aluno_id)
            matriculas += 1

    total_alunos = len(store.list_students())
    total_disc = len(store.list_subjects())
    print(
        f"Seed: +{criados_alunos} alunos, +{criados_disc} disciplinas, "
        f"+{matriculas} matrículas (enroll). "
        f"Totais agora: {total_alunos} alunos, {total_disc} disciplinas."
    )


if __name__ == "__main__":
    main()
