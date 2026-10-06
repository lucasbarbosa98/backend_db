FROM python:3.11.4-bullseye

ENV PYTHONDONTWRITEBYTECODE 1

RUN apt update && apt install -y git curl && apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt