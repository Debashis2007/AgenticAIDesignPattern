# Deployment Guide

## Local Deployment with Docker

### Prerequisites
- Docker and Docker Compose installed
- 10GB disk space (for Ollama model)

### Quick Start

```bash
# Clone repository
git clone https://github.com/Debashis2007/ImmigrationChatbot.git
cd ImmigrationChatbot

# Start all services
docker-compose up -d

# Wait for services to be healthy (1-2 minutes for Ollama to download model)
docker-compose ps

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Health check: http://localhost:8000/health
```

### Docker Compose Services

- **ollama**: LLM backend (llama3.1:8b)
- **backend**: FastAPI server (port 8000)
- **frontend**: Next.js UI (port 3000)

### Stop Services

```bash
docker-compose down

# Remove volumes (and data)
docker-compose down -v
```

---

## Cloud Deployment Options

### 1. Railway.app (Recommended for Quick Start)

#### Prerequisites
- Railway account (free tier available)
- GitHub repository

#### Steps

1. **Create Railway Project**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub"
   - Connect your GitHub account and select this repo

2. **Configure Variables**
   ```
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://ollama:11434/v1
   OLLAMA_MODEL=llama3.1:8b
   LLM_TIMEOUT_SECONDS=30
   DATABASE_URL=sqlite:///./chatbot.db
   ```

3. **Deploy Services**
   - Add Ollama service (custom Docker image)
   - Add Backend service (from Dockerfile.backend)
   - Add Frontend service (from Dockerfile.frontend)

4. **Link Services**
   - Set environment variables to point services to each other

---

### 2. Heroku

#### Prerequisites
- Heroku CLI
- Heroku account

#### Deploy Backend

```bash
# Create app
heroku create immigration-chatbot-api

# Set environment variables
heroku config:set LLM_PROVIDER=ollama
heroku config:set OLLAMA_BASE_URL=http://ollama:11434/v1
heroku config:set OLLAMA_MODEL=llama3.1:8b
heroku config:set LLM_TIMEOUT_SECONDS=30

# Deploy
git push heroku main:main
```

#### Deploy Frontend

```bash
# Create frontend app
heroku create immigration-chatbot-web

# Set API URL
heroku config:set NEXT_PUBLIC_API_BASE_URL=https://immigration-chatbot-api.herokuapp.com

# Add buildpack for Node.js
heroku buildpacks:add heroku/nodejs

# Deploy
git push heroku main:main
```

---

### 3. AWS Deployment

#### Option A: ECS with Docker Compose

```bash
# Install ECS CLI
curl -o /usr/local/bin/ecs-cli https://amazon-ecs-cli.s3.amazonaws.com/ecs-cli-darwin-amd64-latest

# Create cluster
ecs-cli up

# Deploy
ecs-cli compose -f docker-compose.yml up
```

#### Option B: EC2 Instance

```bash
# SSH into EC2 instance
ssh -i your-key.pem ec2-user@your-instance

# Install Docker
sudo yum update
sudo yum install docker
sudo usermod -a -G docker ec2-user

# Clone and run
git clone https://github.com/Debashis2007/ImmigrationChatbot.git
cd ImmigrationChatbot
docker-compose up -d
```

---

### 4. Google Cloud Run

#### Deploy Backend

```bash
# Authenticate
gcloud auth login

# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/immigration-backend --file Dockerfile.backend

# Deploy
gcloud run deploy immigration-backend \
  --image gcr.io/PROJECT_ID/immigration-backend \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 300
```

#### Deploy Frontend

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/immigration-frontend --file Dockerfile.frontend

# Deploy
gcloud run deploy immigration-frontend \
  --image gcr.io/PROJECT_ID/immigration-frontend \
  --platform managed \
  --region us-central1 \
  --set-env-vars NEXT_PUBLIC_API_BASE_URL=https://immigration-backend-xxx.run.app
```

---

### 5. DigitalOcean App Platform

1. **Connect GitHub**
   - Go to DigitalOcean App Platform
   - Create new app
   - Select repository

2. **Configure Services**
   - Backend: Dockerfile.backend, 8000
   - Frontend: Dockerfile.frontend, 3000
   - Ollama: Custom Docker container

3. **Set Environment Variables**
   - `LLM_PROVIDER=ollama`
   - `NEXT_PUBLIC_API_BASE_URL=<backend-url>`

4. **Deploy**
   - Click "Deploy"

---

## Environment Variables Reference

### Backend (.env)

```bash
# LLM Configuration
LLM_ENABLED=true
LLM_PROVIDER=ollama                    # openai or ollama
LLM_TIMEOUT_SECONDS=30

# Ollama Settings
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.1:8b
OLLAMA_API_KEY=ollama

# OpenAI Settings (alternative)
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini

# Database
MEMORY_BACKEND=sql
DATABASE_URL=sqlite:///./chatbot.db

# API Auth
API_AUTH_ENABLED=false
API_AUTH_KEY=your_secure_key
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=
```

---

## Monitoring & Logging

### Docker Logs

```bash
# Backend logs
docker logs immigration-backend -f

# Frontend logs
docker logs immigration-frontend -f

# Ollama logs
docker logs immigration-ollama -f
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Ollama health
curl http://localhost:11434/api/tags
```

---

## Performance Tips

1. **Increase Timeout**: Set `LLM_TIMEOUT_SECONDS=60` for slower connections
2. **Database**: Use PostgreSQL in production instead of SQLite
3. **Caching**: Add Redis for session caching
4. **CDN**: Use CloudFront/CloudFlare for frontend static assets
5. **Load Balancing**: Deploy multiple backend instances behind a load balancer

---

## Troubleshooting

### Ollama Model Not Loading

```bash
# Pull model manually
docker exec immigration-ollama ollama pull llama3.1:8b
```

### Backend Connection Issues

```bash
# Check network
docker network ls
docker inspect immigration_chatbot_default

# Verify backend is running
curl http://localhost:8000/health
```

### Frontend Can't Connect to Backend

- Check `NEXT_PUBLIC_API_BASE_URL` environment variable
- Ensure CORS is enabled on backend (it is by default)
- Check browser console for specific error

---

## Production Checklist

- [ ] Use PostgreSQL for database (not SQLite)
- [ ] Enable API authentication (`API_AUTH_ENABLED=true`)
- [ ] Set strong `API_AUTH_KEY`
- [ ] Use environment-specific `.env` files
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring and alerts
- [ ] Configure automatic backups
- [ ] Use production-grade LLM (consider OpenAI for reliability)
- [ ] Add rate limiting
- [ ] Enable logging to external service (e.g., CloudWatch, Datadog)
