# GAIC Detector - Quick Deployment Guide

## Prerequisites

- Linux/MacOS/Windows with WSL
- Python 3.8+
- 4GB+ RAM
- Optional: CUDA GPU for faster inference

## Installation (5 minutes)

### 1. Clone & Setup

```bash
git clone https://github.com/thedannyliu/GAIC-Detector-Web-GUI.git
cd GAIC-Detector-Web-GUI
./setup.sh
```

### 2. Configure (Optional)

```bash
# Edit environment file
nano .env

# Key settings:
# - LLM_ENABLED=true (if using OpenAI)
# - OPENAI_API_KEY=your_key
```

### 3. Get Models (Optional)

**Option A: Use mock models** (immediate)
- No action needed
- System auto-detects missing weights
- Good for testing UI/UX

**Option B: Download real models**
```bash
./download_models.sh  # Update URLs first
```

**Option C: Manual download**
```bash
# Place .pth files in models/weights/
# - susy.pth
# - fatformer.pth
# - distildire.pth
```

### 4. Launch

```bash
./start.sh
```

Visit: http://localhost:7860

## Docker Deployment (Alternative)

```bash
# Build image
docker build -t gaic-detector .

# Run container
docker run -p 8000:8000 -p 7860:7860 gaic-detector
```

## Production Deployment

### Using systemd

1. Create service file:
```bash
sudo nano /etc/systemd/system/gaic-backend.service
```

```ini
[Unit]
Description=GAIC Detector Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/gaic-detector
Environment="PATH=/opt/gaic-detector/venv/bin"
ExecStart=/opt/gaic-detector/venv/bin/python -m app.main
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Enable and start:
```bash
sudo systemctl enable gaic-backend
sudo systemctl start gaic-backend
```

### Using nginx reverse proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 10M;
    }
}
```

## Cloud Deployment

### AWS EC2
```bash
# t2.large or better recommended
# Open ports 8000, 7860 in security group
# Follow standard installation steps
```

### Google Cloud Run
```bash
gcloud run deploy gaic-detector \
  --source . \
  --port 7860 \
  --memory 4Gi
```

### Heroku
```bash
heroku create gaic-detector
git push heroku main
```

## Troubleshooting

### Port already in use
```bash
# Kill existing processes
lsof -ti:8000 | xargs kill -9
lsof -ti:7860 | xargs kill -9
```

### Import errors
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Out of memory
```bash
# Reduce max image size in .env
MAX_LONG_SIDE=1024
```

### Slow inference
- Enable GPU if available
- Use degraded stride mode
- Reduce image resolution

## Monitoring

### Logs
```bash
# Backend logs
tail -f logs/backend.log

# Frontend access
tail -f logs/gradio.log
```

### Health checks
```bash
# API health
curl http://localhost:8000/

# Test inference
python test_api.py test_image.jpg
```

## Security Checklist

- [ ] Change default ports in production
- [ ] Enable HTTPS (Let's Encrypt)
- [ ] Set up firewall rules
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Monitor access logs

## Performance Tuning

### Backend
```python
# In app/config.py
WORKERS = 4  # CPU cores
MAX_QUEUE = 100
```

### Frontend
```python
# In gradio_app.py
demo.queue(concurrency_count=10)
```

## Backup & Recovery

```bash
# Backup models
tar -czf models-backup.tar.gz models/weights/

# Backup configuration
cp .env .env.backup
```

## Updates

```bash
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
./start.sh
```

## Support

- GitHub Issues: https://github.com/thedannyliu/GAIC-Detector-Web-GUI/issues
- Documentation: /docs/
- Email: support@example.com
