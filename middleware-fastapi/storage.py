from __future__ import annotations

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from database import SessionLocal, seed_sequence_rows
from models import Enrollment, IdSeq, MatriculaSeq, Student, Subject
from schemas import AlunoCreate, AlunoPatch, SubjectCreate


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


def _student_to_dict(row: Student) -> dict:
    return {
        "id": row.id,
        "nome": row.nome,
        "email": row.email,
        "curso": row.curso,
        "matricula": row.matricula,
    }


def _subject_to_dict(row: Subject) -> dict:
    return {"id": row.id, "code": row.code, "name": row.name}


class PostgresStore:
    def _session(self) -> Session:
        return SessionLocal()

    def reset(self) -> None:
        """Limpa todas as tabelas e reinicia contadores (uso em testes)."""
        with self._session() as session:
            session.execute(delete(Enrollment))
            session.execute(delete(Student))
            session.execute(delete(Subject))
            session.execute(delete(MatriculaSeq))
            session.execute(delete(IdSeq))
            session.commit()
        with self._session() as session:
            seed_sequence_rows(session)
            session.commit()

    def _next_matricula_and_id(self, session: Session, curso: str) -> tuple[int, str]:
        row = session.get(MatriculaSeq, curso, with_for_update=True)
        if row is None:
            row = MatriculaSeq(curso=curso, last_value=0)
            session.add(row)
            session.flush()
        row.last_value += 1
        matricula = row.last_value
        return matricula, f"{curso}{matricula}"

    def _next_subject_id(self, session: Session) -> str:
        row = session.get(IdSeq, "subject", with_for_update=True)
        if row is None:
            row = IdSeq(name="subject", last_value=0)
            session.add(row)
            session.flush()
        row.last_value += 1
        return f"sub_{row.last_value}"

    def create_student(self, data: AlunoCreate) -> dict:
        with self._session() as session:
            matricula, aluno_id = self._next_matricula_and_id(session, data.curso)
            row = Student(
                id=aluno_id,
                nome=data.nome,
                email=data.email,
                curso=data.curso,
                matricula=matricula,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return _student_to_dict(row)

    def list_students(self) -> list[dict]:
        with self._session() as session:
            rows = session.scalars(select(Student).order_by(Student.id)).all()
            return [_student_to_dict(r) for r in rows]

    def get_student(self, aluno_id: str) -> dict:
        with self._session() as session:
            row = session.get(Student, aluno_id)
            if row is None:
                raise NotFoundError("Aluno não encontrado.")
            return _student_to_dict(row)

    def patch_student(self, aluno_id: str, data: AlunoPatch) -> dict:
        with self._session() as session:
            row = session.get(Student, aluno_id, with_for_update=True)
            if row is None:
                raise NotFoundError("Aluno não encontrado.")
            if data.nome is not None:
                row.nome = data.nome
            if data.email is not None:
                row.email = data.email
            if data.curso is not None and data.curso != row.curso:
                old_id = row.id
                matricula, new_id = self._next_matricula_and_id(session, data.curso)
                session.execute(
                    update(Enrollment).where(Enrollment.aluno_id == old_id).values(aluno_id=new_id)
                )
                row.curso = data.curso
                row.matricula = matricula
                row.id = new_id
            session.commit()
            session.refresh(row)
            return _student_to_dict(row)

    def delete_student(self, aluno_id: str) -> None:
        with self._session() as session:
            row = session.get(Student, aluno_id)
            if row is None:
                raise NotFoundError("Aluno não encontrado.")
            session.delete(row)
            session.commit()

    def clear_all_students(self) -> int:
        with self._session() as session:
            n = session.scalar(select(func.count()).select_from(Student)) or 0
            session.execute(delete(Student))
            session.commit()
            return int(n)

    def create_subject(self, data: SubjectCreate) -> dict:
        with self._session() as session:
            subject_id = self._next_subject_id(session)
            row = Subject(id=subject_id, code=data.code, name=data.name)
            session.add(row)
            session.commit()
            session.refresh(row)
            return _subject_to_dict(row)

    def list_subjects(self) -> list[dict]:
        with self._session() as session:
            rows = session.scalars(select(Subject).order_by(Subject.id)).all()
            return [_subject_to_dict(r) for r in rows]

    def get_subject(self, subject_id: str) -> dict:
        with self._session() as session:
            row = session.get(Subject, subject_id)
            if row is None:
                raise NotFoundError("Subject not found.")
            return _subject_to_dict(row)

    def enroll(self, subject_id: str, aluno_id: str) -> None:
        with self._session() as session:
            if session.get(Subject, subject_id) is None:
                raise NotFoundError("Subject not found.")
            if session.get(Student, aluno_id) is None:
                raise NotFoundError("Aluno não encontrado.")
            session.merge(Enrollment(subject_id=subject_id, aluno_id=aluno_id))
            session.commit()

    def unenroll(self, subject_id: str, aluno_id: str) -> None:
        with self._session() as session:
            if session.get(Subject, subject_id) is None:
                raise NotFoundError("Subject not found.")
            if session.get(Student, aluno_id) is None:
                raise NotFoundError("Aluno não encontrado.")
            row = session.get(Enrollment, (subject_id, aluno_id))
            if row:
                session.delete(row)
            session.commit()

    def student_subject_ids(self, aluno_id: str) -> list[str]:
        with self._session() as session:
            if session.get(Student, aluno_id) is None:
                raise NotFoundError("Aluno não encontrado.")
            ids = session.scalars(
                select(Enrollment.subject_id).where(Enrollment.aluno_id == aluno_id)
            ).all()
            return sorted(ids)

    def subject_student_ids(self, subject_id: str) -> list[str]:
        with self._session() as session:
            if session.get(Subject, subject_id) is None:
                raise NotFoundError("Subject not found.")
            ids = session.scalars(
                select(Enrollment.aluno_id).where(Enrollment.subject_id == subject_id)
            ).all()
            return sorted(ids)


store = PostgresStore()
