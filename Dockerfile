# Base builder image
FROM python:3.12-alpine

# Configure environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Set working directory
WORKDIR /app

# Copy requirements files
COPY ./requirements.txt /app/requirements.txt

# Install project dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .
