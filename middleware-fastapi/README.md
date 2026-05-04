# Middleware FastAPI — Gerenciador de alunos

API em **FastAPI** com CRUD de alunos em `/api/v1/alunos/` (curso **GES** ou **GEC**, matrícula e ID automáticos) e rotas auxiliares de disciplinas em `/subjects`.

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/) (forma **obrigatória** de executar a API na atividade)
- Para testes **fora** do container: Python **3.12+** (recomendado, alinhado ao `Dockerfile`)

## Rodar o projeto (API)

Na pasta `middleware-fastapi/`:

```bash
docker compose up --build
```

- A API sobe em **http://127.0.0.1:8000**
- Documentação interativa: **http://127.0.0.1:8000/docs** (Swagger) ou **http://127.0.0.1:8000/redoc**

Para rodar em segundo plano:

```bash
docker compose up --build -d
```

Para parar:

```bash
docker compose down
```

### Exemplo rápido (cadastrar um aluno)

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/alunos/ \
  -H "Content-Type: application/json" \
  -d '{"nome":"Maria","email":"maria@example.com","curso":"GES"}'
```

## Rodar os testes automatizados

### Opção A — na sua máquina (Python local)

1. Entre na pasta do projeto e crie um ambiente virtual:

   ```bash
   cd middleware-fastapi
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

2. Instale as dependências e execute o **pytest**:

   ```bash
   pip install -r requirements.txt
   pytest tests/test_api.py -v
   ```

O arquivo `pytest.ini` já define `pythonpath = .`, então os imports (`main`, `storage`, etc.) funcionam sem configurar `PYTHONPATH` manualmente.

### Opção B — dentro do Docker (mesma imagem da API)

Com o `docker compose` build já feito ao menos uma vez:

```bash
cd middleware-fastapi
docker compose run --rm --no-deps api pytest tests/test_api.py -v
```

- O volume `./tests/reports` é montado em `/app/tests/reports`: ao final da suíte é gerado o relatório **`tests/reports/pytest_report.md`**.

### Saída e relatório

- Com `-s` (já está em `pytest.ini` via `addopts`), os logs de cada requisição aparecem no terminal.
- O relatório em Markdown é atualizado em **`tests/reports/pytest_report.md`** após a sessão de testes.

## Estrutura útil

| Arquivo / pasta   | Descrição                          |
|-------------------|-------------------------------------|
| `main.py`         | App FastAPI e rotas                |
| `schemas.py`      | Modelos Pydantic (entrada/saída)   |
| `storage.py`      | Armazenamento em memória           |
| `docker-compose.yml` | Orquestra o serviço `api`       |
| `Dockerfile`      | Imagem Python 3.12 + dependências  |
| `tests/`          | Testes com `TestClient` (FastAPI)  |

## Resumo

| Objetivo              | Comando principal                                      |
|-----------------------|--------------------------------------------------------|
| Subir a API           | `docker compose up --build`                           |
| Testes (local)        | `source .venv/bin/activate && pytest tests/test_api.py -v` |
| Testes (container)    | `docker compose run --rm --no-deps api pytest tests/test_api.py -v` |
