FROM python:3.13.5

WORKDIR /app

RUN pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
