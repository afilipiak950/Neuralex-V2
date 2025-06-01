# NeuraLex Platform - Hetzner Server Deployment

## Architektur-Übersicht

Die NeuraLex Platform nutzt eine hybride Architektur für optimale Dokumentverarbeitung:

```
Dokument Upload → OCR (Google Vision API) → Ollama Analyse → Strukturierte Daten
```

## Server-Setup

### 1. Ollama Installation
```bash
# Auf Ihrem Hetzner Server ausführen:
sudo ./setup_ollama.sh
```

### 2. NeuraLex Platform starten
```bash
# Mit Ollama auf localhost:
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama3.2

python -m uvicorn app.simple_main:app --host 0.0.0.0 --port 5000
```

## API-Endpunkte

### Vollständige Dokumentverarbeitung
```bash
POST /api/process/complete
# Upload: Bild-Datei
# Output: OCR + Ollama-Analyse mit Doc-Type und Event-Type
```

### Nur Ollama-Analyse
```bash
POST /api/ollama/analyze
# Input: OCR-JSON-Daten
# Output: Klassifizierung und strukturierte Datenextraktion
```

### Konfigurationsstatus
```bash
GET /api/config/status
# Zeigt Verfügbarkeit von Ollama und Google Vision API
```

## Dokumenttypen und Event-Types

### Unterstützte Dokumenttypen:
- **INVOICE** - Rechnungen
- **CONTRACT** - Verträge
- **RECEIPT** - Quittungen
- **LETTER** - Briefe
- **FORM** - Formulare
- **CERTIFICATE** - Zertifikate
- **REPORT** - Berichte
- **OTHER** - Sonstige

### Event-Types pro Dokumenttyp:

**INVOICE:**
- PAYMENT_DUE
- PAYMENT_RECEIVED
- INVOICE_SENT
- OVERDUE

**CONTRACT:**
- CONTRACT_SIGNED
- CONTRACT_EXPIRED
- CONTRACT_RENEWED
- CONTRACT_TERMINATED

**RECEIPT:**
- PAYMENT_CONFIRMED
- EXPENSE_RECORDED
- REFUND_ISSUED

## Strukturierte Datenextraktion

### Rechnung (INVOICE)
```json
{
  "invoice_number": "INV-2024-001",
  "date": "2024-01-15",
  "due_date": "2024-02-15",
  "total_amount": "2023.00",
  "currency": "EUR",
  "vendor_name": "Musterfirma GmbH",
  "customer_name": "Max Mustermann"
}
```

### Vertrag (CONTRACT)
```json
{
  "contract_type": "Dienstleistungsvertrag",
  "parties": ["Firma A", "Firma B"],
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "value": "50000.00"
}
```

## Performance-Optimierung

### Empfohlene Hetzner Server-Konfiguration:
- **CPU:** Mindestens 4 Cores (8+ empfohlen für Ollama)
- **RAM:** Mindestens 8GB (16GB+ für große Modelle)
- **Storage:** SSD für schnelle Modell-Zugriffe

### Modell-Auswahl nach Use-Case:
- **llama3.2** - Beste Genauigkeit für komplexe Dokumente
- **mistral** - Optimal für JSON-Extraktion
- **phi3** - Schnellste Verarbeitung
- **gemma:2b** - Minimaler Ressourcenverbrauch

## Monitoring und Logs

### Ollama Status prüfen:
```bash
systemctl status ollama
ollama ps  # Zeigt aktive Modelle
```

### NeuraLex Logs:
```bash
# Application Logs
tail -f /var/log/neuralex.log

# Performance Monitoring
htop  # CPU/Memory Usage
```

## Skalierung

### Horizontal:
- Load Balancer vor mehreren NeuraLex-Instanzen
- Shared Storage für Dokument-Cache

### Vertikal:
- Größere Ollama-Modelle für bessere Genauigkeit
- GPU-Beschleunigung für Ollama (falls verfügbar)

## Sicherheit

### API-Schutz:
```bash
# Rate Limiting implementieren
# JWT-Token für API-Zugriff
# HTTPS für Production
```

### Daten-Sicherheit:
- Dokumente werden nur temporär verarbeitet
- Keine persistente Speicherung von Inhalten
- Google Cloud Credentials sicher verwalten

## Troubleshooting

### Ollama reagiert nicht:
```bash
sudo systemctl restart ollama
ollama pull llama3.2  # Modell neu laden
```

### Hoher Speicherverbrauch:
```bash
# Kleineres Modell verwenden
export OLLAMA_MODEL=gemma:2b
```

### OCR-Fehler:
- Google Cloud Credentials prüfen
- Vision API Quotas kontrollieren
- Bildqualität verbessern