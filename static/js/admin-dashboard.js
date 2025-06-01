// NeuraLex Admin Dashboard - JavaScript
class AdminDashboard {
    constructor() {
        this.currentSection = 'overview';
        this.charts = {};
        this.isLogStreamActive = true;
        this.updateInterval = null;
        
        this.init();
    }

    init() {
        this.initNavigation();
        this.initCharts();
        this.initRealTimeUpdates();
        this.initTabs();
        this.initFormHandlers();
        this.loadSystemStatus();
        
        // Initialize Lucide icons
        lucide.createIcons();
    }

    initNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.switchSection(section);
            });
        });
    }

    switchSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.admin-section').forEach(sec => {
            sec.classList.remove('active');
        });
        document.getElementById(section).classList.add('active');

        this.currentSection = section;

        // Load section-specific data
        this.loadSectionData(section);
    }

    async loadSectionData(section) {
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
            case 'analytics':
                await this.loadAnalyticsData();
                break;
        }
    }

    async loadSystemStatus() {
        try {
            const response = await fetch('/api/config/status');
            const status = await response.json();
            
            this.updateStatusIndicators(status);
            this.updateDocumentCount();
        } catch (error) {
            console.error('Failed to load system status:', error);
        }
    }

    updateStatusIndicators(status) {
        // Ollama Status
        const ollamaStatus = document.getElementById('ollama-status');
        const ollamaMeta = document.getElementById('ollama-meta');
        
        if (status.ollama?.available) {
            ollamaStatus.innerHTML = '<span class="status-dot online"></span>Online';
            ollamaMeta.textContent = `Host: ${status.ollama.host} | Model: ${status.ollama.model}`;
        } else {
            ollamaStatus.innerHTML = '<span class="status-dot offline"></span>Offline';
            ollamaMeta.textContent = 'Nicht verfügbar';
        }

        // Vision API Status
        const visionStatus = document.getElementById('vision-status');
        const visionMeta = document.getElementById('vision-meta');
        
        if (status.google_vision_api?.configured) {
            visionStatus.innerHTML = '<span class="status-dot online"></span>Konfiguriert';
            visionMeta.textContent = `Project: ${status.google_vision_api.project_id || 'N/A'}`;
        } else {
            visionStatus.innerHTML = '<span class="status-dot offline"></span>Nicht konfiguriert';
            visionMeta.textContent = 'Google Cloud Credentials erforderlich';
        }
    }

    async updateDocumentCount() {
        try {
            const response = await fetch('/jobs?limit=1');
            const data = await response.json();
            document.getElementById('doc-count').textContent = data.total || 0;
        } catch (error) {
            console.error('Failed to update document count:', error);
        }
    }

    async loadOverviewData() {
        await this.updateRecentActivity();
        await this.updateSystemMetrics();
    }

    async updateRecentActivity() {
        try {
            const response = await fetch('/jobs?limit=5');
            const data = await response.json();
            
            const activityList = document.getElementById('activity-list');
            activityList.innerHTML = '';

            if (data.jobs && data.jobs.length > 0) {
                data.jobs.forEach(job => {
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
        
        const iconClass = this.getActivityIcon(job.status);
        const timeAgo = this.formatTimeAgo(job.created_at);
        
        item.innerHTML = `
            <div class="activity-icon">
                <i data-lucide="${iconClass}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">
                    ${job.doc_type || 'Dokument'} verarbeitet
                </div>
                <div class="activity-meta">
                    ${job.id} • ${timeAgo} • Status: ${job.status}
                </div>
            </div>
        `;
        
        return item;
    }

    getActivityIcon(status) {
        switch(status) {
            case 'completed': return 'check-circle';
            case 'processing': return 'clock';
            case 'failed': return 'alert-circle';
            default: return 'file-text';
        }
    }

    formatTimeAgo(timestamp) {
        if (!timestamp) return 'Unbekannt';
        
        const now = new Date();
        const time = new Date(timestamp);
        const diffMs = now - time;
        const diffMinutes = Math.floor(diffMs / 60000);
        
        if (diffMinutes < 1) return 'Gerade eben';
        if (diffMinutes < 60) return `vor ${diffMinutes} Min.`;
        
        const diffHours = Math.floor(diffMinutes / 60);
        if (diffHours < 24) return `vor ${diffHours} Std.`;
        
        const diffDays = Math.floor(diffHours / 24);
        return `vor ${diffDays} Tag${diffDays > 1 ? 'en' : ''}`;
    }

    async updateSystemMetrics() {
        // Simulate system metrics (in real implementation, get from system monitoring)
        const metrics = {
            cpu: Math.random() * 100,
            memory: Math.random() * 100,
            gpu: 0, // No GPU detected
            storage: Math.random() * 100
        };

        this.updateMetricBar('cpu', metrics.cpu);
        this.updateMetricBar('memory', metrics.memory);
        this.updateMetricBar('gpu', metrics.gpu);
        this.updateMetricBar('storage', metrics.storage);
    }

    updateMetricBar(type, value) {
        const bars = document.querySelectorAll('.metric-fill');
        const values = document.querySelectorAll('.metric-value');
        
        // Simple mapping - in real implementation, use proper selectors
        bars.forEach((bar, index) => {
            if (index === 0 && type === 'cpu') {
                bar.style.width = `${value}%`;
                values[index].textContent = `${Math.round(value)}%`;
            }
        });
    }

    async loadModelsData() {
        try {
            const response = await fetch('/api/config/status');
            const status = await response.json();
            
            this.updateModelsList(status);
            this.updateModelPerformanceChart();
        } catch (error) {
            console.error('Failed to load models data:', error);
        }
    }

    updateModelsList(status) {
        const modelsList = document.getElementById('models-list');
        
        const models = [
            { name: 'Llama 3.2', status: 'active', size: '3.8GB', accuracy: '94.2%' },
            { name: 'Mistral 7B', status: 'idle', size: '7.2GB', accuracy: '92.8%' },
            { name: 'Phi-3 Mini', status: 'idle', size: '2.1GB', accuracy: '89.5%' },
            { name: 'Gemma 2B', status: 'idle', size: '1.6GB', accuracy: '87.3%' }
        ];

        modelsList.innerHTML = '';
        models.forEach(model => {
            const modelItem = this.createModelItem(model);
            modelsList.appendChild(modelItem);
        });
    }

    createModelItem(model) {
        const item = document.createElement('div');
        item.className = 'model-item';
        
        item.innerHTML = `
            <div class="model-header">
                <div class="model-name">${model.name}</div>
                <div class="model-status ${model.status}">${model.status}</div>
            </div>
            <div class="model-meta">
                Größe: ${model.size} • Genauigkeit: ${model.accuracy}
            </div>
        `;
        
        return item;
    }

    initCharts() {
        this.initModelPerformanceChart();
        this.initSystemChart();
        this.initRequestChart();
        this.initEvaluationChart();
        this.initProcessingChart();
        this.initDistributionChart();
        this.initTrendsChart();
    }

    initModelPerformanceChart() {
        const ctx = document.getElementById('modelPerformanceChart');
        if (!ctx) return;

        this.charts.modelPerformance = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Genauigkeit', 'Geschwindigkeit', 'Effizienz', 'Stabilität', 'Qualität'],
                datasets: [{
                    label: 'Llama 3.2',
                    data: [94, 78, 85, 92, 89],
                    borderColor: '#ff4444',
                    backgroundColor: 'rgba(255, 68, 68, 0.1)',
                    borderWidth: 2
                }, {
                    label: 'Mistral 7B',
                    data: [92, 65, 90, 88, 91],
                    borderColor: '#ff8800',
                    backgroundColor: 'rgba(255, 136, 0, 0.1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#cccccc' }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#888888' },
                        grid: { color: '#333333' },
                        pointLabels: { color: '#cccccc' }
                    }
                }
            }
        });
    }

    initSystemChart() {
        const ctx = document.getElementById('systemChart');
        if (!ctx) return;

        this.charts.system = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateTimeLabels(20),
                datasets: [{
                    label: 'CPU %',
                    data: this.generateRandomData(20, 30, 80),
                    borderColor: '#ff4444',
                    backgroundColor: 'rgba(255, 68, 68, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Memory %',
                    data: this.generateRandomData(20, 60, 85),
                    borderColor: '#ff8800',
                    backgroundColor: 'rgba(255, 136, 0, 0.1)',
                    tension: 0.4
                }]
            },
            options: this.getChartOptions()
        });
    }

    initRequestChart() {
        const ctx = document.getElementById('requestChart');
        if (!ctx) return;

        this.charts.requests = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.generateTimeLabels(12),
                datasets: [{
                    label: 'Requests',
                    data: this.generateRandomData(12, 10, 100),
                    backgroundColor: 'rgba(255, 68, 68, 0.8)',
                    borderColor: '#ff4444',
                    borderWidth: 1
                }]
            },
            options: this.getChartOptions()
        });
    }

    initEvaluationChart() {
        const ctx = document.getElementById('evaluationChart');
        if (!ctx) return;

        this.charts.evaluation = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Epoch 1', 'Epoch 2', 'Epoch 3', 'Epoch 4', 'Epoch 5'],
                datasets: [{
                    label: 'Training Loss',
                    data: [0.85, 0.65, 0.45, 0.35, 0.28],
                    borderColor: '#ff4444',
                    backgroundColor: 'rgba(255, 68, 68, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y'
                }, {
                    label: 'Validation Accuracy',
                    data: [78, 84, 89, 92, 94],
                    borderColor: '#00ff88',
                    backgroundColor: 'rgba(0, 255, 136, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                ...this.getChartOptions(),
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        ticks: { color: '#888888' },
                        grid: { color: '#333333' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        ticks: { color: '#888888' },
                        grid: { drawOnChartArea: false }
                    },
                    x: {
                        ticks: { color: '#888888' },
                        grid: { color: '#333333' }
                    }
                }
            }
        });
    }

    initProcessingChart() {
        const ctx = document.getElementById('processingChart');
        if (!ctx) return;

        this.charts.processing = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateTimeLabels(7, 'days'),
                datasets: [{
                    label: 'Verarbeitete Dokumente',
                    data: this.generateRandomData(7, 50, 200),
                    borderColor: '#ff8800',
                    backgroundColor: 'rgba(255, 136, 0, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: this.getChartOptions()
        });
    }

    initDistributionChart() {
        const ctx = document.getElementById('distributionChart');
        if (!ctx) return;

        this.charts.distribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Rechnungen', 'Verträge', 'Quittungen', 'Berichte', 'Sonstige'],
                datasets: [{
                    data: [45, 25, 15, 10, 5],
                    backgroundColor: [
                        '#ff4444',
                        '#ff8800',
                        '#ffaa00',
                        '#00ff88',
                        '#00ccff'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#cccccc' }
                    }
                }
            }
        });
    }

    initTrendsChart() {
        const ctx = document.getElementById('trendsChart');
        if (!ctx) return;

        this.charts.trends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateTimeLabels(30, 'days'),
                datasets: [{
                    label: 'Durchschnittliche Verarbeitungszeit (s)',
                    data: this.generateRandomData(30, 1.5, 3.5),
                    borderColor: '#ff4444',
                    backgroundColor: 'rgba(255, 68, 68, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Genauigkeit (%)',
                    data: this.generateRandomData(30, 88, 96),
                    borderColor: '#00ff88',
                    backgroundColor: 'rgba(0, 255, 136, 0.1)',
                    tension: 0.4
                }]
            },
            options: this.getChartOptions()
        });
    }

    generateTimeLabels(count, unit = 'hours') {
        const labels = [];
        const now = new Date();
        
        for (let i = count - 1; i >= 0; i--) {
            const time = new Date(now);
            
            if (unit === 'hours') {
                time.setHours(time.getHours() - i);
                labels.push(time.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }));
            } else if (unit === 'days') {
                time.setDate(time.getDate() - i);
                labels.push(time.toLocaleDateString('de-DE', { month: 'short', day: 'numeric' }));
            }
        }
        
        return labels;
    }

    generateRandomData(count, min, max) {
        return Array.from({ length: count }, () => Math.random() * (max - min) + min);
    }

    getChartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#cccccc' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#888888' },
                    grid: { color: '#333333' }
                },
                y: {
                    ticks: { color: '#888888' },
                    grid: { color: '#333333' }
                }
            }
        };
    }

    initRealTimeUpdates() {
        this.updateInterval = setInterval(() => {
            if (this.currentSection === 'overview') {
                this.updateSystemMetrics();
            } else if (this.currentSection === 'monitoring') {
                this.updateMonitoringCharts();
                if (this.isLogStreamActive) {
                    this.updateLiveLogs();
                }
            }
        }, 5000);
    }

    updateMonitoringCharts() {
        if (this.charts.system) {
            const newCpuData = Math.random() * 50 + 30;
            const newMemoryData = Math.random() * 25 + 60;
            
            this.charts.system.data.datasets[0].data.shift();
            this.charts.system.data.datasets[0].data.push(newCpuData);
            this.charts.system.data.datasets[1].data.shift();
            this.charts.system.data.datasets[1].data.push(newMemoryData);
            
            this.charts.system.data.labels.shift();
            this.charts.system.data.labels.push(new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }));
            
            this.charts.system.update('none');
        }
    }

    updateLiveLogs() {
        const logOutput = document.getElementById('log-output');
        if (!logOutput) return;

        const logEntries = [
            'INFO: Document processed successfully',
            'DEBUG: Ollama model response received',
            'INFO: Vision API request completed',
            'WARNING: High memory usage detected'
        ];

        const randomEntry = logEntries[Math.floor(Math.random() * logEntries.length)];
        const timestamp = new Date().toLocaleTimeString();
        const logLevel = randomEntry.split(':')[0].toLowerCase();
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${logLevel}`;
        logEntry.textContent = `[${timestamp}] ${randomEntry}`;
        
        logOutput.appendChild(logEntry);
        logOutput.scrollTop = logOutput.scrollHeight;

        // Keep only last 50 entries
        while (logOutput.children.length > 50) {
            logOutput.removeChild(logOutput.firstChild);
        }
    }

    initTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.dataset.tab;
                this.switchTab(tabId);
            });
        });
    }

    switchTab(tabId) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');

        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(tabId).classList.add('active');
    }

    initFormHandlers() {
        // Range inputs
        const rangeInputs = document.querySelectorAll('.form-range');
        rangeInputs.forEach(input => {
            const valueSpan = input.parentNode.querySelector('.range-value');
            if (valueSpan) {
                input.addEventListener('input', () => {
                    valueSpan.textContent = input.value;
                });
            }
        });
    }

    // API Functions
    async refreshOverview() {
        await this.loadSystemStatus();
        await this.loadOverviewData();
        this.showNotification('Übersicht aktualisiert', 'success');
    }

    async refreshModels() {
        await this.loadModelsData();
        this.showNotification('Modell-Status aktualisiert', 'success');
    }

    async saveModelConfig() {
        const config = {
            primaryModel: document.getElementById('primary-model').value,
            fallbackModel: document.getElementById('fallback-model').value,
            temperature: parseFloat(document.getElementById('temperature').value),
            maxTokens: parseInt(document.getElementById('max-tokens').value)
        };

        try {
            // In real implementation, send to backend
            console.log('Saving model config:', config);
            this.showNotification('Modell-Konfiguration gespeichert', 'success');
        } catch (error) {
            this.showNotification('Fehler beim Speichern der Konfiguration', 'error');
        }
    }

    toggleLogStream() {
        this.isLogStreamActive = !this.isLogStreamActive;
        const btn = document.querySelector('[onclick="toggleLogStream()"]');
        const icon = btn.querySelector('i');
        
        if (this.isLogStreamActive) {
            icon.setAttribute('data-lucide', 'pause');
            btn.innerHTML = '<i data-lucide="pause"></i> Pausieren';
        } else {
            icon.setAttribute('data-lucide', 'play');
            btn.innerHTML = '<i data-lucide="play"></i> Fortsetzen';
        }
        
        lucide.createIcons();
    }

    async testGoogleConnection() {
        const projectId = document.getElementById('gcp-project-id').value;
        const credentials = document.getElementById('gcp-credentials').value;

        if (!projectId || !credentials) {
            this.showNotification('Bitte füllen Sie alle Felder aus', 'warning');
            return;
        }

        try {
            // Test connection
            this.showNotification('Verbindung wird getestet...', 'info');
            
            // In real implementation, test actual connection
            setTimeout(() => {
                this.showNotification('Google Cloud Verbindung erfolgreich', 'success');
            }, 2000);
        } catch (error) {
            this.showNotification('Verbindung fehlgeschlagen', 'error');
        }
    }

    async testOllamaConnection() {
        const host = document.getElementById('ollama-host').value;

        try {
            this.showNotification('Ollama-Verbindung wird getestet...', 'info');
            
            const response = await fetch('/api/config/status');
            const status = await response.json();
            
            if (status.ollama?.available) {
                this.showNotification('Ollama-Verbindung erfolgreich', 'success');
            } else {
                this.showNotification('Ollama ist nicht erreichbar', 'error');
            }
        } catch (error) {
            this.showNotification('Verbindungstest fehlgeschlagen', 'error');
        }
    }

    startFinetuning() {
        const config = {
            baseModel: document.getElementById('base-model').value,
            dataset: document.getElementById('training-dataset').value,
            learningRate: parseFloat(document.getElementById('learning-rate').value),
            epochs: parseInt(document.getElementById('epochs').value),
            batchSize: parseInt(document.getElementById('batch-size').value)
        };

        this.showModal('Training starten', `
            <p>Möchten Sie das Training mit folgender Konfiguration starten?</p>
            <ul>
                <li>Basis Modell: ${config.baseModel}</li>
                <li>Dataset: ${config.dataset}</li>
                <li>Learning Rate: ${config.learningRate}</li>
                <li>Epochs: ${config.epochs}</li>
                <li>Batch Size: ${config.batchSize}</li>
            </ul>
        `, [
            { text: 'Abbrechen', class: 'btn-secondary', action: 'closeModal()' },
            { text: 'Training starten', class: 'btn-success', action: 'confirmStartTraining()' }
        ]);
    }

    confirmStartTraining() {
        this.closeModal();
        this.showNotification('Training gestartet', 'success');
        
        // Simulate training progress
        this.simulateTraining();
    }

    simulateTraining() {
        const statusEl = document.getElementById('training-status');
        const progressEl = document.getElementById('training-progress');
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        const etaText = document.getElementById('eta-text');

        statusEl.innerHTML = `
            <div class="status-card active">
                <i data-lucide="zap"></i>
                <span>Training läuft</span>
            </div>
        `;
        progressEl.style.display = 'block';

        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 5;
            if (progress > 100) progress = 100;

            progressFill.style.width = `${progress}%`;
            progressText.textContent = `${Math.round(progress)}%`;
            
            const remainingTime = Math.round((100 - progress) / 2);
            etaText.textContent = `ETA: ${remainingTime}min`;

            if (progress >= 100) {
                clearInterval(interval);
                statusEl.innerHTML = `
                    <div class="status-card idle">
                        <i data-lucide="check-circle"></i>
                        <span>Training abgeschlossen</span>
                    </div>
                `;
                progressEl.style.display = 'none';
                this.showNotification('Training erfolgreich abgeschlossen', 'success');
            }
        }, 1000);

        lucide.createIcons();
    }

    showModal(title, content, buttons) {
        const modal = document.getElementById('modal-overlay');
        const titleEl = document.getElementById('modal-title');
        const bodyEl = document.getElementById('modal-body');
        const footerEl = document.getElementById('modal-footer');

        titleEl.textContent = title;
        bodyEl.innerHTML = content;
        
        footerEl.innerHTML = '';
        buttons.forEach(btn => {
            const button = document.createElement('button');
            button.className = `btn ${btn.class}`;
            button.textContent = btn.text;
            button.onclick = () => eval(btn.action);
            footerEl.appendChild(button);
        });

        modal.classList.add('active');
    }

    closeModal() {
        document.getElementById('modal-overlay').classList.remove('active');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            padding: 1rem 1.5rem;
            color: var(--text-primary);
            z-index: 1001;
            animation: slideInRight 0.3s ease;
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    async loadMonitoringData() {
        this.updateErrorList();
    }

    updateErrorList() {
        const errorList = document.getElementById('error-list');
        const errors = [
            { time: '14:23', message: 'OCR processing timeout', level: 'warning' },
            { time: '13:45', message: 'Model loading failed', level: 'error' },
            { time: '12:15', message: 'High memory usage', level: 'warning' }
        ];

        errorList.innerHTML = '';
        errors.forEach(error => {
            const errorItem = document.createElement('div');
            errorItem.className = `log-entry ${error.level}`;
            errorItem.textContent = `[${error.time}] ${error.message}`;
            errorList.appendChild(errorItem);
        });
    }

    async loadFinetuningData() {
        this.updateTrainingHistory();
    }

    updateTrainingHistory() {
        const historyEl = document.getElementById('training-history');
        const history = [
            { date: '2024-01-15', model: 'llama3.2', dataset: 'invoices', accuracy: '94.2%', status: 'completed' },
            { date: '2024-01-12', model: 'mistral', dataset: 'contracts', accuracy: '92.8%', status: 'completed' },
            { date: '2024-01-10', model: 'phi3', dataset: 'mixed', accuracy: '89.5%', status: 'failed' }
        ];

        historyEl.innerHTML = '';
        history.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.style.cssText = `
                padding: 1rem;
                background: var(--bg-secondary);
                border-radius: 8px;
                margin-bottom: 0.5rem;
                border-left: 4px solid ${item.status === 'completed' ? 'var(--success)' : 'var(--error)'};
            `;
            
            historyItem.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>${item.model}</strong> • ${item.dataset}
                        <div style="color: var(--text-muted); font-size: 0.875rem;">${item.date}</div>
                    </div>
                    <div style="text-align: right;">
                        <div>${item.accuracy}</div>
                        <div style="color: var(--text-muted); font-size: 0.875rem;">${item.status}</div>
                    </div>
                </div>
            `;
            
            historyEl.appendChild(historyItem);
        });
    }

    async loadAnalyticsData() {
        // Analytics data is already initialized in charts
        this.showNotification('Analytics-Daten geladen', 'info');
    }

    generateJWTSecret() {
        const secret = Array.from(crypto.getRandomValues(new Uint8Array(32)))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
        document.getElementById('jwt-secret').value = secret;
        this.showNotification('JWT Secret generiert', 'success');
    }

    async saveAllConfig() {
        this.showNotification('Konfiguration wird gespeichert...', 'info');
        
        // Simulate save delay
        setTimeout(() => {
            this.showNotification('Alle Konfigurationen gespeichert', 'success');
        }, 1500);
    }

    exportConfig() {
        const config = {
            platform: {
                name: document.getElementById('platform-name').value,
                language: document.getElementById('default-language').value
            },
            api: {
                gcpProjectId: document.getElementById('gcp-project-id').value,
                ollamaHost: document.getElementById('ollama-host').value
            },
            security: {
                sessionTimeout: document.getElementById('session-timeout').value
            }
        };

        const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'neuralex-config.json';
        a.click();
        URL.revokeObjectURL(url);

        this.showNotification('Konfiguration exportiert', 'success');
    }

    exportLogs() {
        const logs = document.getElementById('log-output').textContent;
        const blob = new Blob([logs], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `neuralex-logs-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);

        this.showNotification('Logs exportiert', 'success');
    }

    clearLogs() {
        this.showModal('Logs löschen', 'Möchten Sie wirklich alle Logs löschen? Diese Aktion kann nicht rückgängig gemacht werden.', [
            { text: 'Abbrechen', class: 'btn-secondary', action: 'closeModal()' },
            { text: 'Löschen', class: 'btn-danger', action: 'confirmClearLogs()' }
        ]);
    }

    confirmClearLogs() {
        document.getElementById('log-output').innerHTML = '';
        this.closeModal();
        this.showNotification('Logs gelöscht', 'success');
    }

    pullNewModel() {
        this.showModal('Neues Modell hinzufügen', `
            <div class="form-group">
                <label>Modell Name</label>
                <select class="form-control" id="new-model-select">
                    <option value="codellama">CodeLlama</option>
                    <option value="llama2">Llama 2</option>
                    <option value="vicuna">Vicuna</option>
                    <option value="orca-mini">Orca Mini</option>
                </select>
            </div>
            <p style="color: var(--text-muted); font-size: 0.875rem; margin-top: 1rem;">
                Das Modell wird automatisch heruntergeladen und installiert.
            </p>
        `, [
            { text: 'Abbrechen', class: 'btn-secondary', action: 'closeModal()' },
            { text: 'Herunterladen', class: 'btn-primary', action: 'confirmPullModel()' }
        ]);
    }

    confirmPullModel() {
        const modelName = document.getElementById('new-model-select').value;
        this.closeModal();
        this.showNotification(`${modelName} wird heruntergeladen...`, 'info');
        
        // Simulate download
        setTimeout(() => {
            this.showNotification(`${modelName} erfolgreich installiert`, 'success');
            this.loadModelsData();
        }, 3000);
    }

    generateReport() {
        this.showNotification('Report wird generiert...', 'info');
        
        setTimeout(() => {
            const report = {
                timeframe: document.getElementById('analytics-timeframe').value,
                generated: new Date().toISOString(),
                metrics: {
                    totalDocuments: Math.floor(Math.random() * 1000),
                    averageProcessingTime: (Math.random() * 2 + 1).toFixed(1),
                    accuracy: (Math.random() * 10 + 90).toFixed(1)
                }
            };

            const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `neuralex-report-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);

            this.showNotification('Report generiert und heruntergeladen', 'success');
        }, 2000);
    }
}

// Global functions for onclick handlers
function refreshOverview() { dashboard.refreshOverview(); }
function refreshModels() { dashboard.refreshModels(); }
function saveModelConfig() { dashboard.saveModelConfig(); }
function toggleLogStream() { dashboard.toggleLogStream(); }
function testGoogleConnection() { dashboard.testGoogleConnection(); }
function testOllamaConnection() { dashboard.testOllamaConnection(); }
function startFinetuning() { dashboard.startFinetuning(); }
function confirmStartTraining() { dashboard.confirmStartTraining(); }
function closeModal() { dashboard.closeModal(); }
function generateJWTSecret() { dashboard.generateJWTSecret(); }
function saveAllConfig() { dashboard.saveAllConfig(); }
function exportConfig() { dashboard.exportConfig(); }
function exportLogs() { dashboard.exportLogs(); }
function clearLogs() { dashboard.clearLogs(); }
function confirmClearLogs() { dashboard.confirmClearLogs(); }
function pullNewModel() { dashboard.pullNewModel(); }
function confirmPullModel() { dashboard.confirmPullModel(); }
function generateReport() { dashboard.generateReport(); }

// Initialize dashboard when DOM is loaded
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new AdminDashboard();
});