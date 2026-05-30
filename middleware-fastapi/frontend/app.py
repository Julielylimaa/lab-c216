from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import requests
from flask import Flask, flash, redirect, render_template, request, url_for
from markupsafe import Markup

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-in-production")

FIELD_LABELS: dict[str, str] = {
    "nome": "Nome",
    "email": "E-mail",
    "curso": "Curso",
    "code": "Código da disciplina",
    "name": "Nome da disciplina",
}

STATUS_HINTS: dict[int, str] = {
    400: "Requisição inválida.",
    404: "Recurso não encontrado.",
    409: "Conflito com um registro existente.",
    422: "Dados inválidos.",
    500: "Erro interno na API.",
    502: "A API está indisponível.",
    503: "A API está temporariamente indisponível.",
}

MESSAGE_PT: dict[str, str] = {
    "Invalid subject code. Example: MAT101.": (
        "Código inválido. Use 2 a 10 letras maiúsculas seguidas de até 6 dígitos (ex.: MAT101)."
    ),
    "Invalid subject name.": "Nome da disciplina inválido.",
    "Subject not found.": "Disciplina não encontrada.",
    "String should have at least 2 characters": "Deve ter no mínimo 2 caracteres.",
    "String should have at least 1 characters": "Não pode ficar vazio.",
    "String should have at least 3 characters": "Deve ter no mínimo 3 caracteres.",
    "value is not a valid email address": "E-mail inválido.",
    "Field required": "Campo obrigatório.",
    "Input should be a valid string": "Valor inválido.",
}


@dataclass
class ApiErrorInfo:
    summary: str
    details: list[str] = field(default_factory=list)
    status_code: int | None = None

    def flash_message(self) -> str | Markup:
        if not self.details:
            return self.summary
        if len(self.details) == 1 and self.summary == self.details[0]:
            return self.details[0]
        items = "".join(f"<li>{Markup.escape(line)}</li>" for line in self.details)
        title = Markup.escape(self.summary)
        return Markup(f"<strong>{title}</strong><ul class=\"error-details\">{items}</ul>")


def _field_label(loc: list[Any]) -> str | None:
    parts = [str(x) for x in loc if str(x) not in {"body", "query", "path"}]
    if not parts:
        return None
    key = parts[-1]
    return FIELD_LABELS.get(key, key.replace("_", " ").capitalize())


def _normalize_message(msg: str) -> str:
    text = msg.strip()
    if text.startswith("Value error, "):
        text = text[len("Value error, ") :]
    return MESSAGE_PT.get(text, text)


def _parse_validation_detail(detail: list[Any]) -> ApiErrorInfo:
    lines: list[str] = []
    for item in detail:
        if not isinstance(item, dict):
            lines.append(_normalize_message(str(item)))
            continue

        label = _field_label(item.get("loc", []))
        message = _normalize_message(str(item.get("msg", "Erro de validação.")))
        if label:
            lines.append(f"{label}: {message}")
        else:
            lines.append(message)

    summary = "Corrija os campos abaixo:" if len(lines) > 1 else (lines[0] if lines else "Dados inválidos.")
    return ApiErrorInfo(summary=summary, details=lines or [summary], status_code=422)


def _parse_api_error(response: requests.Response) -> ApiErrorInfo:
    status = response.status_code
    hint = STATUS_HINTS.get(status, f"Erro na API (HTTP {status}).")

    try:
        data = response.json()
    except ValueError:
        body = (response.text or "").strip()
        detail = body[:300] + ("..." if len(body) > 300 else "")
        message = f"{hint} Resposta: {detail}" if detail else hint
        return ApiErrorInfo(summary=message, details=[message], status_code=status)

    if isinstance(data, dict):
        if "error" in data:
            message = _normalize_message(str(data["error"]))
            return ApiErrorInfo(summary=message, details=[message], status_code=status)

        if "detail" in data:
            detail = data["detail"]
            if isinstance(detail, list):
                info = _parse_validation_detail(detail)
                info.status_code = status
                if status != 422:
                    info.summary = hint
                return info
            message = _normalize_message(str(detail))
            return ApiErrorInfo(summary=message, details=[message], status_code=status)

        if "message" in data:
            message = _normalize_message(str(data["message"]))
            return ApiErrorInfo(summary=message, details=[message], status_code=status)

    message = hint
    return ApiErrorInfo(summary=message, details=[message], status_code=status)


