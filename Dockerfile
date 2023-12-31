# syntax=docker/dockerfile:1
FROM python:3.9-alpine3.15

WORKDIR /code
COPY requirements.txt .
COPY bot/ .
RUN pip install --disable-pip-version-check -q -r requirements.txt
ENTRYPOINT [ "python", "maincode.py" ]