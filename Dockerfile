FROM python:3.14-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

ENV PYTHONPATH=src

CMD ["uv", "run", "uvicorn", "src.endpoint:app", "--host", "0.0.0.0", "--port", "8000"]