def _flash_api_error(info: ApiErrorInfo) -> None:
    flash(info.flash_message(), "error")


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def _request(self, method: str, path: str, **kwargs: Any) -> tuple[bool, Any, ApiErrorInfo | None]:
        try:
            response = requests.request(method, f"{self.base_url}{path}", timeout=10, **kwargs)
        except requests.ConnectionError:
            info = ApiErrorInfo(
                summary="Não foi possível conectar à API.",
                details=[
                    f"Verifique se o backend está rodando em {self.base_url}.",
                    "No Docker: execute `docker compose up -d`.",
                ],
            )
            return False, None, info
        except requests.Timeout:
            info = ApiErrorInfo(
                summary="A API demorou para responder.",
                details=["Tente novamente em alguns instantes."],
            )
            return False, None, info
        except requests.RequestException as exc:
            info = ApiErrorInfo(
                summary="Falha ao comunicar com a API.",
                details=[str(exc)],
            )
            return False, None, info

        if response.ok:
            if response.status_code == 204 or not response.content:
                return True, None, None
            try:
                return True, response.json(), None
            except ValueError:
                return True, None, None

        return False, None, _parse_api_error(response)

    def list_alunos(self) -> tuple[list[dict], ApiErrorInfo | None]:
        ok, data, err = self._request("GET", "/api/v1/alunos/")
        if not ok:
            return [], err
        return data or [], None

    def get_aluno(self, aluno_id: str) -> tuple[dict | None, ApiErrorInfo | None]:
        ok, data, err = self._request("GET", f"/api/v1/alunos/{aluno_id}")
        return (data if ok else None), err

    def create_aluno(self, payload: dict) -> tuple[dict | None, ApiErrorInfo | None]:
        ok, data, err = self._request("POST", "/api/v1/alunos/", json=payload)
        return (data if ok else None), err

    def update_aluno(self, aluno_id: str, payload: dict) -> tuple[dict | None, ApiErrorInfo | None]:
        ok, data, err = self._request("PATCH", f"/api/v1/alunos/{aluno_id}", json=payload)
        return (data if ok else None), err

    def delete_aluno(self, aluno_id: str) -> ApiErrorInfo | None:
        ok, _, err = self._request("DELETE", f"/api/v1/alunos/{aluno_id}")
        return err if not ok else None

    def reset_alunos(self) -> tuple[int | None, ApiErrorInfo | None]:
        ok, data, err = self._request("DELETE", "/api/v1/alunos/")
        if not ok:
            return None, err
        return (data or {}).get("removidos"), None

    def list_subjects(self) -> tuple[list[dict], ApiErrorInfo | None]:
        ok, data, err = self._request("GET", "/subjects")
        if not ok:
            return [], err
        return data or [], None

    def create_subject(self, payload: dict) -> tuple[dict | None, ApiErrorInfo | None]:
        ok, data, err = self._request("POST", "/subjects", json=payload)
        return (data if ok else None), err

    def enroll(self, subject_id: str, aluno_id: str) -> ApiErrorInfo | None:
        ok, _, err = self._request("PUT", f"/subjects/{subject_id}/enroll/{aluno_id}")
        return err if not ok else None


api = ApiClient(API_BASE_URL)


def _alunos_por_id(alunos: list[dict]) -> dict[str, str]:
    return {a["id"]: a["nome"] for a in alunos}


def _subjects_with_names(subjects: list[dict], alunos_por_id: dict[str, str]) -> list[dict]:
    enriched: list[dict] = []
    for subject in subjects:
        enrolled_names = [
            alunos_por_id.get(student_id, student_id)
            for student_id in subject.get("enrolled_student_ids", [])
        ]
        enriched.append({**subject, "enrolled_names": enrolled_names})
    return enriched


def _subjects_por_id(subjects: list[dict]) -> dict[str, dict]:
    return {s["id"]: s for s in subjects}


def _load_dashboard() -> dict[str, Any]:
    alunos, alunos_err = api.list_alunos()
    subjects, subjects_err = api.list_subjects()
    alunos_map = _alunos_por_id(alunos)
    return {
        "alunos": alunos,
        "subjects": _subjects_with_names(subjects, alunos_map),
        "alunos_err": alunos_err,
        "subjects_err": subjects_err,
    }


