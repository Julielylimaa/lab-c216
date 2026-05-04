from __future__ import annotations

import threading

from schemas import AlunoCreate, AlunoPatch, SubjectCreate


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class InMemoryStore:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._subject_seq = 0
        self._course_matricula_seq: dict[str, int] = {c: 0 for c in ("GES", "GEC")}
        self.students: dict[str, dict] = {}
        self.subjects: dict[str, dict] = {}
        self.enrollments: dict[str, set[str]] = {}  # subject_id -> set(aluno_id)

    def reset(self) -> None:
        with self._lock:
            self._subject_seq = 0
            for c in self._course_matricula_seq:
                self._course_matricula_seq[c] = 0
            self.students.clear()
            self.subjects.clear()
            self.enrollments.clear()

    def _issue_matricula_and_id(self, curso: str) -> tuple[int, str]:
        self._course_matricula_seq[curso] = self._course_matricula_seq.get(curso, 0) + 1
        matricula = self._course_matricula_seq[curso]
        return matricula, f"{curso}{matricula}"

    def _next_subject_id(self) -> str:
        self._subject_seq += 1
        return f"sub_{self._subject_seq}"

    def create_student(self, data: AlunoCreate) -> dict:
        with self._lock:
            matricula, aluno_id = self._issue_matricula_and_id(data.curso)
            self.students[aluno_id] = {
                "id": aluno_id,
                "nome": data.nome,
                "email": data.email,
                "curso": data.curso,
                "matricula": matricula,
            }
            return self.students[aluno_id]

    def list_students(self) -> list[dict]:
        with self._lock:
            return list(self.students.values())

    def get_student(self, aluno_id: str) -> dict:
        with self._lock:
            s = self.students.get(aluno_id)
            if not s:
                raise NotFoundError("Aluno não encontrado.")
            return s

    def patch_student(self, aluno_id: str, data: AlunoPatch) -> dict:
        with self._lock:
            s = self.students.get(aluno_id)
            if not s:
                raise NotFoundError("Aluno não encontrado.")
            if data.nome is not None:
                s["nome"] = data.nome
            if data.email is not None:
                s["email"] = data.email
            if data.curso is not None and data.curso != s["curso"]:
                old_id = s["id"]
                matricula, new_id = self._issue_matricula_and_id(data.curso)
                s["curso"] = data.curso
                s["matricula"] = matricula
                s["id"] = new_id
                del self.students[old_id]
                self.students[new_id] = s
                for student_ids in self.enrollments.values():
                    if old_id in student_ids:
                        student_ids.discard(old_id)
                        student_ids.add(new_id)
                return s
            return s

    def delete_student(self, aluno_id: str) -> None:
        with self._lock:
            if aluno_id not in self.students:
                raise NotFoundError("Aluno não encontrado.")
            del self.students[aluno_id]
            for student_ids in self.enrollments.values():
                student_ids.discard(aluno_id)

    def clear_all_students(self) -> int:
        with self._lock:
            n = len(self.students)
            self.students.clear()
            for student_ids in self.enrollments.values():
                student_ids.clear()
            return n

    def create_subject(self, data: SubjectCreate) -> dict:
        with self._lock:
            subject_id = self._next_subject_id()
            self.subjects[subject_id] = {
                "id": subject_id,
                "code": data.code,
                "name": data.name,
            }
            self.enrollments.setdefault(subject_id, set())
            return self.subjects[subject_id]

    def list_subjects(self) -> list[dict]:
        with self._lock:
            return list(self.subjects.values())

    def get_subject(self, subject_id: str) -> dict:
        with self._lock:
            sub = self.subjects.get(subject_id)
            if not sub:
                raise NotFoundError("Subject not found.")
            return sub

    def enroll(self, subject_id: str, aluno_id: str) -> None:
        with self._lock:
            self.get_subject(subject_id)
            self.get_student(aluno_id)
            self.enrollments.setdefault(subject_id, set()).add(aluno_id)

    def unenroll(self, subject_id: str, aluno_id: str) -> None:
        with self._lock:
            self.get_subject(subject_id)
            self.get_student(aluno_id)
            self.enrollments.setdefault(subject_id, set()).discard(aluno_id)

    def student_subject_ids(self, aluno_id: str) -> list[str]:
        with self._lock:
            self.get_student(aluno_id)
            subject_ids: list[str] = []
            for sub_id, aluno_ids in self.enrollments.items():
                if aluno_id in aluno_ids:
                    subject_ids.append(sub_id)
            subject_ids.sort()
            return subject_ids

    def subject_student_ids(self, subject_id: str) -> list[str]:
        with self._lock:
            self.get_subject(subject_id)
            return sorted(self.enrollments.get(subject_id, set()))


store = InMemoryStore()
