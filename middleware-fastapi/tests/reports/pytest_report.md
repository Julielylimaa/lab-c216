**Resumo**: 7 passed, 0 failed, 0 skipped, 7 total

# Relatório de testes (pytest)

- Gerado em: 2026-04-21T19:15:32.258930+00:00
- Exit status: 0

## O que foi validado

- CRUD básico de **estudantes** (criação, listagem, PUT, PATCH, DELETE).
- CRUD básico de **matérias** (criação, listagem com `enrolled_count`).
- **Matrícula** e **desmatrícula** de estudante em matéria.
- **Contagem** de matriculados por matéria (`enrolled_count`) após mudanças.
- Tratamento de erro **404** para recursos inexistentes.
- Validações (ex.: email inválido retorna **422**).

## Resultados por teste (o que passou e retornos)

### test_create_student_and_list_students

- Resultado: **passed**
- Chamadas e retornos:
  - **POST /students** → **201**

```json
{
  "course": "GES",
  "email": "ana@example.com",
  "id": "stu_1",
  "name": "Ana",
  "subject_ids": []
}
```
  - **GET /students** → **200**

```json
[
  {
    "course": "GES",
    "email": "ana@example.com",
    "id": "stu_1",
    "name": "Ana",
    "subject_ids": []
  }
]
```

### test_invalid_email_is_422

- Resultado: **passed**
- Chamadas e retornos:
  - **POST /students** → **422**

```json
{
  "detail": [
    {
      "ctx": {
        "error": {}
      },
      "input": "ana_at_example.com",
      "loc": [
        "body",
        "email"
      ],
      "msg": "Value error, Invalid email. Use a valid address (e.g. name@domain.com).",
      "type": "value_error"
    }
  ]
}
```

### test_create_subject_and_list_subjects_with_count

- Resultado: **passed**
- Chamadas e retornos:
  - **POST /subjects** → **201**

```json
{
  "code": "MAT101",
  "enrolled_count": 0,
  "enrolled_student_ids": [],
  "id": "sub_1",
  "name": "Cálculo I"
}
```
  - **GET /subjects** → **200**

```json
[
  {
    "code": "MAT101",
    "enrolled_count": 0,
    "enrolled_student_ids": [],
    "id": "sub_1",
    "name": "Cálculo I"
  }
]
```

### test_enroll_unenroll_and_count_updates

- Resultado: **passed**
- Chamadas e retornos:
  - **POST /students** → **201**

```json
{
  "course": "GES",
  "email": "ana@example.com",
  "id": "stu_1",
  "name": "Ana",
  "subject_ids": []
}
```
  - **POST /subjects** → **201**

```json
{
  "code": "MAT101",
  "enrolled_count": 0,
  "enrolled_student_ids": [],
  "id": "sub_1",
  "name": "Cálculo I"
}
```
  - **PUT /subjects/sub_1/enroll/stu_1** → **200**

```json
{
  "code": "MAT101",
  "enrolled_count": 1,
  "enrolled_student_ids": [
    "stu_1"
  ],
  "id": "sub_1",
  "name": "Cálculo I"
}
```
  - **GET /students** → **200**

```json
[
  {
    "course": "GES",
    "email": "ana@example.com",
    "id": "stu_1",
    "name": "Ana",
    "subject_ids": [
      "sub_1"
    ]
  }
]
```
  - **PATCH /subjects/sub_1/unenroll/stu_1** → **200**

```json
{
  "code": "MAT101",
  "enrolled_count": 0,
  "enrolled_student_ids": [],
  "id": "sub_1",
  "name": "Cálculo I"
}
```

### test_put_and_patch_student

- Resultado: **passed**
- Chamadas e retornos:
  - **POST /students** → **201**

```json
{
  "course": "GES",
  "email": "ana@example.com",
  "id": "stu_1",
  "name": "Ana",
  "subject_ids": []
}
```
  - **PUT /students/stu_1** → **200**

```json
{
  "course": "GET",
  "email": "anamaria@example.com",
  "id": "stu_1",
  "name": "Ana Maria",
  "subject_ids": []
}
```
  - **PATCH /students/stu_1** → **200**

```json
{
  "course": "GET",
  "email": "anamaria@example.com",
  "id": "stu_1",
  "name": "Ana M.",
  "subject_ids": []
}
```

### test_delete_student_cleans_enrollment_count

- Resultado: **passed**
- Chamadas e retornos:
  - **POST /students** → **201**

```json
{
  "course": "GES",
  "email": "ana@example.com",
  "id": "stu_1",
  "name": "Ana",
  "subject_ids": []
}
```
  - **POST /subjects** → **201**

```json
{
  "code": "MAT101",
  "enrolled_count": 0,
  "enrolled_student_ids": [],
  "id": "sub_1",
  "name": "Cálculo I"
}
```
  - **PUT /subjects/sub_1/enroll/stu_1** → **200**

```json
{
  "code": "MAT101",
  "enrolled_count": 1,
  "enrolled_student_ids": [
    "stu_1"
  ],
  "id": "sub_1",
  "name": "Cálculo I"
}
```
  - **GET /subjects** → **200**

```json
[
  {
    "code": "MAT101",
    "enrolled_count": 1,
    "enrolled_student_ids": [
      "stu_1"
    ],
    "id": "sub_1",
    "name": "Cálculo I"
  }
]
```
  - **DELETE /students/stu_1** → **200**

```json
{
  "id": "stu_1",
  "status": "deleted"
}
```
  - **GET /subjects** → **200**

```json
[
  {
    "code": "MAT101",
    "enrolled_count": 0,
    "enrolled_student_ids": [],
    "id": "sub_1",
    "name": "Cálculo I"
  }
]
```

### test_not_found_returns_404

- Resultado: **passed**
- Chamadas e retornos:
  - **DELETE /students/stu_999** → **404**

```json
{
  "error": "Student not found."
}
```
