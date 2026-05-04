def test_atividade_tres_alunos_por_curso_listagem_busca_patch_delete(api):
    """Requisito 6: 3 por curso, listagem, busca por ID, atualização, remoção."""
    criados_ges = []
    for i in range(3):
        r = api.post(
            "/api/v1/alunos/",
            json_body={
                "nome": f"Aluno GES {i}",
                "email": f"ges{i}@example.com",
                "curso": "GES",
            },
        )
        assert r.status_code == 201
        body = r.json()
        assert body["matricula"] == i + 1
        assert body["id"] == f"GES{i + 1}"
        assert body["curso"] == "GES"
        assert body["subject_ids"] == []
        criados_ges.append(body)

    criados_gec = []
    for i in range(3):
        r = api.post(
            "/api/v1/alunos/",
            json_body={
                "nome": f"Aluno GEC {i}",
                "email": f"gec{i}@example.com",
                "curso": "GEC",
            },
        )
        assert r.status_code == 201
        body = r.json()
        assert body["matricula"] == i + 1
        assert body["id"] == f"GEC{i + 1}"
        criados_gec.append(body)

    r = api.get("/api/v1/alunos/")
    assert r.status_code == 200
    assert len(r.json()) == 6

    aluno_id = criados_ges[0]["id"]
    r = api.get(f"/api/v1/alunos/{aluno_id}")
    assert r.status_code == 200
    assert r.json()["nome"] == "Aluno GES 0"

    r = api.patch(f"/api/v1/alunos/{aluno_id}", json_body={"nome": "Atualizado GES"})
    assert r.status_code == 200
    assert r.json()["nome"] == "Atualizado GES"
    assert r.json()["id"] == aluno_id

    r = api.delete(f"/api/v1/alunos/{aluno_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "deleted"

    r = api.post(
        "/api/v1/alunos/",
        json_body={"nome": "Novo GES", "email": "novoges@example.com", "curso": "GES"},
    )
    assert r.status_code == 201
    assert r.json()["id"] == "GES4"
    assert r.json()["matricula"] == 4


def test_delete_todos_alunos_nao_reinicia_contador_de_matricula(api):
    api.post(
        "/api/v1/alunos/",
        json_body={"nome": "A", "email": "a1@example.com", "curso": "GES"},
    )
    api.post(
        "/api/v1/alunos/",
        json_body={"nome": "B", "email": "b1@example.com", "curso": "GES"},
    )
    r = api.delete("/api/v1/alunos/")
    assert r.status_code == 200
    assert r.json()["status"] == "reset"
    assert r.json()["removidos"] == 2

    r = api.post(
        "/api/v1/alunos/",
        json_body={"nome": "C", "email": "c1@example.com", "curso": "GES"},
    )
    assert r.status_code == 201
    assert r.json()["id"] == "GES3"


def test_create_student_and_list_students(api):
    r = api.post(
        "/api/v1/alunos/",
        json_body={"nome": "Ana", "email": "ana@example.com", "curso": "GES"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == "GES1"
    assert body["matricula"] == 1
    assert body["subject_ids"] == []

    r = api.get("/api/v1/alunos/")
    assert r.status_code == 200
    students = r.json()
    assert len(students) == 1
    assert students[0]["email"] == "ana@example.com"


def test_invalid_email_is_422(api):
    r = api.post(
        "/api/v1/alunos/",
        json_body={"nome": "Ana", "email": "ana_at_example.com", "curso": "GES"},
    )
    assert r.status_code == 422


def test_create_subject_and_list_subjects_with_count(api):
    r = api.post("/subjects", json_body={"code": "MAT101", "name": "Cálculo I"})
    assert r.status_code == 201
    subject = r.json()
    assert subject["id"].startswith("sub_")
    assert subject["enrolled_count"] == 0
    assert subject["enrolled_student_ids"] == []

    r = api.get("/subjects")
    assert r.status_code == 200
    subjects = r.json()
    assert len(subjects) == 1
    assert subjects[0]["enrolled_count"] == 0


def test_enroll_unenroll_and_count_updates(api):
    s = api.post(
        "/api/v1/alunos/",
        json_body={"nome": "Ana", "email": "ana@example.com", "curso": "GES"},
    ).json()
    sub = api.post("/subjects", json_body={"code": "MAT101", "name": "Cálculo I"}).json()

    r = api.put(f"/subjects/{sub['id']}/enroll/{s['id']}")
    assert r.status_code == 200
    subject = r.json()
    assert subject["enrolled_count"] == 1
    assert subject["enrolled_student_ids"] == [s["id"]]

    r = api.get("/api/v1/alunos/")
    assert r.status_code == 200
    assert r.json()[0]["subject_ids"] == [sub["id"]]

    r = api.patch(f"/subjects/{sub['id']}/unenroll/{s['id']}")
    assert r.status_code == 200
    subject = r.json()
    assert subject["enrolled_count"] == 0
    assert subject["enrolled_student_ids"] == []


def test_patch_aluno_nome_e_troca_de_curso_novo_id(api):
    s = api.post(
        "/api/v1/alunos/",
        json_body={"nome": "Ana", "email": "ana@example.com", "curso": "GES"},
    ).json()
    assert s["id"] == "GES1"

    r = api.patch(f"/api/v1/alunos/{s['id']}", json_body={"nome": "Ana M."})
    assert r.status_code == 200
    assert r.json()["nome"] == "Ana M."
    assert r.json()["id"] == "GES1"

    r = api.patch(
        f"/api/v1/alunos/GES1",
        json_body={"curso": "GEC"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "GEC1"
    assert body["curso"] == "GEC"
    assert body["matricula"] == 1


def test_delete_student_cleans_enrollment_count(api):
    s = api.post(
        "/api/v1/alunos/",
        json_body={"nome": "Ana", "email": "ana@example.com", "curso": "GES"},
    ).json()
    sub = api.post("/subjects", json_body={"code": "MAT101", "name": "Cálculo I"}).json()
    api.put(f"/subjects/{sub['id']}/enroll/{s['id']}")

    r = api.get("/subjects")
    assert r.status_code == 200
    assert r.json()[0]["enrolled_count"] == 1

    r = api.delete(f"/api/v1/alunos/{s['id']}")
    assert r.status_code == 200
    assert r.json()["status"] == "deleted"

    r = api.get("/subjects")
    assert r.status_code == 200
    assert r.json()[0]["enrolled_count"] == 0


def test_not_found_returns_404(api):
    r = api.delete("/api/v1/alunos/GES999")
    assert r.status_code == 404
    assert r.json()["error"] == "Aluno não encontrado."
