FROM python:3.12-slim

WORKDIR /app

COPY students_crud.py .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
