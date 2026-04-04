FROM python:3.12-slim

WORKDIR /app

COPY students_crud.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "students_crud.py"]
