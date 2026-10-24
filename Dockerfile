FROM python:3.10-slim

# Telepítjük az ffmpeg-et, a nodejs-t és létrehozzuk a yt-dlp által elvárt 'node' szimbolikus linket
RUN apt-get update && \
    apt-get install -y ffmpeg nodejs && \
    ln -s /usr/bin/nodejs /usr/bin/node && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --upgrade yt-dlp

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app", "--timeout", "120"]
