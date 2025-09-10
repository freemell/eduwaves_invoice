#!/bin/bash

# Startup script to ensure WSGI server is used in production
echo "🚀 Starting EDUwaves Invoice Generator with WSGI Server"
echo "📋 Environment: $RAILWAY_ENVIRONMENT"
echo "🔧 Port: $PORT"

# Check if we're in production (Railway)
if [ "$RAILWAY_ENVIRONMENT" = "production" ] || [ -n "$PORT" ]; then
    echo "✅ Production environment detected - Using Gunicorn WSGI server"
    echo "🌐 Starting Gunicorn on port $PORT"
    exec gunicorn --config gunicorn.conf.py wsgi:application
else
    echo "⚠️  Development environment - Using Flask dev server"
    echo "🌐 Starting Flask dev server on port 5000"
    exec python3 app.py
fi
