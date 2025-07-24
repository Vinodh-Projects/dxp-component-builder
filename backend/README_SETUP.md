# Development Setup Instructions

## Option 1: Run with Docker (Recommended for Production)
1. Start Docker Desktop
2. Run: `docker-compose up -d`
3. Access your app at: http://localhost

## Option 2: Run locally (Development)
1. Start Redis (install Redis locally or use cloud Redis)
2. Activate virtual environment: `.\venv\Scripts\Activate.ps1`
3. Run the app: `python main.py`
4. Access your app at: http://localhost:8000

## Environment Variables Required
- OPENAI_API_KEY (required)
- ANTHROPIC_API_KEY (optional)
- REDIS_URL (default: redis://localhost:6379)

## Docker Services
- **app**: FastAPI application (port 8000)
- **redis**: Redis cache (port 6379)  
- **nginx**: Reverse proxy (port 80)


Here are example curl commands for the /generate-form endpoint with different request inputs:

1. Basic Component Generation (no image, default options)
```bash
curl -X POST http://localhost:8000/api/v1/components/generate-form ^
  -F "request={\"description\":\"Button component\",\"component_type\":\"button\",\"fields\":[{\"name\":\"label\",\"type\":\"string\"}]}"
```


2. With Image Upload
```bash
curl -X POST http://localhost:8000/api/v1/components/generate-form ^
  -F "request={\"description\":\"Image banner\",\"component_type\":\"banner\",\"fields\":[{\"name\":\"imageUrl\",\"type\":\"string\"}]}" ^
  -F "image=@banner.png"
```

3. With Custom Generation Options

```bash
curl -X POST http://localhost:8000/api/v1/components/generate-form ^
  -F "request={\"description\":\"Card component\",\"component_type\":\"card\",\"fields\":[{\"name\":\"title\",\"type\":\"string\"}]}" ^
  -F "options={\"validate\":false,\"someOtherOption\":true}"
```

4. With Image and Options
```bash
curl -X POST http://localhost:8000/api/v1/components/generate-form ^
  -F "request={\"description\":\"Profile component\",\"component_type\":\"profile\",\"fields\":[{\"name\":\"avatar\",\"type\":\"string\"}]}" ^
  -F "image=@profile.jpg" ^
  -F "options={\"validate\":true,\"maxTokens\":2000}"
```
