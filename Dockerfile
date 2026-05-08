FROM python:3.12-slim

WORKDIR /app

COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock

COPY src/ ./src/

ENV PYTHONPATH=/app/src

CMD ["python", "src/main.py"]
