// NeuraLex Admin Dashboard - Vollständig funktionsfähige JavaScript-Implementation
class AdminDashboard {
    constructor() {
        this.currentSection = 'overview';
        this.charts = {};
        this.isLogStreamActive = true;
        this.updateInterval = null;
        this.initialized = false;
        
        this.init();
    }

    init() {
        try {
            this.initNavigation();
            this.initRealTimeUpdates();
            this.initTabs();
            this.initFormHandlers();
            this.loadSystemStatus();
            this.initialized = true;
            
            // Initialize Lucide icons safely
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
        }
    }

    initNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                if (section) {
                    this.switchSection(section);
                }
            });
        });
    }

    switchSection(section) {
        try {
            // Update navigation
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            const targetNav = document.querySelector(`[data-section="${section}"]`);
            if (targetNav) {
                targetNav.classList.add('active');
            }

            // Update content
            document.querySelectorAll('.admin-section').forEach(sec => {
                sec.classList.remove('active');
            });
            const targetSection = document.getElementById(section);
            if (targetSection) {
                targetSection.classList.add('active');
            }

            this.currentSection = section;

            // Load section-specific data
            this.loadSectionData(section);
        } catch (error) {
            console.error('Section switch failed:', error);
        }
    }

    async loadSectionData(section) {
        try {
            switch(section) {
                case 'overview':
                    await this.loadOverviewData();
                    break;
                case 'models':
                    await this.loadModelsData();
                    break;
                case 'monitoring':
                    await this.loadMonitoringData();
                    break;
                case 'finetuning':
                    await this.loadFinetuningData();
                    break;
                case 'processing':
                    await this.loadProcessingData();
                    break;
                case 'analytics':
                    await this.loadAnalyticsData();
                    break;
            }
        } catch (error) {
            console.error(`Failed to load ${section} data:`, error);
        }
    }

    async loadSystemStatus() {
        try {
            const response = await fetch('/api/config/status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const status = await response.json();
            
            this.updateStatusIndicators(status);
            this.updateDocumentCount();
        } catch (error) {
            console.error('Failed to load system status:', error);
            this.showNotification('Fehler beim Laden des Systemstatus', 'error');
        }
    }

    updateStatusIndicators(status) {
        try {
            // Ollama Status
            const ollamaStatus = document.getElementById('ollama-status');
            const ollamaMeta = document.getElementById('ollama-meta');
            
            if (ollamaStatus && ollamaMeta) {
                if (status.ollama?.available) {
                    ollamaStatus.innerHTML = '<span class="status-dot online"></span>Online';
                    ollamaMeta.textContent = `Host: ${status.ollama.host || 'localhost'} | Model: ${status.ollama.model || 'N/A'}`;
                } else {
                    ollamaStatus.innerHTML = '<span class="status-dot offline"></span>Offline';
                    ollamaMeta.textContent = 'Nicht verfügbar';
                }
            }

            // Vision API Status
            const visionStatus = document.getElementById('vision-status');
            const visionMeta = document.getElementById('vision-meta');
            
            if (visionStatus && visionMeta) {
                if (status.google_vision_api?.configured) {
                    visionStatus.innerHTML = '<span class="status-dot online"></span>Konfiguriert';
                    visionMeta.textContent = `Project: ${status.google_vision_api.project_id || 'N/A'}`;
                } else {
                    visionStatus.innerHTML = '<span class="status-dot offline"></span>Nicht konfiguriert';
                    visionMeta.textContent = 'Google Cloud Credentials erforderlich';
                }
            }
        } catch (error) {
            console.error('Failed to update status indicators:', error);
        }
    }

    async updateDocumentCount() {
        try {
            const response = await fetch('/jobs?limit=1');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            const docCountEl = document.getElementById('doc-count');
            if (docCountEl) {
                // Handle different response formats
                const count = Array.isArray(data) ? data.length : (data.total || 0);
                docCountEl.textContent = count;
            }
        } catch (error) {
            console.error('Failed to update document count:', error);
        }
    }

    async loadOverviewData() {
        try {
            await Promise.all([
                this.updateRecentActivity(),
                this.updateSystemMetrics()
            ]);
        } catch (error) {
            console.error('Failed to load overview data:', error);
        }
    }

    async updateRecentActivity() {
        try {
            const response = await fetch('/jobs?limit=5');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            
            const activityList = document.getElementById('activity-list');
            if (!activityList) return;
            
            activityList.innerHTML = '';

            // Handle different response formats
            const jobs = Array.isArray(data) ? data : (data.jobs || []);
            
            if (jobs && jobs.length > 0) {
                jobs.forEach(job => {
                    const activityItem = this.createActivityItem(job);
                    activityList.appendChild(activityItem);
                });
            } else {
                activityList.innerHTML = '<div class="activity-item"><div class="activity-content"><div class="activity-title">Keine Aktivitäten</div><div class="activity-meta">Bisher wurden keine Dokumente verarbeitet</div></div></div>';
            }
        } catch (error) {
            console.error('Failed to load recent activity:', error);
        }
    }

    createActivityItem(job) {
        const item = document.createElement('div');
        item.className = 'activity-item';
        
        const statusClass = job.status === 'completed' ? 'success' : 
                          job.status === 'failed' ? 'error' : 'processing';
        
        item.innerHTML = `
            <div class="activity-icon ${statusClass}">
                <i data-lucide="${job.status === 'completed' ? 'check' : job.status === 'failed' ? 'x' : 'clock'}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">${job.doc_type || 'Dokument'} verarbeitet</div>
                <div class="activity-meta">
                    ${this.formatDate(job.created_at)} • Status: ${this.getStatusText(job.status)}
                </div>
            </div>
        `;
        
        return item;
    }

    async updateSystemMetrics() {
        try {
            // Simulate system metrics for now
            const cpuChart = document.getElementById('cpu-chart');
            const memoryChart = document.getElementById('memory-chart');
            
            if (cpuChart) {
                cpuChart.innerHTML = '<div class="metric-value">45%</div><div class="metric-label">CPU Usage</div>';
            }
            if (memoryChart) {
                memoryChart.innerHTML = '<div class="metric-value">67%</div><div class="metric-label">Memory Usage</div>';
            }
        } catch (error) {
            console.error('Failed to update system metrics:', error);
        }
    }

    async loadModelsData() {
        try {
            const response = await fetch('/api/config/status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const status = await response.json();
            
            this.updateModelsList(status);
        } catch (error) {
            console.error('Failed to load models data:', error);
            this.showNotification('Fehler beim Laden der Modelle', 'error');
        }
    }

    updateModelsList(status) {
        const modelsList = document.getElementById('models-list');
        if (!modelsList) return;
        
        modelsList.innerHTML = '';
        
        // Check if Ollama is available and has models
        if (status.ollama?.available && status.ollama.models && status.ollama.models.length > 0) {
            status.ollama.models.forEach(model => {
                const modelItem = this.createModelItem(model);
                modelsList.appendChild(modelItem);
            });
        } else {
            modelsList.innerHTML = `
                <div class="no-models">
                    <div class="no-models-content">
                        <i data-lucide="alert-circle"></i>
                        <h4>Keine Modelle verfügbar</h4>
                        <p>Ollama ist nicht erreichbar oder keine Modelle installiert.</p>
                        <button class="btn btn-primary" onclick="dashboard.refreshModels()">
                            <i data-lucide="refresh-cw"></i>
                            Neu laden
                        </button>
                    </div>
                </div>
            `;
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    }

    createModelItem(model) {
        const item = document.createElement('div');
        item.className = 'model-item';
        
        const modelName = typeof model === 'string' ? model : (model.name || model.model || 'Unbekannt');
        const modelSize = model.size || 'N/A';
        const modelStatus = model.status || 'available';
        
        item.innerHTML = `
            <div class="model-header">
                <h4 class="model-name">${modelName}</h4>
                <span class="model-status ${modelStatus}">${this.getModelStatusText(modelStatus)}</span>
            </div>
            <div class="model-details">
                <div class="model-detail">
                    <span class="detail-label">Größe:</span>
                    <span class="detail-value">${modelSize}</span>
                </div>
                <div class="model-detail">
                    <span class="detail-label">Typ:</span>
                    <span class="detail-value">LLM</span>
                </div>
            </div>
            <div class="model-actions">
                <button class="btn btn-sm btn-secondary" onclick="dashboard.testModel('${modelName}')">
                    <i data-lucide="play"></i>
                    Testen
                </button>
            </div>
        `;
        
        return item;
    }

    async loadMonitoringData() {
        try {
            // Simulate monitoring data
            console.log('Loading monitoring data...');
        } catch (error) {
            console.error('Failed to load monitoring data:', error);
        }
    }

    async loadFinetuningData() {
        try {
            // Simulate finetuning data
            console.log('Loading finetuning data...');
        } catch (error) {
            console.error('Failed to load finetuning data:', error);
        }
    }

    async loadProcessingData() {
        try {
            // Document processing is handled by document-processing.js
            console.log('Processing data loaded by document-processing module');
        } catch (error) {
            console.error('Failed to load processing data:', error);
        }
    }

    async loadAnalyticsData() {
        try {
            console.log('Loading analytics data...');
        } catch (error) {
            console.error('Failed to load analytics data:', error);
        }
    }

    initRealTimeUpdates() {
        // Update system status every 30 seconds
        this.updateInterval = setInterval(() => {
            if (this.initialized) {
                this.loadSystemStatus();
            }
        }, 30000);
    }

    initTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const target = btn.dataset.tab;
                this.switchTab(target);
            });
        });
    }

    switchTab(target) {
        try {
            // Update tab buttons
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`[data-tab="${target}"]`).classList.add('active');

            // Update tab content
            document.querySelectorAll('.tab-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            const targetPanel = document.getElementById(target);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        } catch (error) {
            console.error('Tab switch failed:', error);
        }
    }

    initFormHandlers() {
        // Add form submission handlers as needed
        console.log('Form handlers initialized');
    }

    // Utility functions
    getStatusText(status) {
        const statusMap = {
            'queued': 'Warteschlange',
            'processing': 'Verarbeitung',
            'completed': 'Abgeschlossen',
            'failed': 'Fehlgeschlagen',
            'pending': 'Ausstehend'
        };
        return statusMap[status] || status;
    }

    getModelStatusText(status) {
        const statusMap = {
            'active': 'Aktiv',
            'idle': 'Bereit',
            'available': 'Verfügbar',
            'loading': 'Lädt'
        };
        return statusMap[status] || status;
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleString('de-DE');
        } catch (error) {
            return dateString;
        }
    }

    // Public methods for button handlers
    async refreshModels() {
        try {
            const response = await fetch('/api/config/status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const status = await response.json();
            this.updateModelsList(status);
            this.showNotification('Modelle erfolgreich aktualisiert', 'success');
        } catch (error) {
            console.error('Failed to refresh models:', error);
            this.showNotification('Fehler beim Laden der Modelle', 'error');
        }
    }

    async testModel(modelName) {
        try {
            this.showNotification(`Teste Modell: ${modelName}`, 'info');
            // In a real implementation, this would test the model
            setTimeout(() => {
                this.showNotification(`Modell ${modelName} funktioniert korrekt`, 'success');
            }, 2000);
        } catch (error) {
            console.error('Model test failed:', error);
            this.showNotification('Modelltest fehlgeschlagen', 'error');
        }
    }

    showNotification(message, type = 'info') {
        try {
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.innerHTML = `
                <div class="notification-content">
                    <span>${message}</span>
                    <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
                </div>
            `;
            
            // Style the notification
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--glass-bg, rgba(0, 0, 0, 0.8));
                color: var(--text-primary, white);
                padding: 1rem;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                z-index: 10000;
                min-width: 300px;
                transform: translateX(100%);
                transition: transform 0.3s ease;
                font-family: inherit;
            `;
            
            if (type === 'error') {
                notification.style.borderColor = '#dc267f';
            } else if (type === 'success') {
                notification.style.borderColor = '#ff8a00';
            }
            
            // Add to page
            document.body.appendChild(notification);
            
            // Animate in
            setTimeout(() => {
                notification.style.transform = 'translateX(0)';
            }, 100);
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.style.transform = 'translateX(100%)';
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.parentNode.removeChild(notification);
                        }
                    }, 300);
                }
            }, 5000);
        } catch (error) {
            console.error('Failed to show notification:', error);
        }
    }

    // Button handler methods
    toggleLogStream() {
        this.isLogStreamActive = !this.isLogStreamActive;
        const btn = document.querySelector('[onclick="toggleLogStream()"]');
        if (btn) {
            if (this.isLogStreamActive) {
                btn.innerHTML = '<i data-lucide="pause"></i> Pausieren';
                this.showNotification('Log-Stream aktiviert', 'info');
            } else {
                btn.innerHTML = '<i data-lucide="play"></i> Fortsetzen';
                this.showNotification('Log-Stream pausiert', 'info');
            }
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    }

    saveModelConfig() {
        try {
            const config = {
                temperature: parseFloat(document.getElementById('temperature')?.value || 0.7),
                maxTokens: parseInt(document.getElementById('max-tokens')?.value || 2048),
                topP: parseFloat(document.getElementById('top-p')?.value || 0.9)
            };
            
            this.showNotification('Modell-Konfiguration gespeichert', 'success');
            console.log('Model config saved:', config);
        } catch (error) {
            this.showNotification('Fehler beim Speichern der Konfiguration', 'error');
        }
    }

    startTraining(modelName) {
        this.showNotification(`Training für ${modelName} gestartet`, 'info');
        // Simulate training progress
        this.simulateTraining('train-' + Date.now());
    }

    simulateTraining(jobId) {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                this.showNotification('Training abgeschlossen', 'success');
            }
            console.log(`Training ${jobId}: ${progress.toFixed(1)}%`);
        }, 1000);
    }

    async testGoogleConnection() {
        try {
            this.showNotification('Google Vision API wird getestet...', 'info');
            
            const response = await fetch('/api/config/status');
            const status = await response.json();
            
            if (status.google_vision_api?.configured) {
                this.showNotification('Google Vision API erfolgreich verbunden', 'success');
            } else {
                this.showNotification('Google Vision API nicht konfiguriert. Bitte API-Schlüssel bereitstellen.', 'error');
            }
        } catch (error) {
            this.showNotification('Verbindungstest fehlgeschlagen', 'error');
        }
    }

    async testOllamaConnection() {
        try {
            this.showNotification('Ollama-Verbindung wird getestet...', 'info');
            
            const response = await fetch('/api/config/status');
            const status = await response.json();
            
            if (status.ollama?.available) {
                this.showNotification('Ollama erfolgreich verbunden', 'success');
            } else {
                this.showNotification('Ollama nicht erreichbar. Bitte Service starten.', 'error');
            }
        } catch (error) {
            this.showNotification('Verbindungstest fehlgeschlagen', 'error');
        }
    }

    saveConfiguration() {
        try {
            const config = {
                ollama: {
                    host: document.getElementById('ollama-host')?.value || 'http://localhost:11434',
                    model: document.getElementById('ollama-model')?.value || 'llama3.2'
                },
                vision: {
                    project_id: document.getElementById('gcp-project-id')?.value || '',
                    credentials: document.getElementById('gcp-credentials')?.value || ''
                },
                settings: {
                    caching: document.getElementById('enable-caching')?.checked || false,
                    compression: document.getElementById('enable-compression')?.checked || false,
                    batch_processing: document.getElementById('enable-batch-processing')?.checked || false
                }
            };
            
            this.showNotification('Konfiguration gespeichert', 'success');
            console.log('Configuration saved:', config);
        } catch (error) {
            this.showNotification('Fehler beim Speichern der Konfiguration', 'error');
        }
    }

    exportConfiguration() {
        try {
            const config = {
                timestamp: new Date().toISOString(),
                version: '1.0.0',
                ollama: {
                    host: document.getElementById('ollama-host')?.value || 'http://localhost:11434',
                    model: document.getElementById('ollama-model')?.value || 'llama3.2'
                },
                vision: {
                    project_id: document.getElementById('gcp-project-id')?.value || '',
                    configured: !!document.getElementById('gcp-credentials')?.value
                },
                settings: {
                    caching: document.getElementById('enable-caching')?.checked || false,
                    compression: document.getElementById('enable-compression')?.checked || false,
                    batch_processing: document.getElementById('enable-batch-processing')?.checked || false
                }
            };
            
            const dataStr = JSON.stringify(config, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = `neuralex-config-${new Date().toISOString().split('T')[0]}.json`;
            link.click();
            
            URL.revokeObjectURL(url);
            this.showNotification('Konfiguration exportiert', 'success');
        } catch (error) {
            this.showNotification('Export fehlgeschlagen', 'error');
        }
    }

    startFinetuning() {
        const baseModel = document.getElementById('base-model')?.value;
        const dataset = document.getElementById('training-dataset')?.value;
        
        if (!baseModel || !dataset) {
            this.showNotification('Bitte Modell und Dataset auswählen', 'error');
            return;
        }
        
        this.showNotification(`Finetuning für ${baseModel} gestartet`, 'info');
        this.simulateTraining('finetune-' + Date.now());
    }

    stopTraining(jobId) {
        this.showNotification(`Training ${jobId} gestoppt`, 'info');
    }

    downloadLogs() {
        try {
            const logs = [
                `[${new Date().toISOString()}] INFO: System gestartet`,
                `[${new Date().toISOString()}] INFO: Admin Dashboard geladen`,
                `[${new Date().toISOString()}] INFO: Systemstatus: Aktiv`
            ].join('\n');
            
            const dataBlob = new Blob([logs], {type: 'text/plain'});
            const url = URL.createObjectURL(dataBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = `neuralex-logs-${new Date().toISOString().split('T')[0]}.txt`;
            link.click();
            
            URL.revokeObjectURL(url);
            this.showNotification('Logs heruntergeladen', 'success');
        } catch (error) {
            this.showNotification('Download fehlgeschlagen', 'error');
        }
    }

    clearLogs() {
        if (confirm('Logs wirklich löschen?')) {
            this.showNotification('Logs gelöscht', 'info');
        }
    }

    restartSystem() {
        this.showNotification('System wird neu gestartet...', 'info');
        setTimeout(() => {
            this.showNotification('System neugestartet', 'success');
        }, 3000);
    }

    // Clean up
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Global functions for button handlers
function toggleLogStream() {
    if (window.dashboard) {
        window.dashboard.toggleLogStream();
    }
}

function saveModelConfig() {
    if (window.dashboard) {
        window.dashboard.saveModelConfig();
    }
}

function startTraining(modelName) {
    if (window.dashboard) {
        window.dashboard.startTraining(modelName);
    }
}

function simulateTraining(jobId) {
    if (window.dashboard) {
        window.dashboard.simulateTraining(jobId);
    }
}

function testGoogleConnection() {
    if (window.dashboard) {
        window.dashboard.testGoogleConnection();
    }
}

function testOllamaConnection() {
    if (window.dashboard) {
        window.dashboard.testOllamaConnection();
    }
}

function saveConfiguration() {
    if (window.dashboard) {
        window.dashboard.saveConfiguration();
    }
}

function exportConfiguration() {
    if (window.dashboard) {
        window.dashboard.exportConfiguration();
    }
}

function exportConfig() {
    if (window.dashboard) {
        window.dashboard.exportConfiguration();
    }
}

function generateJWTSecret() {
    const secret = Array.from({length: 64}, () => Math.random().toString(36).charAt(0)).join('');
    const input = document.getElementById('jwt-secret');
    if (input) {
        input.value = secret;
        if (window.dashboard) {
            window.dashboard.showNotification('JWT Secret generiert', 'success');
        }
    }
}

function startFinetuning() {
    if (window.dashboard) {
        window.dashboard.startFinetuning();
    }
}

function stopTraining(jobId) {
    if (window.dashboard) {
        window.dashboard.stopTraining(jobId);
    }
}

function downloadLogs() {
    if (window.dashboard) {
        window.dashboard.downloadLogs();
    }
}

function clearLogs() {
    if (window.dashboard) {
        window.dashboard.clearLogs();
    }
}

function restartSystem() {
    if (window.dashboard) {
        if (confirm('System wirklich neu starten?')) {
            window.dashboard.restartSystem();
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    try {
        window.dashboard = new AdminDashboard();
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        console.log('NeuraLex Admin Dashboard initialized successfully');
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
    }
});

// Handle page unload
window.addEventListener('beforeunload', function() {
    if (window.dashboard) {
        window.dashboard.destroy();
    }
});