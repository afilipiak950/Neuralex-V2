# NeuraLex Platform - Umfassende Dokumentation

## Überblick

NeuraLex ist eine fortschrittliche KI-gestützte Dokumentenverarbeitungsplattform, die lokale Ollama-Modelle für intelligente Dokumentenanalyse und -klassifizierung verwendet. Die Plattform bietet ein vollständiges Admin-Dashboard für Überwachung, Modellverwaltung und Systemkonfiguration.

## Technische Architektur

### Backend-Stack
- **Framework**: FastAPI (Python 3.11+)
- **Datenbank**: PostgreSQL mit SQLAlchemy ORM
- **Caching/Queuing**: Redis für Job-Warteschlangen
- **ML-Engine**: Ollama (lokale LLM-Integration)
- **Webserver**: Uvicorn ASGI-Server
- **OCR**: Google Vision API (optional)

### Frontend-Stack
- **UI-Framework**: Vanilla JavaScript mit Lucide Icons
- **Styling**: CSS3 mit Glass Morphism Design
- **Farbschema**: Schwarz/Rot/Orange Gradient
- **Responsive**: Mobile-First Design
- **Templates**: Jinja2 Template Engine

### Systemkomponenten

#### 1. Kern-APIs (/app/simple_main.py)
```python
# Haupt-Endpunkte:
GET  /health              # Systemstatus
POST /ingest              # Dokumentenaufnahme
GET  /jobs/{job_id}       # Job-Status abrufen
GET  /jobs                # Alle Jobs auflisten
POST /analyze             # Ollama-Dokumentenanalyse
POST /ocr                 # OCR-Verarbeitung
GET  /search              # Dokumentensuche
```

#### 2. Admin-Dashboard (/admin)
```
Umfassendes 7-Bereiche Dashboard:
├── Übersicht           # System-Metrics und Status
├── Modelle             # Ollama-Modellverwaltung
├── Monitoring          # Echtzeit-Systemüberwachung
├── Finetuning          # Modell-Training und -anpassung
├── Dokumentverarbeitung # Upload und Verarbeitung
├── Analytics           # Verarbeitungsstatistiken
└── Konfiguration       # Systemeinstellungen
```

## Funktionalitäten im Detail

### 1. Dokumentenverarbeitung
- **Upload-Methoden**: 
  - Direkte Datei-Uploads (PDF, PNG, JPG)
  - GCS URI-basierte Verarbeitung
  - Text-Eingabe über Webformular
- **OCR-Integration**: Google Vision API für Texterkennung
- **ML-Analyse**: Ollama-Modelle für Inhaltskategorisierung
- **Ergebnisspeicherung**: Strukturierte Datenbankablage

### 2. Ollama-Integration
```python
# Modell-Konfiguration:
- Standard-Modell: llama3.2
- Host: http://localhost:11434
- Unterstützte Operationen:
  * Dokumentklassifizierung
  * Event-Type-Erkennung
  * Inhaltsextraktion
  * Strukturierte JSON-Ausgabe
```

### 3. Job-Verarbeitungssystem
- **Asynchrone Verarbeitung**: Background Tasks mit FastAPI
- **Redis-Queuing**: Warteschlangenverwaltung für Dokumente
- **Status-Tracking**: Real-time Job-Status-Updates
- **Fehlerbehandlung**: Robuste Retry-Logik

### 4. Admin-Dashboard Features

#### Übersicht
- **System-Metriken**: CPU, RAM, Festplatten-Nutzung
- **Dienste-Status**: Ollama, Google Vision API, PostgreSQL
- **Aktuelle Jobs**: Live-Übersicht laufender Verarbeitungen
- **Fehler-Monitoring**: Kritische Systemfehler

#### Modellverwaltung
- **Ollama-Status**: Verfügbare Modelle anzeigen
- **Modell-Parameter**: Temperature, Max Tokens, Top-P
- **Performance-Metriken**: Antwortzeiten, Genauigkeit
- **Modell-Tests**: Verbindungstests und Validierung

#### Monitoring
- **Echtzeit-Logs**: Live-Log-Stream mit Filterung
- **Performance-Grafiken**: Historische Systemdaten
- **Fehler-Tracking**: Detaillierte Fehlerverfolgung
- **Benachrichtigungen**: Status-Updates und Warnungen

