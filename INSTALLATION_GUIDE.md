# NeuraLex Platform - Hetzner Server Installation

## Schritt 1: Code auf den Server übertragen

### Option A: Über SSH direkt kopieren
```bash
# Von Ihrem lokalen Rechner aus:
scp -r . root@49.13.102.114:/root/neuralex-platform/
```

### Option B: Git Repository verwenden
```bash
# Auf dem Server:
ssh root@49.13.102.114
cd /root
git clone https://github.com/IHR-REPO/neuralex-platform.git
```

### Option C: Manueller Upload
1. Packen Sie alle Dateien in eine ZIP-Datei
2. Laden Sie über SCP oder SFTP hoch
3. Entpacken auf dem Server

## Schritt 2: Installation ausführen

```bash
# Auf dem Hetzner Server:
ssh root@49.13.102.114
# Passwort: hLcWF35MdsBC7k6tJCNGwJ95W6jrjYEs

cd /root/neuralex-platform
chmod +x deploy_hetzner.sh
./deploy_hetzner.sh
```

## Schritt 3: Passwort ändern (Sicherheit)
```bash
passwd root
# Neues sicheres Passwort eingeben
```

## Schritt 4: Zugriff testen

Die Platform ist dann verfügbar unter:
- **http://49.13.102.114** (Hauptseite)
- **http://49.13.102.114:5000** (Direkte API)

## Status überprüfen

```bash
# Service Status
systemctl status neuralex
systemctl status ollama

# Monitoring Script
/home/neuralex/monitor.sh

# Logs anzeigen
journalctl -u neuralex -f
```

## Benötigte Server-Ressourcen

Ihr GEX130 Server sollte ausreichend sein:
- Ollama Modelle: ~15-20GB Speicher
- RAM: Mindestens 8GB für Ollama
- CPU: Alle verfügbaren Kerne werden genutzt

## Google Cloud Integration (Optional)

Falls Sie OCR verwenden möchten, bearbeiten Sie:
```bash
nano /home/neuralex/neuralex-platform/.env
```

Und fügen Sie hinzu:
```
GOOGLE_CLOUD_PROJECT_ID=ihr-projekt-id
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...}
```

## Troubleshooting

Falls Probleme auftreten:
1. Logs prüfen: `journalctl -u neuralex -f`
2. Ollama Status: `ollama list`
3. Ports prüfen: `ss -tulpn | grep -E ':(5000|11434)'`
4. Services neustarten: `systemctl restart neuralex ollama`

## Backup

Regelmäßige Backups erstellen:
```bash
/home/neuralex/backup.sh
```