FROM quay.io/waynesun09/uvicorn-gunicorn:python3.8

LABEL maintainer="Wayne Sun <gsun@redhat.com>"

ENV PIPENV_VENV_IN_PROJECT 1
WORKDIR /
COPY start.sh Pipfile Pipfile.lock .
RUN chmod +x /start.sh

RUN pip install pip pipenv && \
    pipenv install --deploy --ignore-pipfile

COPY ./app /app
EXPOSE 80
EXPOSE 443
CMD ["/start.sh"]
