from __future__ import annotations

import threading

from schemas import SubjectCreate, StudentCreate, StudentPatch, StudentPut


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class InMemoryStore:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._student_seq = 0
        self._subject_seq = 0
        self.students: dict[str, dict] = {}
        self.subjects: dict[str, dict] = {}
        self.enrollments: dict[str, set[str]] = {}  # subject_id -> set(student_id)

    def reset(self) -> None:
        with self._lock:
            self._student_seq = 0
            self._subject_seq = 0
            self.students.clear()
            self.subjects.clear()
            self.enrollments.clear()

    def _next_student_id(self) -> str:
        self._student_seq += 1
        return f"stu_{self._student_seq}"

    def _next_subject_id(self) -> str:
        self._subject_seq += 1
        return f"sub_{self._subject_seq}"

    def create_student(self, data: StudentCreate) -> dict:
        with self._lock:
            student_id = self._next_student_id()
            self.students[student_id] = {
                "id": student_id,
                "name": data.name,
                "email": data.email,
                "course": data.course,
            }
            return self.students[student_id]

    def list_students(self) -> list[dict]:
        with self._lock:
            return list(self.students.values())

    def get_student(self, student_id: str) -> dict:
        with self._lock:
            s = self.students.get(student_id)
            if not s:
                raise NotFoundError("Student not found.")
            return s

    def put_student(self, student_id: str, data: StudentPut) -> dict:
        with self._lock:
            if student_id not in self.students:
                raise NotFoundError("Student not found.")
            self.students[student_id] = {
                "id": student_id,
                "name": data.name,
                "email": data.email,
                "course": data.course,
            }
            return self.students[student_id]

    def patch_student(self, student_id: str, data: StudentPatch) -> dict:
        with self._lock:
            s = self.get_student(student_id)
            if data.name is not None:
                s["name"] = data.name
            if data.email is not None:
                s["email"] = data.email
            if data.course is not None:
                s["course"] = data.course
            return s

    def delete_student(self, student_id: str) -> None:
        with self._lock:
            if student_id not in self.students:
                raise NotFoundError("Student not found.")
            del self.students[student_id]
            for subject_id, student_ids in self.enrollments.items():
                student_ids.discard(student_id)

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

    def enroll(self, subject_id: str, student_id: str) -> None:
        with self._lock:
            self.get_subject(subject_id)
            self.get_student(student_id)
            self.enrollments.setdefault(subject_id, set()).add(student_id)

    def unenroll(self, subject_id: str, student_id: str) -> None:
        with self._lock:
            self.get_subject(subject_id)
            self.get_student(student_id)
            self.enrollments.setdefault(subject_id, set()).discard(student_id)

    def student_subject_ids(self, student_id: str) -> list[str]:
        with self._lock:
            self.get_student(student_id)
            subject_ids: list[str] = []
            for sub_id, student_ids in self.enrollments.items():
                if student_id in student_ids:
                    subject_ids.append(sub_id)
            subject_ids.sort()
            return subject_ids

    def subject_student_ids(self, subject_id: str) -> list[str]:
        with self._lock:
            self.get_subject(subject_id)
            ids = sorted(self.enrollments.get(subject_id, set()))
            return ids


store = InMemoryStore()
