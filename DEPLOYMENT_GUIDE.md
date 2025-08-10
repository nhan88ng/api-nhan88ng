# 🚀 Deployment Guide - API Nhan88ng

**Complete production deployment guide for the Nhan88ng e-commerce platform**

---

## 📋 **Table of Contents**

1. [Pre-Deployment Checklist](#-pre-deployment-checklist)
2. [Environment Setup](#-environment-setup)
3. [Docker Deployment](#-docker-deployment)
4. [Traditional Deployment](#-traditional-deployment)
5. [Cloud Deployment](#-cloud-deployment)
6. [Database Setup](#-database-setup)
7. [Security Configuration](#-security-configuration)
8. [Performance Optimization](#-performance-optimization)
9. [Monitoring & Logging](#-monitoring--logging)
10. [Backup & Recovery](#-backup--recovery)
11. [CI/CD Pipeline](#-cicd-pipeline)
12. [Troubleshooting](#-troubleshooting)

---

## ✅ **Pre-Deployment Checklist**

### **System Requirements**
- [ ] **Server**: 2+ CPU cores, 4GB+ RAM, 20GB+ storage
- [ ] **Python**: Version 3.9+ installed
- [ ] **MongoDB**: Version 5.0+ running and accessible
- [ ] **SSL Certificate**: Valid certificate for HTTPS
- [ ] **Domain**: Configured domain with DNS pointing to server
- [ ] **Firewall**: Ports 80, 443, and MongoDB port configured

### **Code Preparation**
- [ ] All tests passing (90.9%+ success rate)
- [ ] Admin user properly configured
- [ ] Environment variables configured
- [ ] Static files and uploads directory structure created
- [ ] Database indexes created
- [ ] Security headers configured
- [ ] API documentation up to date

### **Environment Files**
Create the following files before deployment:

**`.env.production`**
```bash
# Application Configuration
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-super-secure-secret-key-here-32-characters-minimum
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
MONGODB_URL=mongodb://username:password@localhost:27017/nhan88ng_production
DATABASE_NAME=nhan88ng_production

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-for-production-use
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload Configuration
UPLOAD_DIR=/var/www/api-nhan88ng/uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp

# Email Configuration (if used)
SMTP_HOST=smtp.yourmailserver.com
SMTP_PORT=587
SMTP_USER=your-email@yourdomain.com
SMTP_PASSWORD=your-email-password
EMAIL_FROM=noreply@yourdomain.com

# Security Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_CREDENTIALS=true
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=*

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/api-nhan88ng/app.log
```

---

## 🌍 **Environment Setup**

### **1. Server Preparation**

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx supervisor mongodb-tools curl git

# Create application user
sudo useradd -m -s /bin/bash api-nhan88ng
sudo usermod -aG sudo api-nhan88ng

# Create application directories
sudo mkdir -p /var/www/api-nhan88ng
sudo mkdir -p /var/log/api-nhan88ng
sudo mkdir -p /etc/api-nhan88ng

# Set permissions
sudo chown -R api-nhan88ng:api-nhan88ng /var/www/api-nhan88ng
sudo chown -R api-nhan88ng:api-nhan88ng /var/log/api-nhan88ng
```

### **2. Application Deployment**

```bash
# Switch to application user
sudo su - api-nhan88ng

# Clone repository
cd /var/www/api-nhan88ng
git clone https://github.com/yourusername/api-nhan88ng.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.production .env

# Create uploads directory structure
mkdir -p uploads/tinashop/{products,categories,users}/thumbnails
mkdir -p uploads/micocah/{products,categories,users}/thumbnails
mkdir -p uploads/shared/{products,categories,users}/thumbnails

# Set permissions
chmod -R 755 uploads/
```

### **3. Database Initialization**

```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/nhan88ng_production

# Create indexes for better performance
use nhan88ng_production

# Product indexes
db.products.createIndex({ "shop": 1, "status": 1 })
db.products.createIndex({ "shop": 1, "category_ids": 1 })
db.products.createIndex({ "shop": 1, "price": 1 })
db.products.createIndex({ "shop": 1, "created_at": -1 })
db.products.createIndex({ "slug": 1, "shop": 1 }, { unique: true })
db.products.createIndex({ "name": "text", "description": "text" })

# Category indexes
db.categories.createIndex({ "shop": 1, "is_active": 1 })
db.categories.createIndex({ "shop": 1, "parent_id": 1 })
db.categories.createIndex({ "slug": 1, "shop": 1 }, { unique: true })

# User indexes
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "shop": 1, "role": 1 })
db.users.createIndex({ "is_active": 1 })

# Create admin user
db.users.insertOne({
  "email": "admin@yourdomain.com",
  "hashed_password": "$2b$12$hashed_password_here",
  "full_name": "System Administrator",
  "shop": "tinashop",
  "role": "admin",
  "permissions": [
    "user:read", "user:write", "product:read", "product:write", 
    "product:delete", "order:read", "order:write", "order:delete", 
    "admin:panel"
  ],
  "is_active": true,
  "is_verified": true,
  "created_at": new Date(),
  "updated_at": new Date()
})

exit
```

---

## 🐳 **Docker Deployment**

### **1. Production Dockerfile**

```dockerfile
# Dockerfile.production
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN groupadd -r api && useradd -r -g api api

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads/tinashop/{products,categories,users}/thumbnails \
    && mkdir -p uploads/micocah/{products,categories,users}/thumbnails \
    && mkdir -p uploads/shared/{products,categories,users}/thumbnails \
    && mkdir -p logs

# Set permissions
RUN chown -R api:api /app
USER api

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### **2. Docker Compose Production**

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  mongodb:
    image: mongo:6.0
    container_name: nhan88ng_mongodb
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: your-secure-password
      MONGO_INITDB_DATABASE: nhan88ng_production
    volumes:
      - mongodb_data:/data/db
      - ./mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
    ports:
      - "27017:27017"
    networks:
      - nhan88ng_network

  api:
    build:
      context: .
      dockerfile: Dockerfile.production
    container_name: nhan88ng_api
    restart: unless-stopped
    depends_on:
      - mongodb
    environment:
      - MONGODB_URL=mongodb://admin:your-secure-password@mongodb:27017/nhan88ng_production?authSource=admin
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    ports:
      - "8000:8000"
    networks:
      - nhan88ng_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: nhan88ng_nginx
    restart: unless-stopped
    depends_on:
      - api
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./uploads:/var/www/uploads
    networks:
      - nhan88ng_network

volumes:
  mongodb_data:

networks:
  nhan88ng_network:
    driver: bridge
```

### **3. MongoDB Initialization Script**

```javascript
// mongo-init.js
db = db.getSiblingDB('nhan88ng_production');

// Create application user
db.createUser({
  user: 'api_user',
  pwd: 'your-api-user-password',
  roles: [
    {
      role: 'readWrite',
      db: 'nhan88ng_production'
    }
  ]
});

// Create indexes
db.products.createIndex({ "shop": 1, "status": 1 });
db.products.createIndex({ "shop": 1, "category_ids": 1 });
db.products.createIndex({ "shop": 1, "price": 1 });
db.products.createIndex({ "slug": 1, "shop": 1 }, { unique: true });
db.products.createIndex({ "name": "text", "description": "text" });

db.categories.createIndex({ "shop": 1, "is_active": 1 });
db.categories.createIndex({ "slug": 1, "shop": 1 }, { unique: true });

db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "shop": 1, "role": 1 });
```

### **4. Nginx Configuration**

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=5r/s;

    # Upstream for API
    upstream api_backend {
        server api:8000;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/certificate.crt;
        ssl_certificate_key /etc/nginx/ssl/private.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Client max body size for file uploads
        client_max_body_size 10M;

        # Static files
        location /static/ {
            alias /var/www/uploads/;
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # Upload endpoints with stricter rate limiting
        location /api/v1/upload/ {
            limit_req zone=upload burst=5 nodelay;
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check
        location /health {
            proxy_pass http://api_backend;
            access_log off;
        }

        # Documentation
        location /docs {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Default location
        location / {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### **5. Docker Deployment Commands**

```bash
# Build and start all services
docker-compose -f docker-compose.production.yml up -d --build

# Check service status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f api

# Update application
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d --build

# Backup database
docker exec nhan88ng_mongodb mongodump --db nhan88ng_production --out /data/backup

# Restore database
docker exec nhan88ng_mongodb mongorestore /data/backup/nhan88ng_production
```

---

## 🖥️ **Traditional Deployment**

### **1. Systemd Service Configuration**

```ini
# /etc/systemd/system/api-nhan88ng.service
[Unit]
Description=API Nhan88ng FastAPI application
After=network.target mongodb.service
Requires=mongodb.service

[Service]
Type=exec
User=api-nhan88ng
Group=api-nhan88ng
WorkingDirectory=/var/www/api-nhan88ng
Environment=PATH=/var/www/api-nhan88ng/venv/bin
Environment=ENVIRONMENT=production
EnvironmentFile=/var/www/api-nhan88ng/.env
ExecStart=/var/www/api-nhan88ng/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/www/api-nhan88ng/uploads
ReadWritePaths=/var/log/api-nhan88ng

[Install]
WantedBy=multi-user.target
```

### **2. Service Management**

```bash
# Enable and start service
sudo systemctl enable api-nhan88ng
sudo systemctl start api-nhan88ng

# Check status
sudo systemctl status api-nhan88ng

# View logs
sudo journalctl -u api-nhan88ng -f

# Restart service
sudo systemctl restart api-nhan88ng

# Stop service
sudo systemctl stop api-nhan88ng
```

### **3. Nginx Configuration for Traditional Deployment**

```bash
# Create Nginx site configuration
sudo nano /etc/nginx/sites-available/api-nhan88ng

# Link to sites-enabled
sudo ln -s /etc/nginx/sites-available/api-nhan88ng /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## ☁️ **Cloud Deployment**

### **1. AWS EC2 Deployment**

```bash
# EC2 instance setup script
#!/bin/bash

# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/yourusername/api-nhan88ng.git
cd api-nhan88ng

# Set up environment
cp .env.production .env

# Start services
docker-compose -f docker-compose.production.yml up -d
```

### **2. AWS RDS MongoDB**

```bash
# Connect to MongoDB Atlas or AWS DocumentDB
MONGODB_URL="mongodb://username:password@docdb-cluster.cluster-xyz.us-east-1.docdb.amazonaws.com:27017/nhan88ng_production?ssl=true&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
```

### **3. AWS S3 for File Storage**

```python
# app/core/storage.py
import boto3
from botocore.exceptions import ClientError
import os

class S3Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET')

    async def upload_file(self, file_path: str, key: str):
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, key)
            return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
        except ClientError as e:
            return None

    async def delete_file(self, key: str):
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            return False
```

### **4. Digital Ocean App Platform**

```yaml
# .do/app.yaml
name: api-nhan88ng
services:
- name: api
  source_dir: /
  github:
    repo: yourusername/api-nhan88ng
    branch: main
  run_command: uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
  environment_slug: python
  instance_count: 2
  instance_size_slug: basic-s
  http_port: 8080
  health_check:
    http_path: /health
  envs:
  - key: ENVIRONMENT
    value: production
  - key: MONGODB_URL
    value: ${db.CONNECTION_STRING}
  - key: SECRET_KEY
    value: ${SECRET_KEY}

databases:
- name: mongodb
  engine: MONGODB
  version: "5"
```

---

## 🔒 **Security Configuration**

### **1. SSL Certificate Setup**

```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Set up auto-renewal cron job
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### **2. Firewall Configuration**

```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow from your.trusted.ip.address to any port 27017
sudo ufw status
```

### **3. Security Headers**

```python
# app/core/middleware.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

def add_security_middleware(app: FastAPI):
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost").split(",")
    )

    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
```

---

## ⚡ **Performance Optimization**

### **1. Application Optimization**

```python
# app/core/config.py
import os

class Settings:
    # FastAPI settings
    workers: int = int(os.getenv("WORKERS", "4"))
    worker_class: str = "uvicorn.workers.UvicornWorker"
    max_requests: int = 1000
    max_requests_jitter: int = 100
    preload_app: bool = True
    
    # Database connection pooling
    mongodb_max_connections: int = 100
    mongodb_min_connections: int = 10
    
    # Caching
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    cache_ttl: int = 3600
```

### **2. Database Optimization**

```javascript
// MongoDB optimization script
use nhan88ng_production

// Create compound indexes for better query performance
db.products.createIndex({ "shop": 1, "status": 1, "is_featured": 1 })
db.products.createIndex({ "shop": 1, "category_ids": 1, "price": 1 })
db.products.createIndex({ "shop": 1, "created_at": -1, "status": 1 })

// Enable MongoDB profiler for slow queries
db.setProfilingLevel(1, { slowms: 100 })

// Check current indexes
db.products.getIndexes()
```

### **3. Caching with Redis**

```python
# app/core/cache.py
import redis
import json
from typing import Optional, Any

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except:
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        try:
            self.redis.setex(key, ttl, json.dumps(value))
        except:
            pass
    
    async def delete(self, key: str):
        try:
            self.redis.delete(key)
        except:
            pass

# Usage in endpoints
@router.get("/products/")
async def get_products(shop: str, cache: CacheManager = Depends(get_cache)):
    cache_key = f"products:{shop}:{hash(str(request.query_params))}"
    
    # Try cache first
    cached_result = await cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # Query database
    products = await get_products_from_db(shop, params)
    
    # Cache result
    await cache.set(cache_key, products, ttl=1800)
    
    return products
```

---

## 📊 **Monitoring & Logging**

### **1. Application Logging**

```python
# app/core/logging.py
import logging
import sys
from datetime import datetime

def setup_logging():
    logger = logging.getLogger("api-nhan88ng")
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler("/var/log/api-nhan88ng/app.log")
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Usage
logger = setup_logging()

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    process_time = datetime.now() - start_time
    
    logger.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time.total_seconds():.3f}s"
    )
    
    return response
```

### **2. Health Monitoring**

```python
# app/api/v1/endpoints/health.py
import psutil
import time
from datetime import datetime

@router.get("/health/detailed")
async def detailed_health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time() - start_time,
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        },
        "database": {
            "connected": await check_database_connection(),
            "response_time": await measure_db_response_time()
        },
        "cache": {
            "connected": await check_redis_connection(),
            "response_time": await measure_cache_response_time()
        }
    }
```

### **3. Prometheus Metrics**

```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active database connections')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### **4. Log Rotation**

```bash
# /etc/logrotate.d/api-nhan88ng
/var/log/api-nhan88ng/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 api-nhan88ng api-nhan88ng
    postrotate
        systemctl reload api-nhan88ng
    endscript
}
```

---

## 💾 **Backup & Recovery**

### **1. Automated Database Backup**

```bash
#!/bin/bash
# /opt/scripts/backup-mongodb.sh

BACKUP_DIR="/var/backups/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="nhan88ng_backup_$DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
mongodump --db nhan88ng_production --out $BACKUP_DIR/$BACKUP_NAME

# Compress backup
tar -czf $BACKUP_DIR/$BACKUP_NAME.tar.gz -C $BACKUP_DIR $BACKUP_NAME
rm -rf $BACKUP_DIR/$BACKUP_NAME

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
```

### **2. Backup Cron Job**

```bash
# Add to crontab
0 2 * * * /opt/scripts/backup-mongodb.sh

# Backup uploads directory
0 3 * * * rsync -av /var/www/api-nhan88ng/uploads/ /var/backups/uploads/
```

### **3. Recovery Procedures**

```bash
# Restore database from backup
tar -xzf /var/backups/mongodb/nhan88ng_backup_20250810_020000.tar.gz
mongorestore --db nhan88ng_production --drop nhan88ng_backup_20250810_020000/nhan88ng_production/

# Restore uploads
rsync -av /var/backups/uploads/ /var/www/api-nhan88ng/uploads/
```

---

## 🔄 **CI/CD Pipeline**

### **1. GitHub Actions Workflow**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest
        
    - name: Run tests
      run: pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /var/www/api-nhan88ng
          git pull origin main
          source venv/bin/activate
          pip install -r requirements.txt
          sudo systemctl restart api-nhan88ng
          sudo systemctl reload nginx
```

### **2. Blue-Green Deployment**

```bash
#!/bin/bash
# blue-green-deploy.sh

CURRENT_PORT=$(systemctl show api-nhan88ng --property ExecStart | grep -o 'port [0-9]*' | cut -d' ' -f2)
NEW_PORT=$((CURRENT_PORT == 8000 ? 8001 : 8000))

echo "Current port: $CURRENT_PORT, New port: $NEW_PORT"

# Update code
git pull origin main
source venv/bin/activate
pip install -r requirements.txt

# Start new instance
uvicorn main:app --host 0.0.0.0 --port $NEW_PORT --workers 4 &
NEW_PID=$!

# Wait for new instance to be ready
sleep 10

# Health check
if curl -f http://localhost:$NEW_PORT/health; then
    echo "New instance healthy"
    
    # Update nginx upstream
    sed -i "s/server api:$CURRENT_PORT/server api:$NEW_PORT/" /etc/nginx/sites-available/api-nhan88ng
    nginx -s reload
    
    # Stop old instance
    systemctl stop api-nhan88ng
    
    # Update systemd service
    sed -i "s/--port $CURRENT_PORT/--port $NEW_PORT/" /etc/systemd/system/api-nhan88ng.service
    systemctl daemon-reload
    systemctl start api-nhan88ng
    
    echo "Deployment successful"
else
    echo "New instance failed health check"
    kill $NEW_PID
    exit 1
fi
```

---

## 🔧 **Troubleshooting**

### **1. Common Issues**

#### **Service Won't Start**
```bash
# Check logs
sudo journalctl -u api-nhan88ng -f

# Check configuration
python -c "from app.core.config import settings; print(settings)"

# Check dependencies
source venv/bin/activate
pip check
```

#### **Database Connection Issues**
```bash
# Test MongoDB connection
mongosh mongodb://localhost:27017/nhan88ng_production

# Check MongoDB logs
sudo journalctl -u mongod -f

# Check network connectivity
telnet localhost 27017
```

#### **High Memory Usage**
```bash
# Check memory usage
htop
free -h

# Check for memory leaks
python -m memory_profiler main.py

# Restart services
sudo systemctl restart api-nhan88ng
```

### **2. Performance Issues**

#### **Slow Database Queries**
```javascript
// Check slow queries
use nhan88ng_production
db.setProfilingLevel(2)
db.system.profile.find().limit(5).sort({ts:-1}).pretty()

// Check indexes
db.products.explain("executionStats").find({"shop": "tinashop"})
```

#### **High CPU Usage**
```bash
# Check CPU usage by process
top -p $(pgrep -f "uvicorn")

# Check worker configuration
ps aux | grep uvicorn

# Adjust worker count
sudo systemctl edit api-nhan88ng
```

### **3. Security Issues**

#### **Failed Login Attempts**
```bash
# Check logs for failed attempts
grep "Failed login" /var/log/api-nhan88ng/app.log

# Block suspicious IPs
sudo ufw deny from suspicious.ip.address
```

#### **SSL Certificate Issues**
```bash
# Check certificate expiry
openssl x509 -in /etc/ssl/certs/yourdomain.crt -text -noout

# Test SSL configuration
curl -I https://yourdomain.com
```

### **4. Monitoring Commands**

```bash
# Service status
sudo systemctl status api-nhan88ng mongodb nginx

# Disk usage
df -h
du -sh /var/www/api-nhan88ng/uploads/*

# Network connections
netstat -tulpn | grep :8000

# Process monitoring
ps aux | grep -E "(uvicorn|mongod|nginx)"

# Log monitoring
tail -f /var/log/api-nhan88ng/app.log
tail -f /var/log/nginx/access.log
```

---

## 📋 **Post-Deployment Checklist**

### **Final Verification**
- [ ] All services running and healthy
- [ ] SSL certificate installed and working
- [ ] Database indexes created and optimized
- [ ] Admin user created and accessible
- [ ] API endpoints responding correctly
- [ ] File uploads working and serving correctly
- [ ] Monitoring and logging configured
- [ ] Backups scheduled and tested
- [ ] Security headers configured
- [ ] Firewall rules applied
- [ ] Documentation updated with production URLs

### **Performance Testing**
```bash
# Load testing with Apache Bench
ab -n 1000 -c 10 https://yourdomain.com/health

# API endpoint testing
ab -n 100 -c 5 -H "Authorization: Bearer $TOKEN" https://yourdomain.com/api/v1/products/?shop=tinashop
```

### **Security Audit**
```bash
# SSL testing
sslscan yourdomain.com

# Security headers check
curl -I https://yourdomain.com

# Port scanning
nmap yourdomain.com
```

---

**🚀 Congratulations! Your API Nhan88ng platform is now deployed and ready for production use. Monitor the logs and metrics to ensure optimal performance.**
