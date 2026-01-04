# Use official lightweight Python image
FROM python:3.12-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (needed for MySQL + cryptography)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first (better Docker caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the entire project
COPY . .

# Expose port used by Azure App Service
EXPOSE 8000

# Environment variables expected by Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Start the application using gunicorn (recommended for production)
CMD ["gunicorn", "-b", "0.0.0.0:8000", "run:app"]
