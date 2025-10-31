# Use official Python image
FROM python:3.9-alpine3.13

# Set maintainer info
LABEL maintainer="londonappdev.com"

# Prevent Python from buffering stdout/stderr (ensures logs appear immediately)
ENV PYTHONUNBUFFERED 1

# Copy requirements file into temp directory
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Copy app source directory into container
COPY ./app /app

# Set working directory inside container
WORKDIR /app

# Expose Django dev server port
EXPOSE 8000

ARG DEV=false

# Install dependencies
RUN python -m venv /py && \
  /py/bin/pip install --upgrade pip && \
  # Install PostgreSQL client (needed at runtime)
  apk add --update --no-cache postgresql-client && \
  # Install temporary build dependencies
  apk add --update --no-cache --virtual .tmp-build-deps \
  build-base postgresql-dev musl-dev && \
  /py/bin/pip install -r /tmp/requirements.txt && \
  if [ $DEV = "true" ]; \
  then /py/bin/pip install -r /tmp/requirements.dev.txt; \
  fi && \
  rm -rf /tmp && \
  apk del .tmp-build-deps && \
  adduser \
  --disabled-password \
  --no-create-home \
  django-user

# Set PATH so we don’t need to type /py/bin every time
ENV PATH="/py/bin:$PATH"

# Switch to non-root user
USER django-user