#### Finetuning
- **Training-Jobs**: Modell-Anpassung starten/stoppen
- **Dataset-Management**: Training-Daten verwalten
- **Progress-Tracking**: Training-Fortschritt überwachen
- **Modell-Export**: Trainierte Modelle exportieren

#### Dokumentverarbeitung
- **Batch-Upload**: Mehrere Dateien gleichzeitig
- **OCR-Pipeline**: Automatische Texterkennung
- **Klassifizierung**: KI-gestützte Kategorisierung
- **Ergebnis-Export**: Verarbeitete Daten exportieren

#### Analytics
- **Verarbeitungsstatistiken**: Erfolgsraten, Durchsatz
- **Dokumenttyp-Verteilung**: Kategorisierungs-Übersicht
- **Performance-Trends**: Zeitbasierte Analysen
- **Custom-Reports**: Anpassbare Berichte

#### Konfiguration
- **Ollama-Einstellungen**: Host, Modell, Parameter
- **Google Cloud**: Vision API Konfiguration
- **System-Optimierungen**: Caching, Kompression
- **Sicherheit**: JWT-Token, API-Schlüssel

## Installation und Setup

### Voraussetzungen
```bash
# System-Anforderungen:
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Ollama (optional, für ML-Features)
- Google Cloud Account (optional, für OCR)
```

### Lokale Installation
```bash
# 1. Repository klonen
git clone [repository-url]
cd neuralex-platform

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Umgebungsvariablen setzen
export DATABASE_URL="postgresql://user:pass@localhost/neuralex"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"

# 4. Datenbank initialisieren
python -c "from app.db import create_tables; create_tables()"

# 5. Server starten
python -m uvicorn app.simple_main:app --host 0.0.0.0 --port 5000
```

### Docker-Setup
```dockerfile
# Containerisierte Bereitstellung verfügbar
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.simple_main:app", "--host", "0.0.0.0", "--port", "5000"]
```

## API-Dokumentation

### Dokumentenaufnahme
```http
POST /ingest
Content-Type: application/json

{
  "gcs_uri": "gs://bucket/document.pdf",  # Optional
  "payload": {                            # Optional
    "content": "Dokumenttext...",
    "metadata": {"type": "invoice"}
  }
}

Response:
{
  "job_id": "uuid-string",
  "status": "processing",
  "message": "Document queued for processing"
}
```

### Ollama-Analyse
```http
POST /analyze
Content-Type: application/json

{
  "text": "Zu analysierender Text",
  "model": "llama3.2",
  "task": "classification"
}

Response:
{
  "analysis": {
    "document_type": "invoice",
    "event_type": "payment",
    "confidence": 0.95,
    "extracted_data": {...}
  }
}
```

### Job-Status
```http
GET /jobs/{job_id}

Response:
{
  "job_id": "uuid",
  "status": "completed|processing|failed",
  "result": {...},
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:05:00Z"
}
```

## Datenbank-Schema

### Jobs-Tabelle
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status VARCHAR(50) NOT NULL,
    input_data JSONB,
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Dokumente-Tabelle
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    document_type VARCHAR(100),
    event_type VARCHAR(100),
    content TEXT,
    metadata JSONB,
    processed_at TIMESTAMP DEFAULT NOW()
);
```

## Sicherheit und Authentifizierung

### JWT-Token-System
- **Admin-Zugang**: JWT-basierte Authentifizierung
- **API-Schlüssel**: Sichere API-Endpunkt-Zugriffe
- **Rate-Limiting**: Anfrage-Begrenzung pro Client
- **CORS-Konfiguration**: Cross-Origin-Anfragen kontrolliert

### Datenschutz
- **Verschlüsselung**: Sensitive Daten verschlüsselt gespeichert
- **Audit-Logs**: Vollständige Aktivitätsverfolgung
- **Datenlöschung**: Automatische Bereinigung alter Daten
- **DSGVO-Konformität**: Datenschutz-konforme Verarbeitung

## Performance-Optimierungen

### Caching-Strategien
- **Redis-Caching**: Häufige Anfragen zwischenspeichern
- **Ergebnis-Cache**: ML-Analyse-Ergebnisse cachen
- **Session-Management**: Benutzer-Sessions optimiert
- **Asset-Caching**: Statische Dateien komprimiert

### Skalierbarkeit
- **Horizontale Skalierung**: Multi-Instance-Deployment
- **Load-Balancing**: Anfragen-Verteilung
- **Database-Sharding**: Datenbank-Partitionierung
- **Async-Processing**: Non-blocking Verarbeitung

## Monitoring und Logging

### System-Metriken
- **CPU/RAM-Überwachung**: Ressourcen-Nutzung
- **Disk-I/O**: Speicher-Performance
- **Network-Traffic**: Netzwerk-Auslastung
- **Application-Metrics**: Custom-Metriken

### Log-Management
- **Strukturierte Logs**: JSON-formatierte Einträge
- **Log-Level**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Rotation**: Automatische Log-Bereinigung
- **Aggregation**: Zentrale Log-Sammlung

## Deployment-Optionen

### Lokaler Server
- **Development**: Lokale Entwicklungsumgebung
- **Testing**: Isolierte Test-Instanzen
- **Demo**: Präsentations-Setup

### Cloud-Deployment
- **Hetzner**: Produktions-Server (49.13.102.114)
- **AWS/GCP**: Cloud-Provider-Integration
- **Kubernetes**: Container-Orchestrierung
- **Docker**: Containerisierte Bereitstellung

### CI/CD-Pipeline
```yaml
# GitHub Actions Workflow
name: Deploy NeuraLex
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Hetzner
        run: ./deploy_hetzner.sh
