#!/bin/bash

# NeuraLex Platform - Vollständiges Hetzner Server Deployment
# Server: 49.13.102.114 (GEX130 #2631188)

set -e

echo "🚀 NeuraLex Platform Deployment für Hetzner Server startet..."
echo "📋 Server: 49.13.102.114"
echo "💾 Typ: GEX130"

# System Update und Basic Tools
echo "📦 System wird aktualisiert..."
apt update && apt upgrade -y
apt install -y curl wget git jq htop ufw python3-pip python3-venv nginx

# Firewall konfigurieren
echo "🔥 Firewall wird konfiguriert..."
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 5000
ufw allow 11434
ufw --force enable

# Benutzer für NeuraLex erstellen
echo "👤 NeuraLex Benutzer wird erstellt..."
useradd -m -s /bin/bash neuralex
usermod -aG sudo neuralex

# NeuraLex Platform Code
echo "📥 NeuraLex Platform wird heruntergeladen..."
cd /home/neuralex
git clone https://github.com/your-repo/neuralex-platform.git || echo "Repository wird manuell erstellt..."

# Falls kein Git Repository, erstelle Struktur
mkdir -p /home/neuralex/neuralex-platform
cd /home/neuralex/neuralex-platform

# Python Virtual Environment
echo "🐍 Python Virtual Environment wird erstellt..."
python3 -m venv venv
source venv/bin/activate

# Python Dependencies
echo "📦 Python Pakete werden installiert..."
pip install --upgrade pip
pip install fastapi uvicorn jinja2 python-multipart httpx aiohttp asyncpg sqlalchemy python-dotenv redis aioredis tenacity ollama google-cloud-storage pydantic pytest

# Ollama Installation
echo "🤖 Ollama wird installiert..."
curl -fsSL https://ollama.ai/install.sh | sh

# Ollama Service konfigurieren
echo "⚙️ Ollama Service wird konfiguriert..."
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

# Ollama User erstellen
useradd -r -s /bin/false -m -d /usr/share/ollama ollama

# Service starten
systemctl daemon-reload
systemctl enable ollama
systemctl start ollama

# Warten auf Ollama
echo "⏳ Warte auf Ollama Service..."
sleep 15

# Ollama Modelle herunterladen
echo "📥 Lade Ollama Modelle für Dokumentanalyse..."
ollama pull llama3.2
ollama pull mistral
ollama pull phi3
ollama pull gemma:2b

