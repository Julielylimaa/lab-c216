def test_create_student_and_list_students(api):
    r = api.post("/students", json_body={"name": "Ana", "email": "ana@example.com", "course": "GES"})
    assert r.status_code == 201
    body = r.json()
    assert body["id"].startswith("stu_")
    assert body["subject_ids"] == []

    r = api.get("/students")
    assert r.status_code == 200
    students = r.json()
    assert len(students) == 1
    assert students[0]["email"] == "ana@example.com"


def test_invalid_email_is_422(api):
    r = api.post("/students", json_body={"name": "Ana", "email": "ana_at_example.com", "course": "GES"})
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
        "/students",
        json_body={"name": "Ana", "email": "ana@example.com", "course": "GES"},
    ).json()
    sub = api.post("/subjects", json_body={"code": "MAT101", "name": "Cálculo I"}).json()

    r = api.put(f"/subjects/{sub['id']}/enroll/{s['id']}")
    assert r.status_code == 200
    subject = r.json()
    assert subject["enrolled_count"] == 1
    assert subject["enrolled_student_ids"] == [s["id"]]

    r = api.get("/students")
    assert r.status_code == 200
    assert r.json()[0]["subject_ids"] == [sub["id"]]

    r = api.patch(f"/subjects/{sub['id']}/unenroll/{s['id']}")
    assert r.status_code == 200
    subject = r.json()
    assert subject["enrolled_count"] == 0
    assert subject["enrolled_student_ids"] == []


def test_put_and_patch_student(api):
    s = api.post(
        "/students",
        json_body={"name": "Ana", "email": "ana@example.com", "course": "GES"},
    ).json()

    r = api.put(
        f"/students/{s['id']}",
        json_body={"name": "Ana Maria", "email": "anamaria@example.com", "course": "GET"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Ana Maria"
    assert body["course"] == "GET"

    r = api.patch(f"/students/{s['id']}", json_body={"name": "Ana M."})
    assert r.status_code == 200
    assert r.json()["name"] == "Ana M."


def test_delete_student_cleans_enrollment_count(api):
    s = api.post(
        "/students",
        json_body={"name": "Ana", "email": "ana@example.com", "course": "GES"},
    ).json()
    sub = api.post("/subjects", json_body={"code": "MAT101", "name": "Cálculo I"}).json()
    api.put(f"/subjects/{sub['id']}/enroll/{s['id']}")

    r = api.get("/subjects")
    assert r.status_code == 200
    assert r.json()[0]["enrolled_count"] == 1

    r = api.delete(f"/students/{s['id']}")
    assert r.status_code == 200
    assert r.json()["status"] == "deleted"

    r = api.get("/subjects")
    assert r.status_code == 200
    assert r.json()[0]["enrolled_count"] == 0


def test_not_found_returns_404(api):
    r = api.delete("/students/stu_999")
    assert r.status_code == 404
    assert r.json()["error"] == "Student not found."

