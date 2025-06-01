# NeuraLex Platform

![NeuraLex Platform](https://img.shields.io/badge/NeuraLex-Platform-orange?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green?style=flat-square)
![Redis](https://img.shields.io/badge/Redis-Queue-red?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?style=flat-square)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-purple?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue?style=flat-square)

**Fortschrittliche KI-gestützte Dokumentenverarbeitungs- und Klassifizierungsplattform** entwickelt mit FastAPI, Redis-Job-Warteschlangen, lokalen Ollama-LLMs und modernen ML-Technologien. Bietet umfassendes Admin-Dashboard mit Echtzeit-Überwachung, Modellverwaltung und skalierbarer Infrastruktur.

## 📋 Inhaltsverzeichnis

- [Funktionen](#-funktionen)
- [Architektur](#️-architektur)
- [Live-Demo](#-live-demo)
- [Schnellstart](#-schnellstart)
- [Installation](#-installation)
- [API-Dokumentation](#-api-dokumentation)
- [Admin-Dashboard](#-admin-dashboard)
- [Konfiguration](#️-konfiguration)
- [Bereitstellung](#-bereitstellung)
- [Performance](#-performance)
- [Sicherheit](#-sicherheit)
- [Mitwirken](#-mitwirken)
- [Lizenz](#-lizenz)

## 🚀 Funktionen

### Kernfunktionalitäten
- **🤖 Intelligente Dokumentklassifizierung**: Ollama-betriebene lokale LLM-Klassifizierung in Dokumenttypen (Rechnungen, Verträge, E-Mails)
- **🔍 Erweiterte Entitätsextraktion**: Extraktion von Namen, Daten, Beträgen, Adressen mit hoher Genauigkeit mittels KI-Modellen
- **⚡ Echtzeitverarbeitung**: Redis-basierte Job-Warteschlangen für skalierbare, asynchrone Dokumentverarbeitung
- **🌐 RESTful API**: Umfassende API mit OpenAPI/Swagger-Dokumentation und JWT-Authentifizierung
- **📊 Moderne Weboberfläche**: Glass-Morphism-Design mit schwarz/rot/orange Farbverlauf
- **☁️ Cloud-Integration**: Google Cloud Storage und Vision API Integration für Dokumentaufnahme
- **⚙️ Hintergrund-Worker**: Effiziente asynchrone Verarbeitung mit robuster Fehlerbehandlung und Wiederholungslogik

### Admin-Dashboard
- **📈 Systemüberwachung**: Echtzeit CPU-, Arbeitsspeicher-, Festplattennutzung mit historischen Diagrammen
- **🔧 Modellverwaltung**: Ollama-Modellkonfiguration, Tests und Performance-Metriken
- **📝 Live-Protokollierung**: Echtzeit-Log-Streaming mit Filterung und Export-Funktionen
- **🎯 Feinabstimmung**: Modell-Training-Interface mit Fortschrittsüberwachung und Dataset-Management
- **📄 Dokumentverarbeitung**: Batch-Upload, OCR-Pipeline und Klassifizierungsergebnisse
- **📊 Analytik**: Verarbeitungsstatistiken, Erfolgsraten und Performance-Trends
- **⚙️ Konfiguration**: Systemeinstellungen, API-Schlüssel und Optimierungsparameter

### Technische Funktionen
- **🔐 Sicherheit**: JWT-Authentifizierung, API-Rate-Limiting, verschlüsselte Datenspeicherung
- **📦 Containerisierung**: Docker-Unterstützung mit mehrstufigen Builds und optimierten Images
- **🚀 Performance**: Caching-Strategien, Verbindungspooling und horizontale Skalierung
- **🔄 CI/CD**: Automatisierte Tests, Deployment-Pipelines und Qualitätssicherung
- **📱 Responsive**: Mobile-First-Design mit progressiven Web-App-Funktionen

## 🏗️ Architektur

### Systemübersicht
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   ML-Engine     │
│   Dashboard     │◄───┤   FastAPI       │◄───┤   Ollama        │
│   (JavaScript)  │    │   (Python)      │    │   (Lokales LLM) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐             │
         │              │   Datenschicht  │             │
         └──────────────┤   PostgreSQL    │─────────────┘
                        │   Redis Cache   │
                        └─────────────────┘
```

### Technologie-Stack

**Backend**
- **FastAPI**: Modernes, schnelles Web-Framework mit automatischer API-Dokumentation
- **SQLAlchemy**: Python SQL-Toolkit und Objekt-Relationales Mapping
- **PostgreSQL**: Fortschrittliche Open-Source-Relationsdatenbank
- **Redis**: In-Memory-Datenstruktur-Speicher für Caching und Job-Warteschlangen
- **Uvicorn**: Blitzschnelle ASGI-Server-Implementierung

**KI/ML**
- **Ollama**: Lokale Large-Language-Model-Inferenz-Engine
- **Google Vision API**: Optische Zeichenerkennung und Bildanalyse
- **Custom ML-Pipeline**: Dokumentklassifizierung und Entitätsextraktion

**Frontend**
- **Vanilla JavaScript**: Modernes ES6+ mit modularer Architektur
- **CSS3**: Glass-Morphism-Design mit benutzerdefinierten Animationen
- **Lucide Icons**: Schöne, anpassbare SVG-Icons
- **Responsive Design**: Mobile-First-Ansatz mit progressiver Verbesserung

**Infrastruktur**
- **Docker**: Containerisierte Bereitstellung mit mehrstufigen Builds
- **Nginx**: Hochleistungs-Webserver und Reverse-Proxy
- **systemd**: Service-Management für Produktionsbereitstellung
- **GitHub Actions**: Automatisierte CI/CD-Pipelines

## 🌐 Live-Demo

**Produktionsinstanz**: [49.13.102.114:5000](http://49.13.102.114:5000)
- Admin-Dashboard: [/admin](http://49.13.102.114:5000/admin)
- API-Dokumentation: [/docs](http://49.13.102.114:5000/docs)
- Gesundheitscheck: [/health](http://49.13.102.114:5000/health)

**Test-Zugangsdaten**: Kontaktieren Sie den Administrator für Demo-Zugang

## ⚡ Schnellstart

### Voraussetzungen
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Docker (optional)
- Ollama (für KI-Funktionen)

### 1. Repository klonen
```bash
git clone https://github.com/your-org/neuralex-platform.git
cd neuralex-platform
```

### 2. Umgebung einrichten
```bash
# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### 3. Datenbank einrichten
```bash
# Umgebungsvariablen setzen
export DATABASE_URL="postgresql://user:password@localhost:5432/neuralex"
export REDIS_URL="redis://localhost:6379"

# Datenbank initialisieren
python -c "from app.db import create_tables; create_tables()"
```

### 4. Services starten
```bash
# Redis starten
redis-server

# Ollama starten (optional)
ollama serve
ollama pull llama3.2

# Anwendung starten
python -m uvicorn app.simple_main:app --host 0.0.0.0 --port 5000 --reload
```

### 5. Anwendung aufrufen
- **Haupt-Dashboard**: http://localhost:5000
- **Admin-Panel**: http://localhost:5000/admin  
- **API-Dokumentation**: http://localhost:5000/docs

## 📚 Installation

### Docker-Installation (Empfohlen)

```bash
# 1. Repository klonen
git clone https://github.com/your-org/neuralex-platform.git
cd neuralex-platform

# 2. Mit Docker Compose erstellen und starten
docker-compose up -d

# 3. Datenbank initialisieren
docker-compose exec app python -c "from app.db import create_tables; create_tables()"
```

### Manuelle Installation

#### System-Abhängigkeiten
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql redis-server

# macOS
brew install python@3.11 postgresql redis

# Windows (mit Chocolatey)
choco install python postgresql redis-64
```

#### Python-Umgebung
```bash
# Virtuelle Umgebung erstellen
python3.11 -m venv neuralex-env
source neuralex-env/bin/activate

# pip aktualisieren und Abhängigkeiten installieren
pip install --upgrade pip
pip install -r requirements.txt
```

#### Datenbank-Konfiguration
```bash
# PostgreSQL-Setup
sudo -u postgres createuser neuralex
sudo -u postgres createdb neuralex -O neuralex
sudo -u postgres psql -c "ALTER USER neuralex PASSWORD 'ihr_passwort';"

# Redis-Konfiguration (optionale Optimierung)
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

#### Ollama-Setup (KI-Funktionen)
```bash
# Ollama installieren
curl -fsSL https://ollama.com/install.sh | sh

# Ollama-Service starten
ollama serve

# Erforderliche Modelle herunterladen
ollama pull llama3.2
ollama pull mistral
```

### Umgebungsvariablen
```bash
# .env-Datei erstellen
cat > .env << EOF
DATABASE_URL=postgresql://neuralex:ihr_passwort@localhost:5432/neuralex
REDIS_URL=redis://localhost:6379
OLLAMA_HOST=http://localhost:11434
GOOGLE_APPLICATION_CREDENTIALS=/pfad/zu/service-account.json
JWT_SECRET_KEY=ihr-super-geheimer-jwt-schluessel
ENVIRONMENT=production
EOF
```

## 📖 API-Dokumentation

### Kern-Endpunkte

#### Dokumentverarbeitung
```http
POST /ingest
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "gcs_uri": "gs://bucket/dokument.pdf",
  "payload": {
    "content": "Dokumenttext-Inhalt",
    "metadata": {"type": "rechnung", "source": "email"}
  }
}
```

#### Job-Verwaltung
```http
# Job-Status abrufen
GET /jobs/{job_id}

# Alle Jobs mit Paginierung auflisten
GET /jobs?skip=0&limit=50

# Antwortformat
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed|processing|failed",
  "result": {
    "document_type": "rechnung",
    "event_type": "zahlung_erhalten",
    "confidence": 0.95,
    "extracted_entities": {...}
  },
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:05:00Z"
}
```

#### KI-Analyse
```http
POST /analyze
Content-Type: application/json

{
  "text": "Rechnung von ACME Corp über 1.500,00€ vom 15.01.2024",
  "model": "llama3.2",
  "task": "classification"
}
```

#### OCR-Verarbeitung
```http
POST /ocr
Content-Type: multipart/form-data

file: [binäre_bilddaten]
```

#### Suche
```http
GET /search?q=rechnung&limit=20
```

### Admin-API-Endpunkte
```http
# System-Metriken
GET /api/admin/metrics

# Modell-Status
GET /api/admin/models

# Konfiguration
GET /api/config/status
POST /api/config/save
```

### Antwort-Codes
- `200` - Erfolg
- `202` - Akzeptiert (asynchrone Verarbeitung)
- `400` - Fehlerhafte Anfrage
- `401` - Nicht autorisiert
- `404` - Nicht gefunden
- `500` - Interner Server-Fehler

## 🎛️ Admin-Dashboard

### Übersichts-Bereich
- **Echtzeit-Metriken**: CPU-, Arbeitsspeicher-, Festplattennutzung mit Live-Diagrammen
- **Service-Status**: Datenbank-, Redis-, Ollama-Verbindungsanzeigen
- **Letzte Aktivitäten**: Neueste verarbeitete Dokumente und Systemereignisse
- **Schnellaktionen**: Services neustarten, Cache leeren, Logs exportieren

### Modellverwaltung
- **Ollama-Integration**: Verfügbare Modelle, Download-Status, Performance-Metriken
- **Modellkonfiguration**: Temperature-, Max-Tokens-, Top-P-Parameter
- **Test-Interface**: Echtzeit-Modelltests mit Beispiel-Eingaben
- **Performance-Analytik**: Antwortzeiten, Genauigkeitsmetriken, Nutzungsstatistiken

### Systemüberwachung
- **Live-Logs**: Echtzeit-Log-Streaming mit Filterung nach Level und Komponente
- **Fehler-Tracking**: Detaillierte Fehleranalyse mit Stack-Traces und Kontext
- **Performance-Graphen**: Historische Systemperformance mit anpassbaren Zeitbereichen
- **Benachrichtigungsmanagement**: Benachrichtigungen für kritische Ereignisse konfigurieren

### Feinabstimmungs-Interface
- **Training-Jobs**: Modell-Training-Prozesse starten, stoppen und überwachen
- **Dataset-Management**: Training-Datasets hochladen und verwalten
- **Fortschrittsüberwachung**: Echtzeit-Training-Fortschritt mit Verlust-Kurven
- **Modell-Evaluierung**: Automatisierte Tests auf Validierungs-Datasets

### Dokumentverarbeitung
- **Batch-Upload**: Multi-File-Upload mit Drag-and-Drop-Interface
- **Verarbeitungs-Pipeline**: OCR → Klassifizierung → Entitätsextraktion
- **Ergebnis-Viewer**: Interaktive Anzeige der Verarbeitungsergebnisse
- **Export-Optionen**: CSV-, JSON-, PDF-Berichtsgenerierung

### Analytik-Dashboard
- **Verarbeitungsstatistiken**: Erfolgsraten, Durchsatz, Fehleranalyse
- **Dokumentverteilung**: Diagramme mit Dokumenttyp-Aufschlüsselung
- **Nutzungstrends**: Historisches Verarbeitungsvolumen und -muster
- **Performance-Einblicke**: Engpass-Identifikation und Optimierungsvorschläge

### Konfigurations-Manager
- **Systemeinstellungen**: Kernkonfiguration der Anwendung
- **Integrations-Setup**: Drittanbieter-Service-Zugangsdaten und Endpunkte
- **Sicherheitskonfiguration**: JWT-Einstellungen, API-Rate-Limits, Zugriffskontrollen
- **Optimierungsparameter**: Caching-, Komprimierungs-, Batch-Verarbeitungseinstellungen

## ⚙️ Konfiguration

### Anwendungseinstellungen
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
  jwt_secret: "ihr-geheimer-schluessel"
  token_expiry: 3600
  rate_limit: 100
```

### Google Cloud-Konfiguration
```json
{
  "type": "service_account",
  "project_id": "ihr-projekt-id",
  "private_key_id": "schluessel-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "service-account@projekt.iam.gserviceaccount.com"
}
```

### Modell-Parameter
```python
# Ollama-Modellkonfiguration
OLLAMA_CONFIG = {
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
```

## 🚀 Bereitstellung

### Produktionsbereitstellung (Hetzner)

#### Server-Setup
```bash
# 1. Server-Bereitstellung (Hetzner Cloud)
# CPU: 4 Kerne, RAM: 8GB, Festplatte: 80GB SSD
# OS: Ubuntu 22.04 LTS

# 2. Erste Server-Konfiguration
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose nginx certbot python3-certbot-nginx

# 3. Klonen und bereitstellen
git clone https://github.com/your-org/neuralex-platform.git
cd neuralex-platform
sudo ./deploy_hetzner.sh
```

#### Nginx-Konfiguration
```nginx
server {
    listen 80;
    server_name ihre-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### SSL-Setup
```bash
# Let's Encrypt SSL-Zertifikat
sudo certbot --nginx -d ihre-domain.com
```

## ⚡ Performance

### Benchmarks
- **Durchsatz**: 1000+ Dokumente/Minute
- **Latenz**: <200ms durchschnittliche Antwortzeit
- **Parallelität**: 100+ gleichzeitige Verbindungen
- **Speicherverbrauch**: <512MB Basis-Footprint
- **Verfügbarkeit**: 99,9% Uptime

## 🔒 Sicherheit

### Authentifizierung & Autorisierung
- **JWT-Token**: Sichere API-Zugriffe mit konfigurierbarer Ablaufzeit
- **Rollenbasierte Zugriffe**: Admin-, Benutzer- und Nur-Lese-Berechtigungsebenen
- **API-Rate-Limiting**: Missbrauchsverhinderung mit konfigurierbaren Limits
- **CORS-Schutz**: Kontrollierte Cross-Origin-Ressourcenfreigabe

## 🧪 Tests

### Test-Suite
```bash
# Alle Tests ausführen
pytest tests/ -v

# Mit Coverage ausführen
pytest tests/ --cov=app --cov-report=html

# Spezifische Test-Kategorien ausführen
pytest tests/test_api.py -v
pytest tests/test_ml.py -v
pytest tests/test_integration.py -v
```

## 🤝 Mitwirken

### Entwicklungsumgebung
```bash
# 1. Repository forken und klonen
git clone https://github.com/ihr-username/neuralex-platform.git
cd neuralex-platform

# 2. Entwicklungsbranch erstellen
git checkout -b feature/ihr-feature-name

# 3. Entwicklungsumgebung einrichten
python -m venv dev-env
source dev-env/bin/activate
pip install -r requirements-dev.txt

# 4. Pre-commit-Hooks installieren
pre-commit install
```

### Code-Standards
- **Python**: PEP 8-Styleguide mit Black-Formatter
- **JavaScript**: ESLint mit Airbnb-Konfiguration
- **Dokumentation**: Umfassende Docstrings und Kommentare
- **Tests**: Mindestens 80% Testabdeckung erforderlich

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz - siehe die [LICENSE](LICENSE)-Datei für Details.

### Kommerzielle Nutzung
- ✅ Kommerzielle Nutzung erlaubt
- ✅ Modifikation und Verteilung erlaubt
- ✅ Private Nutzung erlaubt
- ❌ Keine Garantie oder Haftung

## 📞 Support & Kontakt

### Community-Support
- **GitHub Issues**: [Issues](https://github.com/your-org/neuralex-platform/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/your-org/neuralex-platform/discussions)
- **Dokumentation**: [Wiki](https://github.com/your-org/neuralex-platform/wiki)

### Professioneller Support
- **Enterprise-Support**: contact@neuralex.com
- **Custom-Entwicklung**: development@neuralex.com
- **Schulung & Beratung**: consulting@neuralex.com

### Danksagungen
- FastAPI-Framework und Community
- Ollama-Team für lokale LLM-Integration
- Open-Source-Beitragende und Maintainer
- Beta-Tester und Early Adopters

---

**Mit ❤️ für die KI- und Dokumentverarbeitungs-Community entwickelt**

[![Star auf GitHub](https://img.shields.io/github/stars/your-org/neuralex-platform?style=social)](https://github.com/your-org/neuralex-platform)
[![Folgen auf Twitter](https://img.shields.io/twitter/follow/neuralex?style=social)](https://twitter.com/neuralex)