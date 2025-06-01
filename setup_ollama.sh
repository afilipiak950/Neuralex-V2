#!/bin/bash

# NeuraLex Platform - Ollama Setup für Hetzner Server
# Installiert und konfiguriert Ollama mit geeigneten Modellen für Dokumentanalyse

set -e

echo "🚀 NeuraLex Platform - Ollama Setup startet..."

# System Updates
echo "📦 System wird aktualisiert..."
apt update && apt upgrade -y

# Ollama installieren
echo "🤖 Ollama wird installiert..."
curl -fsSL https://ollama.ai/install.sh | sh

# Ollama Service starten
echo "🔧 Ollama Service wird gestartet..."
systemctl start ollama
systemctl enable ollama

# Warten bis Ollama bereit ist
echo "⏳ Warte auf Ollama Service..."
sleep 10

# Modelle für Dokumentanalyse herunterladen
echo "📥 Lade optimale Modelle für Dokumentanalyse..."

# Llama 3.2 (3B) - Gut für Klassifizierung und strukturierte Extraktion
echo "📋 Lade Llama 3.2 (3B) für Dokumentklassifizierung..."
ollama pull llama3.2

# Mistral 7B - Exzellent für JSON-Extraktion
echo "🔍 Lade Mistral 7B für strukturierte Datenextraktion..."
ollama pull mistral

# Phi-3 Mini - Schnell und effizient für kleinere Aufgaben
echo "⚡ Lade Phi-3 Mini für schnelle Verarbeitung..."
ollama pull phi3

# Gemma 2B - Sehr ressourcenschonend
echo "💎 Lade Gemma 2B als Fallback-Modell..."
ollama pull gemma:2b

# Environment-Variablen für NeuraLex setzen
echo "🔧 Konfiguriere Umgebungsvariablen..."

cat << 'EOF' >> /etc/environment
# NeuraLex Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_FALLBACK_MODEL=gemma:2b
EOF

# Systemd Service für optimale Performance
echo "⚙️ Konfiguriere Ollama Service für optimale Performance..."

cat << 'EOF' > /etc/systemd/system/ollama.service
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_MODELS=/usr/share/ollama/.ollama/models"

[Install]
WantedBy=default.target
EOF

# Service neu laden und starten
systemctl daemon-reload
systemctl restart ollama

# Teste Ollama Installation
echo "🧪 Teste Ollama Installation..."
sleep 5

# Test mit einfacher Anfrage
TEST_RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2",
    "prompt": "Klassifiziere dieses Dokument: RECHNUNG Nr. 2024-001",
    "stream": false,
    "options": {"temperature": 0.1}
  }' | jq -r '.response // "ERROR"')

if [[ "$TEST_RESPONSE" != "ERROR" && "$TEST_RESPONSE" != "" ]]; then
    echo "✅ Ollama Installation erfolgreich!"
    echo "📊 Test-Antwort: $TEST_RESPONSE"
else
    echo "❌ Ollama Test fehlgeschlagen"
    exit 1
fi

# Status-Übersicht
echo ""
echo "🎉 Setup abgeschlossen!"
echo "📋 Installierte Modelle:"
ollama list

echo ""
echo "🔧 Konfiguration:"
echo "   Ollama Host: http://localhost:11434"
echo "   Primäres Modell: llama3.2"
echo "   Fallback Modell: gemma:2b"
echo ""
echo "🚀 NeuraLex Platform kann jetzt OCR-Dokumente analysieren:"
echo "   • Dokumenttyp-Klassifizierung (INVOICE, CONTRACT, etc.)"
echo "   • Event-Type-Extraktion (PAYMENT_DUE, CONTRACT_SIGNED, etc.)"
echo "   • Strukturierte Datenextraktion (JSON-Format)"
echo ""
echo "💡 Nützliche Befehle:"
echo "   systemctl status ollama    # Service Status"
echo "   ollama list               # Verfügbare Modelle"
echo "   ollama ps                 # Laufende Modelle"

echo "✨ Setup erfolgreich abgeschlossen!"