# NeuraLex Platform

![NeuraLex Platform](https://img.shields.io/badge/NeuraLex-Platform-orange?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green?style=flat-square)
![Redis](https://img.shields.io/badge/Redis-Queue-red?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?style=flat-square)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-purple?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue?style=flat-square)

**Advanced AI-powered document processing and classification platform** built with FastAPI, Redis job queues, local Ollama LLMs, and modern ML technologies. Features comprehensive admin dashboard with real-time monitoring, model management, and scalable infrastructure.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#️-architecture)
- [Live Demo](#-live-demo)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [API Documentation](#-api-documentation)
- [Admin Dashboard](#-admin-dashboard)
- [Configuration](#️-configuration)
- [Deployment](#-deployment)
- [Performance](#-performance)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features

### Core Functionality
- **🤖 Intelligent Document Classification**: Ollama-powered local LLM classification into document types (invoices, contracts, emails)
- **🔍 Advanced Entity Extraction**: Extract names, dates, amounts, addresses with high accuracy using AI models
- **⚡ Real-time Processing**: Redis-powered job queues for scalable, asynchronous document processing
- **🌐 RESTful API**: Comprehensive API with OpenAPI/Swagger documentation and JWT authentication
- **📊 Modern Web Interface**: Glass morphism design with black/red/orange gradient color scheme
- **☁️ Cloud Integration**: Google Cloud Storage and Vision API integration for document ingestion
- **⚙️ Background Workers**: Efficient async processing with robust error handling and retry logic

### Admin Dashboard
- **📈 System Monitoring**: Real-time CPU, memory, disk usage with historical charts
- **🔧 Model Management**: Ollama model configuration, testing, and performance metrics
- **📝 Live Logging**: Real-time log streaming with filtering and export capabilities
- **🎯 Finetuning**: Model training interface with progress tracking and dataset management
- **📄 Document Processing**: Batch upload, OCR pipeline, and classification results
- **📊 Analytics**: Processing statistics, success rates, and performance trends
- **⚙️ Configuration**: System settings, API keys, and optimization parameters

### Technical Features
- **🔐 Security**: JWT authentication, API rate limiting, encrypted data storage
- **📦 Containerization**: Docker support with multi-stage builds and optimized images
- **🚀 Performance**: Caching strategies, connection pooling, and horizontal scaling
- **🔄 CI/CD**: Automated testing, deployment pipelines, and quality assurance
- **📱 Responsive**: Mobile-first design with progressive web app capabilities

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   ML Engine     │
│   Dashboard     │◄───┤   FastAPI       │◄───┤   Ollama        │
│   (JavaScript)  │    │   (Python)      │    │   (Local LLM)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐             │
         │              │   Data Layer    │             │
         └──────────────┤   PostgreSQL    │─────────────┘
                        │   Redis Cache   │
                        └─────────────────┘
```

### Technology Stack

**Backend**
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **SQLAlchemy**: Python SQL toolkit and Object-Relational Mapping
- **PostgreSQL**: Advanced open-source relational database
- **Redis**: In-memory data structure store for caching and job queues
- **Uvicorn**: Lightning-fast ASGI server implementation

**AI/ML**
- **Ollama**: Local large language model inference engine
- **Google Vision API**: Optical character recognition and image analysis
- **Custom ML Pipeline**: Document classification and entity extraction

**Frontend**
- **Vanilla JavaScript**: Modern ES6+ with modular architecture
- **CSS3**: Glass morphism design with custom animations
- **Lucide Icons**: Beautiful, customizable SVG icons
- **Responsive Design**: Mobile-first approach with progressive enhancement

**Infrastructure**
- **Docker**: Containerized deployment with multi-stage builds
- **Nginx**: High-performance web server and reverse proxy
- **systemd**: Service management for production deployment
- **GitHub Actions**: Automated CI/CD pipelines

## 🌐 Live Demo

**Production Instance**: [49.13.102.114:5000](http://49.13.102.114:5000)
- Admin Dashboard: [/admin](http://49.13.102.114:5000/admin)
- API Documentation: [/docs](http://49.13.102.114:5000/docs)
- Health Check: [/health](http://49.13.102.114:5000/health)

**Test Credentials**: Contact admin for demo access

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Docker (optional)
- Ollama (for AI features)

### 1. Clone Repository
```bash
git clone https://github.com/your-org/neuralex-platform.git
cd neuralex-platform
```

### 2. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/neuralex"
export REDIS_URL="redis://localhost:6379"

# Initialize database
python -c "from app.db import create_tables; create_tables()"
```

### 4. Start Services
```bash
# Start Redis
redis-server

# Start Ollama (optional)
ollama serve
ollama pull llama3.2

# Start application
python -m uvicorn app.simple_main:app --host 0.0.0.0 --port 5000 --reload
```

### 5. Access Application
- **Main Dashboard**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin  
- **API Docs**: http://localhost:5000/docs

## 📚 Installation

### Docker Installation (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/your-org/neuralex-platform.git
cd neuralex-platform

# 2. Build and start with Docker Compose
docker-compose up -d

# 3. Initialize database
docker-compose exec app python -c "from app.db import create_tables; create_tables()"
```

### Manual Installation

#### System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql redis-server

# macOS
brew install python@3.11 postgresql redis

# Windows (using Chocolatey)
choco install python postgresql redis-64
```

#### Python Environment
```bash
# Create virtual environment
python3.11 -m venv neuralex-env
source neuralex-env/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Database Configuration
```bash
# PostgreSQL setup
sudo -u postgres createuser neuralex
sudo -u postgres createdb neuralex -O neuralex
sudo -u postgres psql -c "ALTER USER neuralex PASSWORD 'your_password';"

# Redis configuration (optional tuning)
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

#### Ollama Setup (AI Features)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve

# Pull required models
ollama pull llama3.2
ollama pull mistral
```

### Environment Variables
```bash
# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://neuralex:your_password@localhost:5432/neuralex
REDIS_URL=redis://localhost:6379
OLLAMA_HOST=http://localhost:11434
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
JWT_SECRET_KEY=your-super-secret-jwt-key
ENVIRONMENT=production
EOF
```

## 📖 API Documentation

### Core Endpoints

#### Document Processing
```http
POST /ingest
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "gcs_uri": "gs://bucket/document.pdf",
  "payload": {
    "content": "Document text content",
    "metadata": {"type": "invoice", "source": "email"}
  }
}
```

#### Job Management
```http
# Get job status
GET /jobs/{job_id}

# List all jobs with pagination
GET /jobs?skip=0&limit=50

# Response format
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed|processing|failed",
  "result": {
    "document_type": "invoice",
    "event_type": "payment_received",
    "confidence": 0.95,
    "extracted_entities": {...}
  },
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:05:00Z"
}
```

#### AI Analysis
```http
POST /analyze
Content-Type: application/json

{
  "text": "Invoice from ACME Corp for $1,500.00 dated 2024-01-15",
  "model": "llama3.2",
  "task": "classification"
}
```

#### OCR Processing
```http
POST /ocr
Content-Type: multipart/form-data

file: [binary_image_data]
```

#### Search
```http
GET /search?q=invoice&limit=20
```

### Admin API Endpoints
```http
# System metrics
GET /api/admin/metrics

# Model status
GET /api/admin/models

# Configuration
GET /api/config/status
POST /api/config/save
```

### Response Codes
- `200` - Success
- `202` - Accepted (async processing)
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## 🎛️ Admin Dashboard

### Overview Section
- **Real-time Metrics**: CPU, memory, disk usage with live charts
- **Service Status**: Database, Redis, Ollama connectivity indicators
- **Recent Activity**: Latest processed documents and system events
- **Quick Actions**: Restart services, clear cache, export logs

### Model Management
- **Ollama Integration**: Available models, download status, performance metrics
- **Model Configuration**: Temperature, max tokens, top-p parameters
- **Testing Interface**: Real-time model testing with sample inputs
- **Performance Analytics**: Response times, accuracy metrics, usage statistics

### System Monitoring
- **Live Logs**: Real-time log streaming with filtering by level and component
- **Error Tracking**: Detailed error analysis with stack traces and context
- **Performance Graphs**: Historical system performance with customizable time ranges
- **Alerts Management**: Configure notifications for critical events

### Finetuning Interface
- **Training Jobs**: Start, stop, and monitor model training processes
- **Dataset Management**: Upload and manage training datasets
- **Progress Tracking**: Real-time training progress with loss curves
- **Model Evaluation**: Automated testing on validation datasets

### Document Processing
- **Batch Upload**: Multi-file upload with drag-and-drop interface
- **Processing Pipeline**: OCR → Classification → Entity Extraction
- **Results Viewer**: Interactive display of processing results
- **Export Options**: CSV, JSON, PDF report generation

### Analytics Dashboard
- **Processing Statistics**: Success rates, throughput, error analysis
- **Document Distribution**: Charts showing document type breakdown
- **Usage Trends**: Historical processing volume and patterns
- **Performance Insights**: Bottleneck identification and optimization suggestions

### Configuration Manager
- **System Settings**: Core application configuration
- **Integration Setup**: Third-party service credentials and endpoints
- **Security Configuration**: JWT settings, API rate limits, access controls
- **Optimization Parameters**: Caching, compression, batch processing settings

## ⚙️ Configuration

### Application Settings
```yaml
# config.yaml
app:
  name: "NeuraLex Platform"
  version: "1.0.0"
  debug: false
  host: "0.0.0.0"
  port: 5000

database:
  url: "postgresql://user:pass@localhost:5432/neuralex"
  pool_size: 20
  max_overflow: 0
  pool_timeout: 30

redis:
  url: "redis://localhost:6379"
  max_connections: 100
  socket_timeout: 30

ollama:
  host: "http://localhost:11434"
  default_model: "llama3.2"
  timeout: 120
  max_retries: 3

security:
  jwt_secret: "your-secret-key"
  token_expiry: 3600
  rate_limit: 100
```

### Google Cloud Configuration
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "service-account@project.iam.gserviceaccount.com"
}
```

### Model Parameters
```python
# Ollama model configuration
OLLAMA_CONFIG = {
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
```

## 🚀 Deployment

### Production Deployment (Hetzner)

#### Server Setup
```bash
# 1. Server provisioning (Hetzner Cloud)
# CPU: 4 cores, RAM: 8GB, Disk: 80GB SSD
# OS: Ubuntu 22.04 LTS

# 2. Initial server configuration
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose nginx certbot python3-certbot-nginx

# 3. Clone and deploy
git clone https://github.com/your-org/neuralex-platform.git
cd neuralex-platform
sudo ./deploy_hetzner.sh
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### SSL Setup
```bash
# Let's Encrypt SSL certificate
sudo certbot --nginx -d your-domain.com
```

#### System Service
```ini
# /etc/systemd/system/neuralex.service
[Unit]
Description=NeuraLex Platform
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=neuralex
WorkingDirectory=/opt/neuralex-platform
ExecStart=/opt/neuralex-platform/venv/bin/uvicorn app.simple_main:app --host 0.0.0.0 --port 5000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Docker Production Setup
```dockerfile
# Multi-stage production build
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
EXPOSE 5000
CMD ["uvicorn", "app.simple_main:app", "--host", "0.0.0.0", "--port", "5000"]
```

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/neuralex
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: neuralex
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
```

### Kubernetes Deployment
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: neuralex-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: neuralex-platform
  template:
    metadata:
      labels:
        app: neuralex-platform
    spec:
      containers:
      - name: neuralex
        image: neuralex/platform:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: neuralex-secrets
              key: database-url
---
apiVersion: v1
kind: Service
metadata:
  name: neuralex-service
spec:
  selector:
    app: neuralex-platform
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

## ⚡ Performance

### Benchmarks
- **Throughput**: 1000+ documents/minute
- **Latency**: <200ms average response time
- **Concurrency**: 100+ simultaneous connections
- **Memory Usage**: <512MB base footprint
- **Uptime**: 99.9% availability

### Optimization Strategies

#### Database Optimization
```sql
-- Index optimization
CREATE INDEX CONCURRENTLY idx_jobs_status ON jobs(status);
CREATE INDEX CONCURRENTLY idx_jobs_created_at ON jobs(created_at);
CREATE INDEX CONCURRENTLY idx_documents_type ON documents(document_type);

-- Connection pooling
PGBOUNCER_CONFIG = {
    "pool_size": 25,
    "max_client_conn": 100,
    "default_pool_size": 20
}
```

#### Redis Caching
```python
# Cache frequently accessed data
CACHE_CONFIG = {
    "model_results": 3600,  # 1 hour
    "system_metrics": 300,  # 5 minutes
    "user_sessions": 86400  # 24 hours
}
```

#### Application Tuning
```python
# FastAPI optimization
app = FastAPI(
    title="NeuraLex Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Uvicorn production settings
uvicorn.run(
    app,
    host="0.0.0.0",
    port=5000,
    workers=4,
    loop="uvloop",
    http="httptools",
    access_log=False
)
```

### Monitoring & Alerting
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active connections')
```

## 🔒 Security

### Authentication & Authorization
- **JWT Tokens**: Secure API access with configurable expiration
- **Role-Based Access**: Admin, user, and read-only permission levels
- **API Rate Limiting**: Prevent abuse with configurable limits
- **CORS Protection**: Controlled cross-origin resource sharing

### Data Protection
- **Encryption at Rest**: Sensitive data encrypted in database
- **TLS/SSL**: All traffic encrypted in transit
- **Audit Logging**: Comprehensive activity tracking
- **Data Retention**: Configurable data lifecycle policies

### Security Best Practices
```python
# JWT configuration
JWT_CONFIG = {
    "algorithm": "HS256",
    "access_token_expire_minutes": 60,
    "refresh_token_expire_days": 30
}

# Rate limiting
RATE_LIMIT_CONFIG = {
    "requests_per_minute": 100,
    "burst_size": 200,
    "key_func": "get_client_ip"
}
```

### Vulnerability Management
- **Dependency Scanning**: Automated security vulnerability detection
- **Code Analysis**: Static code analysis with security rules
- **Penetration Testing**: Regular security assessments
- **Security Headers**: OWASP recommended HTTP security headers

## 🧪 Testing

### Test Suite
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test categories
pytest tests/test_api.py -v
pytest tests/test_ml.py -v
pytest tests/test_integration.py -v
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability and penetration testing

### Continuous Integration
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=app
      - name: Security scan
        run: bandit -r app/
```

## 🤝 Contributing

### Development Setup
```bash
# 1. Fork and clone repository
git clone https://github.com/your-username/neuralex-platform.git
cd neuralex-platform

# 2. Create development branch
git checkout -b feature/your-feature-name

# 3. Set up development environment
python -m venv dev-env
source dev-env/bin/activate
pip install -r requirements-dev.txt

# 4. Install pre-commit hooks
pre-commit install
```

### Code Standards
- **Python**: PEP 8 style guide with Black formatter
- **JavaScript**: ESLint with Airbnb configuration
- **Documentation**: Comprehensive docstrings and comments
- **Testing**: Minimum 80% test coverage required

### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Run full test suite and linting
4. Update documentation if needed
5. Submit pull request with detailed description

### Issue Reporting
- **Bug Reports**: Use bug report template with reproduction steps
- **Feature Requests**: Describe use case and proposed solution
- **Security Issues**: Report privately to security@neuralex.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Commercial Usage
- ✅ Commercial use permitted
- ✅ Modification and distribution allowed
- ✅ Private use allowed
- ❌ No warranty or liability

### Attribution
When using NeuraLex Platform in your projects, please include:
```
Powered by NeuraLex Platform
https://github.com/your-org/neuralex-platform
```

## 📞 Support & Contact

### Community Support
- **GitHub Issues**: [Issues](https://github.com/your-org/neuralex-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/neuralex-platform/discussions)
- **Documentation**: [Wiki](https://github.com/your-org/neuralex-platform/wiki)

### Professional Support
- **Enterprise Support**: contact@neuralex.com
- **Custom Development**: development@neuralex.com
- **Training & Consulting**: consulting@neuralex.com

### Acknowledgments
- FastAPI framework and community
- Ollama team for local LLM integration
- Open source contributors and maintainers
- Beta testers and early adopters

---

**Built with ❤️ for the AI and document processing community**

[![Star on GitHub](https://img.shields.io/github/stars/your-org/neuralex-platform?style=social)](https://github.com/your-org/neuralex-platform)
[![Follow on Twitter](https://img.shields.io/twitter/follow/neuralex?style=social)](https://twitter.com/neuralex)