@app.route("/")
def index():
    return render_template("index.html", **_load_dashboard())


@app.route("/alunos/novo", methods=["GET", "POST"])
def aluno_novo():
    if request.method == "GET":
        return render_template("aluno_novo.html")

    _, err = api.create_aluno(
        {
            "nome": request.form.get("nome", "").strip(),
            "email": request.form.get("email", "").strip(),
            "curso": request.form.get("curso", "").strip().upper(),
        }
    )
    if err:
        _flash_api_error(err)
        return render_template(
            "aluno_novo.html",
            form={
                "nome": request.form.get("nome", ""),
                "email": request.form.get("email", ""),
                "curso": request.form.get("curso", ""),
            },
        )

    flash("Aluno cadastrado com sucesso.", "success")
    return redirect(url_for("index"))


@app.route("/alunos/<aluno_id>/editar", methods=["GET", "POST"])
def aluno_editar(aluno_id: str):
    if request.method == "GET":
        aluno, err = api.get_aluno(aluno_id)
        if err:
            _flash_api_error(err)
            return redirect(url_for("index"))

        subjects, subjects_err = api.list_subjects()
        if subjects_err:
            _flash_api_error(subjects_err)

        enrolled = [
            _subjects_por_id(subjects).get(sid, {"id": sid, "code": sid, "name": sid})
            for sid in aluno.get("subject_ids", [])
        ]
        available = [s for s in subjects if s["id"] not in aluno.get("subject_ids", [])]

        return render_template(
            "aluno_editar.html",
            aluno=aluno,
            enrolled_subjects=enrolled,
            available_subjects=available,
        )

    payload = {
        "nome": request.form.get("nome", "").strip(),
        "email": request.form.get("email", "").strip(),
        "curso": request.form.get("curso", "").strip().upper(),
    }

    updated, err = api.update_aluno(aluno_id, payload)
    if err:
        _flash_api_error(err)
        aluno, _ = api.get_aluno(aluno_id)
        subjects, _ = api.list_subjects()
        enrolled = [
            _subjects_por_id(subjects).get(sid, {"id": sid, "code": sid, "name": sid})
            for sid in (aluno or {}).get("subject_ids", [])
        ]
        available = [s for s in subjects if s["id"] not in (aluno or {}).get("subject_ids", [])]
        return render_template(
            "aluno_editar.html",
            aluno=aluno or {"id": aluno_id, **payload, "subject_ids": []},
            enrolled_subjects=enrolled,
            available_subjects=available,
        )

    flash(f"Aluno {updated['id']} atualizado.", "success")
    return redirect(url_for("index"))


@app.post("/alunos/<aluno_id>/matricular")
def aluno_matricular(aluno_id: str):
    subject_id = request.form.get("subject_id", "").strip()
    if not subject_id:
        flash("Selecione uma disciplina para matricular.", "error")
        return redirect(url_for("aluno_editar", aluno_id=aluno_id))

    err = api.enroll(subject_id, aluno_id)
    if err:
        _flash_api_error(err)
    else:
        flash("Aluno matriculado na disciplina.", "success")
    return redirect(url_for("aluno_editar", aluno_id=aluno_id))


@app.post("/alunos/<aluno_id>/excluir")
def delete_aluno(aluno_id: str):
    err = api.delete_aluno(aluno_id)
    if err:
        _flash_api_error(err)
    else:
        flash(f"Aluno {aluno_id} removido.", "success")
    return redirect(url_for("index"))


@app.post("/alunos/reset")
def reset_alunos():
    removidos, err = api.reset_alunos()
    if err:
        _flash_api_error(err)
    else:
        flash(f"Todos os alunos foram removidos ({removidos or 0} registro(s)).", "success")
    return redirect(url_for("index"))


@app.route("/disciplinas/nova", methods=["GET", "POST"])
def disciplina_nova():
    if request.method == "GET":
        return render_template("disciplina_nova.html")

    _, err = api.create_subject(
        {
            "code": request.form.get("code", "").strip().upper(),
            "name": request.form.get("name", "").strip(),
        }
    )
    if err:
        _flash_api_error(err)
        return render_template(
            "disciplina_nova.html",
            form={
                "code": request.form.get("code", ""),
                "name": request.form.get("name", ""),
            },
        )

    flash("Disciplina cadastrada com sucesso.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
