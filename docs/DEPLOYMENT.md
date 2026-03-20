# 🚀 Deployment Guide

Complete guide for deploying the AI-Powered Customer Support Insight Platform to various environments.

## Prerequisites

- Git repository with code
- OpenAI API key
- Docker installed (for containerized deployments)

## Option 1: Fly.io (Recommended - Free Tier Available)

### Setup

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login
```

### Deploy

```bash
# Initialize (first time only)
flyctl launch

# Follow prompts:
# - App name: support-insight-platform
# - Region: Choose closest to you
# - PostgreSQL: No (we use SQLite)
# - Redis: No

# Set secrets
flyctl secrets set OPENAI_API_KEY=sk-your-key-here

# Deploy
flyctl deploy

# Open in browser
flyctl open
```

### Update

```bash
# After code changes
flyctl deploy
```

### Monitor

```bash
# View logs
flyctl logs

# Check status
flyctl status

# SSH into container
flyctl ssh console
```

## Option 2: Railway (Easiest - One-Click Deploy)

### Setup

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository

### Configure

1. Add environment variable:
   - Key: `OPENAI_API_KEY`
   - Value: `sk-your-key-here`

2. Railway auto-detects Dockerfile and deploys

3. Get public URL from dashboard

### Update

- Push to GitHub → Railway auto-deploys

## Option 3: Render (Free Tier Available)

### Setup

1. Go to [render.com](https://render.com)
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository

### Configure

- **Name**: support-insight-platform
- **Environment**: Docker
- **Plan**: Free
- **Environment Variables**:
  - `OPENAI_API_KEY`: sk-your-key-here

### Deploy

- Click "Create Web Service"
- Render builds and deploys automatically

## Option 4: AWS (Production-Grade)

### Using ECS Fargate

```bash
# 1. Build and push Docker image
aws ecr create-repository --repository-name support-insight-platform
docker build -t support-insight-platform .
docker tag support-insight-platform:latest <account-id>.dkr.ecr.<region>.amazonaws.com/support-insight-platform:latest
aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/support-insight-platform:latest

# 2. Create ECS cluster
aws ecs create-cluster --cluster-name support-platform-cluster

# 3. Create task definition (see task-definition.json below)
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 4. Create service
aws ecs create-service \
  --cluster support-platform-cluster \
  --service-name support-platform-service \
  --task-definition support-platform-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

**task-definition.json**:
```json
{
  "family": "support-platform-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "support-platform",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/support-insight-platform:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "sk-your-key-here"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/support-platform",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

## Option 5: Google Cloud Run

```bash
# 1. Enable Cloud Run API
gcloud services enable run.googleapis.com

# 2. Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/support-insight-platform

# 3. Deploy
gcloud run deploy support-insight-platform \
  --image gcr.io/PROJECT_ID/support-insight-platform \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=sk-your-key-here

# 4. Get URL
gcloud run services describe support-insight-platform --region us-central1 --format 'value(status.url)'
```

## Option 6: Azure Container Instances

```bash
# 1. Create resource group
az group create --name support-platform-rg --location eastus

# 2. Create container registry
az acr create --resource-group support-platform-rg --name supportplatformacr --sku Basic

# 3. Build and push
az acr build --registry supportplatformacr --image support-insight-platform:latest .

# 4. Deploy
az container create \
  --resource-group support-platform-rg \
  --name support-platform \
  --image supportplatformacr.azurecr.io/support-insight-platform:latest \
  --dns-name-label support-platform-unique \
  --ports 8501 \
  --environment-variables OPENAI_API_KEY=sk-your-key-here

# 5. Get URL
az container show --resource-group support-platform-rg --name support-platform --query ipAddress.fqdn
```

## Option 7: DigitalOcean App Platform

### Setup

1. Go to [cloud.digitalocean.com](https://cloud.digitalocean.com)
2. Click "Create" → "Apps"
3. Connect GitHub repository

### Configure

- **Resource Type**: Docker
- **HTTP Port**: 8501
- **Environment Variables**:
  - `OPENAI_API_KEY`: sk-your-key-here
- **Plan**: Basic ($5/month)

### Deploy

- Click "Create Resources"
- DigitalOcean builds and deploys

## Option 8: Heroku

```bash
# 1. Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# 2. Login
heroku login

# 3. Create app
heroku create support-insight-platform

# 4. Set buildpack
heroku stack:set container

# 5. Set environment variables
heroku config:set OPENAI_API_KEY=sk-your-key-here

# 6. Deploy
git push heroku main

# 7. Open
heroku open
```

## Option 9: Local Production (Docker)

```bash
# Build
docker build -t support-insight-platform .

