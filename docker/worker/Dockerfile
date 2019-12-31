# Use an official Python runtime as a parent image
FROM python:3.7.5-alpine3.10

# Set the working directory to /application
WORKDIR /application

# Copy the current directory contents into the container at /application
ADD . /application

# Install all python requirements and then clean up
RUN set -e; \
    apk add --no-cache --virtual .build-deps \
    gcc \
    libc-dev \
    libffi \
    libffi-dev \
    linux-headers \
    libressl-dev \
    ; \
    pip install -r requirements.txt; \
    apk del .build-deps;

# Run the Celery worker
CMD ["celery", "-A", "run.celery", "worker"]
