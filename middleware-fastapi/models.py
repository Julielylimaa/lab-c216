from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (UniqueConstraint("email", name="uq_students_email"),)

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254))
    curso: Mapped[str] = mapped_column(String(8))
    matricula: Mapped[int] = mapped_column(Integer)


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    code: Mapped[str] = mapped_column(String(16))
    name: Mapped[str] = mapped_column(String(120))


class Enrollment(Base):
    __tablename__ = "enrollments"

    subject_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True
    )
    aluno_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )


class MatriculaSeq(Base):
    __tablename__ = "matricula_seq"

    curso: Mapped[str] = mapped_column(String(8), primary_key=True)
    last_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class IdSeq(Base):
    __tablename__ = "id_seq"

    name: Mapped[str] = mapped_column(String(32), primary_key=True)
    last_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
