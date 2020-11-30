FROM tiangolo/uvicorn-gunicorn:python3.8

LABEL maintainer="Wayne Sun <gsun@redhat.com>"

RUN pip install --no-cache-dir fastapi

COPY ./notify-service/app /app
