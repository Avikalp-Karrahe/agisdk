# Deployment Guide - Enhanced AGI Agents

## Overview

This guide provides comprehensive instructions for deploying the Enhanced AGI Agents framework in production environments. The framework is designed for scalability, reliability, and easy maintenance.

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended for production)
- **Storage**: 1GB free space for logs and memory storage
- **Network**: Stable internet connection for web automation tasks

### Dependencies
```bash
# Core dependencies
pip install agisdk>=0.1.0
pip install openai>=1.0.0
pip install anthropic>=0.7.0

# Optional performance enhancements
pip install redis>=4.0.0  # For distributed memory
pip install celery>=5.0.0  # For task queuing
pip install prometheus-client>=0.14.0  # For monitoring
```

## Installation Methods

### Method 1: Direct Installation

```bash
# Clone the repository
git clone https://github.com/your-username/agisdk.git
cd agisdk/examples/enhanced_agents

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Method 2: Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Run the application
CMD ["python", "config_010_enhanced_agent.py"]
```

```bash
# Build and run Docker container
docker build -t enhanced-agi-agent .
docker run -d --name agi-agent \
  -e OPENAI_API_KEY=your_key_here \
  -e ANTHROPIC_API_KEY=your_key_here \
  -v $(pwd)/logs:/app/logs \
  enhanced-agi-agent
```

### Method 3: Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: enhanced-agi-agent
  labels:
    app: enhanced-agi-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: enhanced-agi-agent
  template:
    metadata:
      labels:
        app: enhanced-agi-agent
    spec:
      containers:
      - name: agi-agent
        image: enhanced-agi-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: anthropic-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "1000m"
        volumeMounts:
        - name: logs-volume
          mountPath: /app/logs
        - name: memory-volume
          mountPath: /app/memory
      volumes:
      - name: logs-volume
        persistentVolumeClaim:
          claimName: logs-pvc
      - name: memory-volume
        persistentVolumeClaim:
          claimName: memory-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: enhanced-agi-agent-service
spec:
  selector:
    app: enhanced-agi-agent
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

## Configuration

### Environment Variables

```bash
# .env file
# API Keys (Required)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Memory Configuration
MEMORY_BACKEND=local  # Options: local, redis, postgresql
MEMORY_MAX_SIZE=1000  # Maximum number of stored experiences
MEMORY_CLEANUP_INTERVAL=3600  # Cleanup interval in seconds

# Performance Settings
MAX_CONCURRENT_TASKS=5
TASK_TIMEOUT=300  # Task timeout in seconds
RETRY_MAX_ATTEMPTS=3
RETRY_EXPONENTIAL_BASE=2

# Logging Configuration
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json  # Options: json, text
LOG_FILE_PATH=./logs/enhanced_agent.log

# Browser Configuration
HEADLESS_BROWSER=true
BROWSER_TIMEOUT=30
PAGE_LOAD_TIMEOUT=30

# Domain-Specific Settings
DEFAULT_WAIT_TIME=2
ELEMENT_WAIT_TIMEOUT=10
SCROLL_PAUSE_TIME=1

# Monitoring
METRICS_ENABLED=true
METRICS_PORT=9090
HEALTH_CHECK_ENDPOINT=/health
```

### Advanced Configuration

```python
# config/production.py
class ProductionConfig:
    # Memory System Configuration
    MEMORY_CONFIG = {
        'episodic_memory': {
            'max_experiences': 5000,
            'similarity_threshold': 0.8,
            'cleanup_strategy': 'lru'
        },
        'semantic_memory': {
            'max_patterns': 1000,
            'learning_rate': 0.1,
            'consolidation_interval': 3600
        },
        'working_memory': {
            'context_window': 10,
            'attention_mechanism': 'weighted'
        }
    }
    
    # Self-Critique Configuration
    CRITIQUE_CONFIG = {
        'validation_threshold': 0.7,
        'assessment_criteria': [
            'element_availability',
            'action_appropriateness',
            'success_probability'
        ],
        'learning_enabled': True
    }
    
    # Planning System Configuration
    PLANNING_CONFIG = {
        'max_decomposition_depth': 5,
        'strategy_selection_method': 'probability_weighted',
        'contingency_planning': True,
        'goal_timeout': 600
    }
    
    # Retry System Configuration
    RETRY_CONFIG = {
        'strategies': {
            'element_not_found': 'wait_and_retry',
            'timeout': 'exponential_backoff',
            'network_error': 'immediate_retry',
            'javascript_error': 'page_refresh'
        },
        'max_retries_per_strategy': 3,
        'global_max_retries': 10
    }
```

## Production Deployment Steps

### Step 1: Environment Setup

```bash
# Create production environment
python -m venv venv-prod
source venv-prod/bin/activate  # On Windows: venv-prod\Scripts\activate

# Install production dependencies
pip install -r requirements.txt
pip install gunicorn  # For web server deployment
pip install supervisor  # For process management
```

### Step 2: Security Configuration

```bash
# Set up secure API key storage
sudo mkdir -p /etc/agi-agent/secrets
sudo chmod 700 /etc/agi-agent/secrets

# Store API keys securely
echo "your_openai_key" | sudo tee /etc/agi-agent/secrets/openai_key
echo "your_anthropic_key" | sudo tee /etc/agi-agent/secrets/anthropic_key
sudo chmod 600 /etc/agi-agent/secrets/*

# Create service user
sudo useradd -r -s /bin/false agi-agent
sudo chown -R agi-agent:agi-agent /etc/agi-agent
```

