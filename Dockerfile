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

# Make startup script executable
RUN chmod +x start_wsgi.sh

# Expose port
EXPOSE 5000

# Set environment variables
ENV PORT=5000
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV RAILWAY_ENVIRONMENT=production

# Run the application with WSGI server
CMD ["./start_wsgi.sh"]
