# Base builder image
FROM python:3.12-alpine as builder

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
RUN pip install -r requirements.txt

# Base image
FROM python:3.12-alpine

# Configure environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Copy project dependencies
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy project files
COPY . .
