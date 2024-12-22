FROM python:3.12-alpine3.20

WORKDIR /app

RUN python -m pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . /app

EXPOSE 3000

ENTRYPOINT ["python", "main.py"]