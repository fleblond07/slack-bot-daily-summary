FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY . .

CMD ["uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
