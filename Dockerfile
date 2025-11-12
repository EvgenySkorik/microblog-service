FROM python:3.12-slim-bookworm

WORKDIR /app
COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/src

WORKDIR /app/src

EXPOSE 8000

CMD ["sh", "-c", "cd /app && alembic upgrade head && uvicorn microblog.main:app --host 0.0.0.0 --port 8000"]
