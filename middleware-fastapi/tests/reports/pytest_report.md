**Resumo**: 9 passed, 0 failed, 0 skipped, 9 total

# Relatório de testes (pytest)

- Gerado em: 2026-05-04T17:16:20.157601+00:00
- Exit status: 0

## O que foi validado

- CRUD de **alunos** em `/api/v1/alunos/` (criação, listagem, GET por ID, PATCH, DELETE, reset).
- CRUD básico de **matérias** (criação, listagem com `enrolled_count`).
- **Matrícula** e **desmatrícula** de estudante em matéria.
- **Contagem** de matriculados por matéria (`enrolled_count`) após mudanças.
- Tratamento de erro **404** para recursos inexistentes.
- Validações (ex.: email inválido retorna **422**).

## Resultados por teste (o que passou e retornos)

### test_atividade_tres_alunos_por_curso_listagem_busca_patch_delete

- Resultado: **passed**
- Chamadas e retornos:
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GES",
  "email": "ges0@example.com",
  "id": "GES1",
  "matricula": 1,
  "nome": "Aluno GES 0",
  "subject_ids": []
}
```
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GES",
  "email": "ges1@example.com",
  "id": "GES2",
  "matricula": 2,
  "nome": "Aluno GES 1",
  "subject_ids": []
}
```
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GES",
  "email": "ges2@example.com",
  "id": "GES3",
  "matricula": 3,
  "nome": "Aluno GES 2",
  "subject_ids": []
}
```
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GEC",
  "email": "gec0@example.com",
  "id": "GEC1",
  "matricula": 1,
  "nome": "Aluno GEC 0",
  "subject_ids": []
}
```
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GEC",
  "email": "gec1@example.com",
  "id": "GEC2",
  "matricula": 2,
  "nome": "Aluno GEC 1",
  "subject_ids": []
}
```
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GEC",
  "email": "gec2@example.com",
  "id": "GEC3",
  "matricula": 3,
  "nome": "Aluno GEC 2",
  "subject_ids": []
}
```
  - **GET /api/v1/alunos/** → **200**

```json
[
  {
    "curso": "GES",
    "email": "ges0@example.com",
    "id": "GES1",
    "matricula": 1,
    "nome": "Aluno GES 0",
    "subject_ids": []
  },
  {
    "curso": "GES",
    "email": "ges1@example.com",
    "id": "GES2",
    "matricula": 2,
    "nome": "Aluno GES 1",
    "subject_ids": []
  },
  {
    "curso": "GES",
    "email": "ges2@example.com",
    "id": "GES3",
    "matricula": 3,
    "nome": "Aluno GES 2",
    "subject_ids": []
  },
  {
    "curso": "GEC",
    "email": "gec0@example.com",
    "id": "GEC1",
    "matricula": 1,
    "nome": "Aluno GEC 0",
    "subject_ids": []
  },
  {
    "curso": "GEC",
    "email": "gec1@example.com",
    "id": "GEC2",
    "matricula": 2,
    "nome": "Aluno GEC 1",
    "subject_ids": []
  },
  {
    "curso": "GEC",
    "email": "gec2@example.com",
    "id": "GEC3",
    "matricula": 3,
    "nome": "Aluno GEC 2",
    "subject_ids": []
  }
]
```
  - **GET /api/v1/alunos/GES1** → **200**

```json
{
  "curso": "GES",
  "email": "ges0@example.com",
  "id": "GES1",
  "matricula": 1,
  "nome": "Aluno GES 0",
  "subject_ids": []
}
```
  - **PATCH /api/v1/alunos/GES1** → **200**

```json
{
  "curso": "GES",
  "email": "ges0@example.com",
  "id": "GES1",
  "matricula": 1,
  "nome": "Atualizado GES",
  "subject_ids": []
}
```
  - **DELETE /api/v1/alunos/GES1** → **200**

```json
{
  "id": "GES1",
  "status": "deleted"
}
```
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GES",
  "email": "novoges@example.com",
  "id": "GES4",
  "matricula": 4,
  "nome": "Novo GES",
  "subject_ids": []
}
```

### test_delete_todos_alunos_nao_reinicia_contador_de_matricula

- Resultado: **passed**
- Chamadas e retornos:
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GES",
  "email": "a1@example.com",
  "id": "GES1",
  "matricula": 1,
  "nome": "A",
  "subject_ids": []
}
```
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GES",
  "email": "b1@example.com",
  "id": "GES2",
  "matricula": 2,
  "nome": "B",
  "subject_ids": []
}
```
  - **DELETE /api/v1/alunos/** → **200**

```json
{
  "removidos": 2,
  "status": "reset"
}
```
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GES",
  "email": "c1@example.com",
  "id": "GES3",
  "matricula": 3,
  "nome": "C",
  "subject_ids": []
}
```

### test_create_student_and_list_students

- Resultado: **passed**
- Chamadas e retornos:
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GES",
  "email": "ana@example.com",
  "id": "GES1",
  "matricula": 1,
  "nome": "Ana",
  "subject_ids": []
}
```
  - **GET /api/v1/alunos/** → **200**

```json
[
  {
    "curso": "GES",
    "email": "ana@example.com",
    "id": "GES1",
    "matricula": 1,
    "nome": "Ana",
    "subject_ids": []
  }
]
```

### test_invalid_email_is_422

- Resultado: **passed**
- Chamadas e retornos:
  - **POST /api/v1/alunos/** → **422**

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
      "msg": "Value error, E-mail inválido. Use um endereço válido (ex.: nome@dominio.com).",
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
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GES",
  "email": "ana@example.com",
  "id": "GES1",
  "matricula": 1,
  "nome": "Ana",
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
  - **PUT /subjects/sub_1/enroll/GES1** → **200**

```json
{
  "code": "MAT101",
  "enrolled_count": 1,
  "enrolled_student_ids": [
    "GES1"
  ],
  "id": "sub_1",
  "name": "Cálculo I"
}
```
  - **GET /api/v1/alunos/** → **200**

```json
[
  {
    "curso": "GES",
    "email": "ana@example.com",
    "id": "GES1",
    "matricula": 1,
    "nome": "Ana",
    "subject_ids": [
      "sub_1"
    ]
  }
]
```
  - **PATCH /subjects/sub_1/unenroll/GES1** → **200**

```json
{
  "code": "MAT101",
  "enrolled_count": 0,
  "enrolled_student_ids": [],
  "id": "sub_1",
  "name": "Cálculo I"
}
```

### test_patch_aluno_nome_e_troca_de_curso_novo_id

- Resultado: **passed**
- Chamadas e retornos:
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GES",
  "email": "ana@example.com",
  "id": "GES1",
  "matricula": 1,
  "nome": "Ana",
  "subject_ids": []
}
```
  - **PATCH /api/v1/alunos/GES1** → **200**

```json
{
  "curso": "GES",
  "email": "ana@example.com",
  "id": "GES1",
  "matricula": 1,
  "nome": "Ana M.",
  "subject_ids": []
}
```
  - **PATCH /api/v1/alunos/GES1** → **200**

```json
{
  "curso": "GEC",
  "email": "ana@example.com",
  "id": "GEC1",
  "matricula": 1,
  "nome": "Ana M.",
  "subject_ids": []
}
```

### test_delete_student_cleans_enrollment_count

- Resultado: **passed**
- Chamadas e retornos:
  - **POST /api/v1/alunos/** → **201**

```json
{
  "curso": "GES",
  "email": "ana@example.com",
  "id": "GES1",
  "matricula": 1,
  "nome": "Ana",
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
  - **PUT /subjects/sub_1/enroll/GES1** → **200**

```json
{
  "code": "MAT101",
  "enrolled_count": 1,
  "enrolled_student_ids": [
    "GES1"
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
      "GES1"
    ],
    "id": "sub_1",
    "name": "Cálculo I"
  }
]
```
  - **DELETE /api/v1/alunos/GES1** → **200**

```json
{
  "id": "GES1",
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
  - **DELETE /api/v1/alunos/GES999** → **404**

```json
{
  "error": "Aluno não encontrado."
}
```
