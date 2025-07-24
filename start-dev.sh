#!/bin/bash
# Start all services in development mode

echo "🚀 Starting DXP Component Builder in Development Mode..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env file with your API keys before running again."
    exit 1
fi

# Start services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

echo "🎉 Services started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "🗄️  Redis: localhost:6379"
