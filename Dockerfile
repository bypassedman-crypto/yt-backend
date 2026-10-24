FROM python:3.12-slim

RUN apt-get update && apt-get install -y ffmpeg curl unzip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -U -r requirements.txt

COPY . .

CMD gunicorn main:app --bind 0.0.0.0:${PORT:-10000} --timeout 300 --workers 1