# Run
docker run -d \
  -p 8501:8501 \
  -e OPENAI_API_KEY=sk-your-key-here \
  -v $(pwd)/data:/app/data \
  --name support-platform \
  support-insight-platform

# Access at http://localhost:8501
```

## Option 10: Kubernetes

**deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: support-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: support-platform
  template:
    metadata:
      labels:
        app: support-platform
    spec:
      containers:
      - name: support-platform
        image: your-registry/support-insight-platform:latest
        ports:
        - containerPort: 8501
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: support-platform-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8501
  selector:
    app: support-platform
```

Deploy:
```bash
# Create secret
kubectl create secret generic openai-secret --from-literal=api-key=sk-your-key-here

# Deploy
kubectl apply -f deployment.yaml

# Get external IP
kubectl get service support-platform-service
```

## Environment Variables

All deployments require:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |

Optional:
| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8501` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Health Checks

All platforms should configure:

- **Health Check Path**: `/_stcore/health`
- **Port**: `8501`
- **Interval**: `30s`
- **Timeout**: `10s`
- **Retries**: `3`

## Monitoring

### Application Logs

```bash
# Fly.io
flyctl logs

# Railway
railway logs

# Render
(View in dashboard)

# AWS
aws logs tail /ecs/support-platform --follow

# GCP
gcloud logging read "resource.type=cloud_run_revision"

# Azure
az container logs --resource-group support-platform-rg --name support-platform --follow
```

### Metrics

Set up monitoring for:
- Request count
- Response time
- Error rate
- API call volume
- Database size

## Scaling

### Horizontal Scaling

**Fly.io**:
```bash
flyctl scale count 3
```

**Railway**: Auto-scales based on load

**AWS ECS**:
```bash
aws ecs update-service --cluster support-platform-cluster --service support-platform-service --desired-count 3
```

**Kubernetes**:
```bash
kubectl scale deployment support-platform --replicas=3
```

### Vertical Scaling

**Fly.io**:
```bash
flyctl scale vm shared-cpu-2x --memory 1024
```

**Railway**: Adjust in dashboard

**AWS ECS**: Update task definition CPU/memory

## Cost Estimates

| Platform | Free Tier | Paid (Basic) | Notes |
|----------|-----------|--------------|-------|
| **Fly.io** | 3 VMs (256MB) | $5-10/month | Best value |
| **Railway** | $5 credit/month | $10-20/month | Easiest setup |
| **Render** | 750 hours/month | $7/month | Good free tier |
| **Heroku** | None | $7/month | Simple but pricey |
| **AWS** | 12 months free | $15-30/month | Most flexible |
| **GCP** | $300 credit | $10-25/month | Good for scale |
| **Azure** | $200 credit | $15-30/month | Enterprise-ready |
| **DigitalOcean** | None | $5-12/month | Predictable pricing |

**Plus OpenAI API costs**: ~$50/month for 10K tickets/day

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs <container-id>

# Verify environment variables
docker exec <container-id> env | grep OPENAI

# Test locally
docker run -it --entrypoint /bin/bash support-insight-platform
```

### Out of memory

Increase memory allocation:
- Fly.io: `flyctl scale memory 1024`
- Docker: `docker run -m 1g ...`
- Kubernetes: Update `resources.limits.memory`

### API rate limits

- Reduce batch size in `pipeline.py`
- Add delays between API calls
- Upgrade OpenAI tier

### Database locked

- Use PostgreSQL instead of SQLite for production
- Enable WAL mode: `PRAGMA journal_mode=WAL;`

## Security Checklist

- [ ] API keys in environment variables (not code)
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Input validation enabled
- [ ] Database backups scheduled
- [ ] Logs monitored
- [ ] Security updates automated

## Backup & Recovery

### Database Backup

```bash
# SQLite
docker exec support-platform sqlite3 /app/support_platform.db ".backup /app/backup.db"
docker cp support-platform:/app/backup.db ./backup.db

# Schedule with cron
0 2 * * * docker exec support-platform sqlite3 /app/support_platform.db ".backup /app/backup-$(date +\%Y\%m\%d).db"
```

### Restore

```bash
docker cp backup.db support-platform:/app/support_platform.db
docker restart support-platform
```

## CI/CD Integration

GitHub Actions workflow is included in `.github/workflows/ci.yml`

Customize deployment step for your platform:

```yaml
- name: Deploy to Fly.io
  run: flyctl deploy --remote-only
  env:
    FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

## Next Steps

1. Choose deployment platform
2. Set up monitoring
3. Configure backups
4. Test with real data
5. Monitor costs
6. Scale as needed

---

**Need help?** Open an issue on GitHub or check the documentation.
