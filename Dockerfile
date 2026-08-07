FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .
COPY images/ ./images/
COPY evening-poster/content.json ./evening-poster/content.json

CMD ["python3", "bot.py"]
