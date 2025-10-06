FROM python:3.13-slim

# Evitiamo buffering, impostiamo ambiente
ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# Copia file di progetto (pyproject + lock)
COPY . /app/

# Installa Poetry
RUN pip install poetry

# Installa le dipendenze (senza installare il package stesso se vuoi)
RUN poetry install --no-root --only main

# Copia il resto del codice

CMD ["python", "agent.py"]
