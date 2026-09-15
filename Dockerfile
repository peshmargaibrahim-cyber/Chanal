FROM python:3.9-slim

# دامەزراندنی FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# کردنەوەی پۆرت بۆ Render
EXPOSE 10000

CMD ["python", "app.py"]