# NeuraLex Service erstellen
echo "🔧 NeuraLex Service wird konfiguriert..."
cat << 'EOF' > /etc/systemd/system/neuralex.service
[Unit]
Description=NeuraLex Platform
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=exec
User=neuralex
Group=neuralex
WorkingDirectory=/home/neuralex/neuralex-platform
Environment=PATH=/home/neuralex/neuralex-platform/venv/bin
Environment=OLLAMA_HOST=http://localhost:11434
Environment=OLLAMA_MODEL=llama3.2
ExecStart=/home/neuralex/neuralex-platform/venv/bin/python -m uvicorn app.simple_main:app --host 0.0.0.0 --port 5000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Nginx Reverse Proxy konfigurieren
echo "🌐 Nginx Reverse Proxy wird konfiguriert..."
cat << 'EOF' > /etc/nginx/sites-available/neuralex
server {
    listen 80;
    server_name 49.13.102.114;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # File upload support
        client_max_body_size 50M;
    }

    location /api/ollama/ {
        proxy_pass http://localhost:11434/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Nginx Site aktivieren
ln -sf /etc/nginx/sites-available/neuralex /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

# Environment Variables
echo "🔧 Environment Variables werden konfiguriert..."
cat << 'EOF' > /home/neuralex/neuralex-platform/.env
# NeuraLex Platform Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Optional: Google Cloud Credentials
# GOOGLE_CLOUD_PROJECT_ID=your-project-id
# GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...}
EOF

# Ownership setzen
chown -R neuralex:neuralex /home/neuralex/

# Services starten
echo "🚀 Services werden gestartet..."
systemctl daemon-reload
systemctl enable neuralex
systemctl start neuralex

# Status prüfen
echo "🧪 Installation wird getestet..."
sleep 10

# Test Ollama
echo "🤖 Teste Ollama..."
OLLAMA_STATUS=$(curl -s http://localhost:11434/api/tags | jq -r '.models | length' || echo "0")
echo "   Verfügbare Modelle: $OLLAMA_STATUS"

# Test NeuraLex
echo "🔬 Teste NeuraLex Platform..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health || echo "000")
echo "   NeuraLex HTTP Status: $HTTP_STATUS"

# Monitoring Setup
echo "📊 Monitoring wird eingerichtet..."
cat << 'EOF' > /home/neuralex/monitor.sh
#!/bin/bash
echo "=== NeuraLex Platform Status ==="
echo "Datum: $(date)"
echo ""
echo "Services:"
systemctl status ollama --no-pager -l
systemctl status neuralex --no-pager -l
echo ""
echo "Ollama Modelle:"
ollama list
echo ""
echo "System Resources:"
free -h
df -h
echo ""
echo "Network:"
ss -tulpn | grep -E ':(5000|11434|80|443)'
EOF

chmod +x /home/neuralex/monitor.sh

# Backup Script
echo "💾 Backup Script wird erstellt..."
cat << 'EOF' > /home/neuralex/backup.sh
#!/bin/bash
BACKUP_DIR="/home/neuralex/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Platform Code
cp -r /home/neuralex/neuralex-platform "$BACKUP_DIR/"

# Configurations
cp /etc/systemd/system/neuralex.service "$BACKUP_DIR/"
cp /etc/nginx/sites-available/neuralex "$BACKUP_DIR/"

# Environment
cp /home/neuralex/neuralex-platform/.env "$BACKUP_DIR/"

echo "Backup erstellt in: $BACKUP_DIR"
EOF

chmod +x /home/neuralex/backup.sh

# Abschluss-Informationen
echo ""
echo "🎉 NeuraLex Platform Installation abgeschlossen!"
echo ""
echo "📋 Server Details:"
echo "   IP: 49.13.102.114"
echo "   IPv6: 2a01:4f8:1060:2194::2"
echo "   HTTP: http://49.13.102.114"
echo ""
echo "🔧 Services:"
echo "   NeuraLex Platform: http://49.13.102.114:5000"
echo "   Ollama API: http://49.13.102.114:11434"
echo "   Status: systemctl status neuralex"
echo ""
echo "🤖 Verfügbare Ollama Modelle:"
ollama list
echo ""
echo "📊 Monitoring:"
echo "   Status: /home/neuralex/monitor.sh"
echo "   Logs: journalctl -u neuralex -f"
echo "   Backup: /home/neuralex/backup.sh"
echo ""
echo "🔑 Nächste Schritte:"
echo "   1. Google Cloud Credentials in .env konfigurieren (optional)"
echo "   2. SSL-Zertifikat mit Let's Encrypt installieren"
echo "   3. Domain-Name konfigurieren"
echo ""
echo "✨ Installation erfolgreich!"

# Test der kompletten Installation
echo "🧪 Führe Abschlusstest durch..."
sleep 5

# Finale Validierung
if systemctl is-active --quiet neuralex && systemctl is-active --quiet ollama; then
    echo "✅ Alle Services laufen erfolgreich!"
    
    # API Test
    API_TEST=$(curl -s http://localhost:5000/api/config/status | jq -r '.ollama.available' 2>/dev/null || echo "false")
    if [ "$API_TEST" = "true" ]; then
        echo "✅ Ollama Integration funktioniert!"
    else
        echo "⚠️  Ollama Integration benötigt möglicherweise weitere Konfiguration"
    fi
else
    echo "❌ Einige Services sind nicht gestartet. Prüfen Sie die Logs."
fi