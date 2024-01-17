# Base builder image
FROM python:3.12-alpine

# Configure environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Set working directory
WORKDIR /app

# Create media directory if it doesn't exist
RUN mkdir -p /app/school_event_management_system/media

# Copy requirements files
COPY requirements/requirements.txt requirements.txt
COPY requirements/requirements.lint.txt requirements.lint.txt

# Install project dependencies
RUN pip install --upgrade pip-tools
RUN pip-sync requirements.txt requirements.*.txt

# Copy project files
COPY . .

ENTRYPOINT ["sh", "/app/configuration/docker/entrypoint.sh"]
