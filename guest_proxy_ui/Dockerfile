# syntax=docker/dockerfile:1
FROM python:3.11-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir flask requests

COPY . .

EXPOSE 8080

CMD [ "python3", "-u", "./app.py" ]