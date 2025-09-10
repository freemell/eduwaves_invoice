# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p templates static

# Expose port
EXPOSE 5000

# Set environment variables
ENV PORT=5000
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py

# Run the application with gunicorn using WSGI file
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:application"]