```

## Troubleshooting

### Häufige Probleme

#### Ollama-Verbindung
```bash
# Problem: Ollama nicht erreichbar
# Lösung: Ollama-Service starten
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull llama3.2
```

#### PostgreSQL-Verbindung
```bash
# Problem: Datenbankverbindung fehlgeschlagen
# Lösung: Verbindungsstring prüfen
export DATABASE_URL="postgresql://user:password@localhost:5432/database"
```

#### Google Vision API
```bash
# Problem: OCR-Service nicht verfügbar
# Lösung: API-Schlüssel konfigurieren
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### Debug-Modi
```python
# Entwicklung mit Debug-Modus
uvicorn app.simple_main:app --reload --log-level debug

# Produktions-Logging
uvicorn app.simple_main:app --log-config logging.conf
```

## Entwicklung und Beitrag

### Code-Struktur
```
neuralex-platform/
├── app/
│   ├── __init__.py         # Paket-Initialisierung
│   ├── simple_main.py      # Haupt-FastAPI-App
│   ├── admin/              # Admin-Dashboard-Module
│   ├── db/                 # Datenbank-Models
│   └── ml_client/          # ML-Integration
├── static/                 # Frontend-Assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript-Module
│   └── images/            # Grafik-Assets
├── templates/             # Jinja2-Templates
├── tests/                 # Test-Suites
└── docs/                  # Dokumentation
```

### Entwicklungsrichtlinien
- **Code-Style**: PEP 8 für Python, ESLint für JavaScript
- **Testing**: Pytest für Backend, Jest für Frontend
- **Documentation**: Docstrings und README-Updates
- **Git-Workflow**: Feature-Branches mit Pull-Requests

### Testing-Framework
```bash
# Backend-Tests
pytest tests/ -v --cov=app

# Frontend-Tests
npm test

# Integration-Tests
pytest tests/test_integration.py

# Performance-Tests
pytest tests/test_performance.py --benchmark
```

## Lizenz und Support

### Open-Source-Lizenz
- **MIT-Lizenz**: Freie kommerzielle Nutzung
- **Community-Support**: GitHub Issues und Discussions
- **Dokumentation**: Umfassende Wiki verfügbar

### Enterprise-Support
- **Professionelle Beratung**: Implementation und Skalierung
- **Custom-Development**: Anpassungen und Erweiterungen
- **SLA-Support**: 24/7 Verfügbarkeit und Wartung

## Roadmap und Zukunft

### Version 2.0 (Q2 2024)
- [ ] Multi-Tenant-Architektur
- [ ] Advanced ML-Pipeline
- [ ] Real-time Collaboration
- [ ] Mobile App Integration

### Version 3.0 (Q4 2024)
- [ ] Federated Learning
- [ ] Blockchain Integration
- [ ] Advanced Analytics Dashboard
- [ ] AI-powered Insights

---

**NeuraLex Platform** - Entwickelt für moderne Dokumentenverarbeitung mit KI-Integration.
Besuchen Sie das Admin-Dashboard unter: http://localhost:5000/admin