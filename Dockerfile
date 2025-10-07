# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine

WORKDIR /

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install the requirements
COPY requirements.txt /
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .

EXPOSE 5000/tcp

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
