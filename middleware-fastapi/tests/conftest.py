from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from main import app
from storage import store


@dataclass
class CallLog:
    method: str
    url: str
    status_code: int
    response_json: Any | None


class ApiLogger:
    def __init__(self, client: TestClient, calls: list[CallLog]) -> None:
        self._client = client
        self.calls = calls

    def request(self, method: str, url: str, *, json_body: Any | None = None):
        r = self._client.request(method, url, json=json_body)
        try:
            body = r.json()
        except Exception:
            body = None
        self.calls.append(
            CallLog(
                method=method.upper(),
                url=url,
                status_code=r.status_code,
                response_json=body,
            )
        )
        return r

    def get(self, url: str):
        return self.request("GET", url)

    def post(self, url: str, *, json_body: Any):
        return self.request("POST", url, json_body=json_body)

    def put(self, url: str, *, json_body: Any | None = None):
        return self.request("PUT", url, json_body=json_body)

    def patch(self, url: str, *, json_body: Any | None = None):
        return self.request("PATCH", url, json_body=json_body)

    def delete(self, url: str):
        return self.request("DELETE", url)


def _pretty(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)


@pytest.fixture(autouse=True)
def _reset_store():
    store.reset()


@pytest.fixture
def api(request: pytest.FixtureRequest) -> ApiLogger:
    calls: list[CallLog] = []
    request.node._api_calls = calls  # type: ignore[attr-defined]
    return ApiLogger(TestClient(app), calls)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        item._outcome = rep.outcome  # type: ignore[attr-defined]
        item._longrepr = str(rep.longrepr) if rep.failed else ""  # type: ignore[attr-defined]


def pytest_runtest_logreport(report: pytest.TestReport):
    if report.when != "call":
        return
    item = getattr(report, "item", None)
    if item is None:
        return
    calls: list[CallLog] = getattr(item, "_api_calls", [])
    if not calls:
        return

    # Log simples por teste (aparece mesmo com -q)
    print(f"\n[TEST {getattr(item, 'name', 'unknown')}] {report.outcome}")
    for c in calls:
        print(f"  - {c.method} {c.url} -> {c.status_code}")


def pytest_sessionfinish(session: pytest.Session, exitstatus: int):
    out_dir = Path(__file__).resolve().parent / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "pytest_report.md"

    passed = 0
    failed = 0
    skipped = 0

    lines: list[str] = []
    lines.append("# Relatório de testes (pytest)")
    lines.append("")
    lines.append(f"- Gerado em: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"- Exit status: {exitstatus}")
    lines.append("")
    lines.append("## O que foi validado")
    lines.append("")
    lines.append("- CRUD de **alunos** em `/api/v1/alunos/` (criação, listagem, GET por ID, PATCH, DELETE, reset).")
    lines.append("- CRUD básico de **matérias** (criação, listagem com `enrolled_count`).")
    lines.append("- **Matrícula** e **desmatrícula** de estudante em matéria.")
    lines.append("- **Contagem** de matriculados por matéria (`enrolled_count`) após mudanças.")
    lines.append("- Tratamento de erro **404** para recursos inexistentes.")
    lines.append("- Validações (ex.: email inválido retorna **422**).")
    lines.append("")
    lines.append("## Resultados por teste (o que passou e retornos)")
    lines.append("")

    for item in session.items:
        outcome = getattr(item, "_outcome", "unknown")
        if outcome == "passed":
            passed += 1
        elif outcome == "failed":
            failed += 1
        elif outcome == "skipped":
            skipped += 1

        lines.append(f"### {item.name}")
        lines.append("")
        lines.append(f"- Resultado: **{outcome}**")
        calls: list[CallLog] = getattr(item, "_api_calls", [])
        if calls:
            lines.append("- Chamadas e retornos:")
            for c in calls:
                lines.append(f"  - **{c.method} {c.url}** → **{c.status_code}**")
                if c.response_json is not None:
                    snippet = _pretty(c.response_json)
                    if len(snippet) > 1500:
                        snippet = snippet[:1500] + "\n... (truncado)"
                    lines.append("")
                    lines.append("```json")
                    lines.append(snippet)
                    lines.append("```")
        else:
            lines.append("- Chamadas e retornos: *(nenhuma chamada registrada)*")

        longrepr = getattr(item, "_longrepr", "")
        if longrepr:
            lines.append("")
            lines.append("**Falha (resumo):**")
            lines.append("")
            lines.append("```")
            lines.append(longrepr[:2000] + ("... (truncado)" if len(longrepr) > 2000 else ""))
            lines.append("```")

        lines.append("")

    lines.insert(
        0,
        f"**Resumo**: {passed} passed, {failed} failed, {skipped} skipped, {len(session.items)} total\n",
    )

    out_file.write_text("\n".join(lines), encoding="utf-8")


def pytest_terminal_summary(terminalreporter, exitstatus: int, config):
    terminalreporter.write_line("")
    terminalreporter.write_line("=== Relatório simples (logs) ===")
    terminalreporter.write_line("Cada linha mostra: RESULTADO | METHOD rota -> status")

    session = terminalreporter._session
    if session is None:
        terminalreporter.write_line("Sem sessão disponível para imprimir logs.")
        return

    for item in session.items:
        outcome = getattr(item, "_outcome", "unknown")
        calls: list[CallLog] = getattr(item, "_api_calls", [])
        if not calls:
            terminalreporter.write_line(f"{item.name}: {outcome} (sem chamadas registradas)")
            continue

        terminalreporter.write_line(f"{item.name}: {outcome}")
        for c in calls:
            terminalreporter.write_line(f"  - {c.method} {c.url} -> {c.status_code}")

    out_file = (Path(__file__).resolve().parent / "reports" / "pytest_report.md").as_posix()
    terminalreporter.write_line("")
    terminalreporter.write_line(f"Relatório detalhado (Markdown): {out_file}")
