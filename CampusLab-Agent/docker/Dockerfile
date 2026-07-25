# Dockerfile for CampusLab Agent
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt .

# Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose Flask Port
EXPOSE 5000

# Environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Command to launch server with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:create_app()"]
