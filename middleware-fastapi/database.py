from __future__ import annotations

import os

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session, sessionmaker

from models import Base, IdSeq, MatriculaSeq

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/middleware",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def seed_sequence_rows(session: Session) -> None:
    for curso in ("GES", "GEC"):
        row = session.get(MatriculaSeq, curso)
        if row is None:
            session.add(MatriculaSeq(curso=curso, last_value=0))
    row_sub = session.get(IdSeq, "subject")
    if row_sub is None:
        session.add(IdSeq(name="subject", last_value=0))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_sequence_rows(session)
        session.commit()