### Step 3: Process Management

```ini
# /etc/supervisor/conf.d/agi-agent.conf
[program:agi-agent]
command=/path/to/venv-prod/bin/python /path/to/enhanced_agents/config_010_enhanced_agent.py
directory=/path/to/enhanced_agents
user=agi-agent
autostart=true
autorestart=true
stderr_logfile=/var/log/agi-agent/error.log
stdout_logfile=/var/log/agi-agent/output.log
environment=PYTHONPATH="/path/to/enhanced_agents"

[program:agi-agent-worker]
command=/path/to/venv-prod/bin/celery worker -A enhanced_agent.celery --loglevel=info
directory=/path/to/enhanced_agents
user=agi-agent
numprocs=4
process_name=%(program_name)s_%(process_num)02d
autostart=true
autorestart=true
stderr_logfile=/var/log/agi-agent/worker_error.log
stdout_logfile=/var/log/agi-agent/worker_output.log
```

### Step 4: Monitoring Setup

```python
# monitoring/prometheus_metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
task_counter = Counter('agi_tasks_total', 'Total number of tasks processed')
task_duration = Histogram('agi_task_duration_seconds', 'Task execution time')
memory_usage = Gauge('agi_memory_usage_bytes', 'Memory usage in bytes')
success_rate = Gauge('agi_success_rate', 'Task success rate')

# Start metrics server
start_http_server(9090)
```

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'agi-agent'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 5s
    metrics_path: /metrics
```

### Step 5: Load Balancing

```nginx
# /etc/nginx/sites-available/agi-agent
upstream agi_agent {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://agi_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    location /health {
        proxy_pass http://agi_agent/health;
        access_log off;
    }
    
    location /metrics {
        proxy_pass http://127.0.0.1:9090/metrics;
        allow 10.0.0.0/8;
        deny all;
    }
}
```

## Scaling Strategies

### Horizontal Scaling

```python
# distributed/task_queue.py
from celery import Celery

app = Celery('enhanced_agent')
app.config_from_object('config.celery_config')

@app.task
def process_web_task(task_data):
    from config_010_enhanced_agent import Config010EnhancedAgent
    
    agent = Config010EnhancedAgent()
    result = agent.execute_task(task_data)
    return result

# Scale workers based on queue length
@app.task
def auto_scale_workers():
    queue_length = get_queue_length()
    if queue_length > 100:
        spawn_additional_workers(2)
    elif queue_length < 10:
        reduce_workers(1)
```

### Vertical Scaling

```python
# performance/memory_optimization.py
class OptimizedMemorySystem:
    def __init__(self):
        self.memory_pool = MemoryPool(max_size=10000)
        self.compression_enabled = True
        self.lazy_loading = True
    
    def optimize_memory_usage(self):
        # Implement memory compression
        # Use lazy loading for large datasets
        # Implement memory pooling
        pass
```

## Maintenance and Updates

### Automated Deployment

```bash
#!/bin/bash
# deploy.sh
set -e

echo "Starting deployment..."

# Pull latest code
git pull origin main

# Install/update dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Backup current deployment
sudo cp -r /opt/agi-agent /opt/agi-agent.backup.$(date +%Y%m%d_%H%M%S)

# Deploy new version
sudo cp -r . /opt/agi-agent/

# Restart services
sudo supervisorctl restart agi-agent
sudo supervisorctl restart agi-agent-worker

# Health check
sleep 10
curl -f http://localhost/health || exit 1

echo "Deployment completed successfully!"
```

### Monitoring and Alerting

```yaml
# alerting/alerts.yml
groups:
- name: agi-agent-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(agi_tasks_failed_total[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"
  
  - alert: HighMemoryUsage
    expr: agi_memory_usage_bytes > 3e9
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High memory usage"
      description: "Memory usage is {{ $value }} bytes"
  
  - alert: ServiceDown
    expr: up{job="agi-agent"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "AGI Agent service is down"
```

## Troubleshooting

### Common Issues

1. **Memory Leaks**
   ```bash
   # Monitor memory usage
   ps aux | grep python
   # Check for memory leaks
   valgrind --tool=memcheck python config_010_enhanced_agent.py
   ```

2. **Performance Degradation**
   ```python
   # Enable performance profiling
   import cProfile
   cProfile.run('agent.execute_task(task)', 'profile_output')
   ```

3. **Browser Issues**
   ```bash
   # Check browser dependencies
   which chromium-browser
   chromium-browser --version
   
   # Test browser automation
   python -c "from selenium import webdriver; driver = webdriver.Chrome(); driver.quit()"
   ```

### Log Analysis

```bash
# Analyze error patterns
grep "ERROR" /var/log/agi-agent/error.log | tail -100

# Monitor performance metrics
tail -f /var/log/agi-agent/output.log | grep "execution_time"

# Check memory usage trends
grep "memory_usage" /var/log/agi-agent/output.log | awk '{print $3}' | sort -n
```

## Security Considerations

### API Key Management
- Use environment variables or secure key management systems
- Rotate API keys regularly
- Monitor API usage for anomalies

### Network Security
- Use HTTPS for all external communications
- Implement rate limiting
- Set up firewall rules

### Data Protection
- Encrypt sensitive data at rest
- Implement secure logging practices
- Regular security audits

This deployment guide provides a comprehensive foundation for running Enhanced AGI Agents in production environments with proper scaling, monitoring, and maintenance procedures.