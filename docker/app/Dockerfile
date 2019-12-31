# Use an official Python runtime as a parent image
FROM python:3.7.5-alpine3.10

# Set the working directory to /application
WORKDIR /application

# Copy the current directory contents into the container at /application
ADD . /application

# Install uWSGI dependencies, all python requirements, and then clean up
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
    pip install uWSGI==2.0.18; \
    apk del .build-deps;

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the application on port 5000
CMD ["sh", "run.sh"]
