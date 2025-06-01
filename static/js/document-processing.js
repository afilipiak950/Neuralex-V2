/**
 * Document Processing Module for Admin Dashboard
 */

class DocumentProcessor {
    constructor() {
        this.documents = [];
        this.selectedDocument = null;
        this.isUploading = false;
    }

    async init() {
        this.setupUpload();
        this.setupFilters();
        await this.loadDocuments();
        this.startPolling();
    }

    async loadDocuments() {
        try {
            const response = await fetch('/jobs?limit=1000');
            const jobs = await response.json();
            this.documents = jobs;
            this.renderDocumentGrid(jobs);
        } catch (error) {
            console.error('Failed to load documents:', error);
            this.showError('Fehler beim Laden der Dokumente');
        }
    }

    renderDocumentGrid(documents) {
        const grid = document.getElementById('document-grid');
        if (!grid) return;

        if (!documents || documents.length === 0) {
            grid.innerHTML = `
                <div class="no-documents">
                    <i data-lucide="file-text"></i>
                    <span>Keine Dokumente vorhanden</span>
                    <p>Laden Sie ein Dokument hoch, um zu beginnen.</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        grid.innerHTML = documents.map(doc => `
            <div class="document-item" data-job-id="${doc.id}" onclick="documentProcessor.selectDocument('${doc.id}')">
                <div class="document-header">
                    <span class="document-type">${doc.doc_type || 'UNKNOWN'}</span>
                    <span class="document-status ${doc.status}">${this.getStatusText(doc.status)}</span>
                </div>
                <div class="document-meta">
                    <div><strong>ID:</strong> ${doc.id.substring(0, 8)}...</div>
                    <div><strong>Erstellt:</strong> ${this.formatDate(doc.created_at)}</div>
                    ${doc.confidence ? `<div><strong>Konfidenz:</strong> ${(doc.confidence * 100).toFixed(1)}%</div>` : ''}
                    ${doc.processing_time ? `<div><strong>Zeit:</strong> ${doc.processing_time.toFixed(2)}s</div>` : ''}
                </div>
            </div>
        `).join('');

        if (window.lucide) lucide.createIcons();
    }

    selectDocument(jobId) {
        // Remove previous selection
        document.querySelectorAll('.document-item').forEach(item => {
            item.classList.remove('selected');
        });

        // Add selection to clicked item
        const selectedItem = document.querySelector(`[data-job-id="${jobId}"]`);
        if (selectedItem) {
            selectedItem.classList.add('selected');
        }

        this.selectedDocument = jobId;
        this.loadDocumentDetails(jobId);
    }

    async loadDocumentDetails(jobId) {
        try {
            const response = await fetch(`/jobs/${jobId}`);
            const job = await response.json();
            this.renderDocumentDetails(job);
        } catch (error) {
            console.error('Failed to load document details:', error);
            this.renderDocumentDetails(null);
        }
    }

    renderDocumentDetails(job) {
        const detailsContent = document.getElementById('document-details');
        if (!detailsContent) return;

        if (!job) {
            detailsContent.innerHTML = `
                <div class="no-selection">
                    <i data-lucide="alert-circle"></i>
                    <span>Fehler beim Laden der Dokumentdetails</span>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        detailsContent.innerHTML = `
            <div class="document-details">
                <div class="detail-section">
                    <h4>Grundinformationen</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="detail-label">Job-ID</span>
                            <span class="detail-value">${job.id}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Status</span>
                            <span class="detail-value">
                                <span class="document-status ${job.status}">${this.getStatusText(job.status)}</span>
                            </span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Dokumenttyp</span>
                            <span class="detail-value">${job.doc_type || 'Unbekannt'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Event-Typ</span>
                            <span class="detail-value">${job.event_type || 'Unbekannt'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Konfidenz</span>
                            <span class="detail-value">${job.confidence ? (job.confidence * 100).toFixed(1) + '%' : 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Verarbeitungszeit</span>
                            <span class="detail-value">${job.processing_time ? job.processing_time.toFixed(2) + 's' : 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Erstellt</span>
                            <span class="detail-value">${this.formatDate(job.created_at)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Modell</span>
                            <span class="detail-value">${job.model_version || 'N/A'}</span>
                        </div>
                    </div>
                </div>
                
                ${job.result ? `
                <div class="detail-section">
                    <h4>Analyseergebnis</h4>
                    <div class="detail-content">
                        <pre class="json-content">${JSON.stringify(job.result, null, 2)}</pre>
                    </div>
                </div>
                ` : ''}
                
                ${job.error ? `
                <div class="detail-section">
                    <h4>Fehlerinformationen</h4>
                    <div class="detail-content">
                        <div class="error-message">${job.error}</div>
                    </div>
                </div>
                ` : ''}

                ${job.gcs_uri ? `
                <div class="detail-section">
                    <h4>Quellfile</h4>
                    <div class="detail-content">
                        <div class="file-info">
                            <span class="detail-label">GCS URI:</span>
                            <span class="detail-value">${job.gcs_uri}</span>
                        </div>
                    </div>
                </div>
                ` : ''}
            </div>
        `;

        if (window.lucide) lucide.createIcons();
    }

    setupUpload() {
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');

        if (!uploadArea || !fileInput) return;

        // Click to upload
        uploadArea.addEventListener('click', () => {
            if (!this.isUploading) {
                fileInput.click();
            }
        });

        // File selection
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            if (!this.isUploading) {
                uploadArea.classList.add('drag-over');
            }
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            if (e.dataTransfer.files.length > 0 && !this.isUploading) {
                this.handleFileUpload(e.dataTransfer.files[0]);
            }
        });
    }

    async handleFileUpload(file) {
        if (this.isUploading) return;

        try {
            this.isUploading = true;
            const formData = new FormData();
            formData.append('file', file);

            // Get processing method
            const processingMethod = document.querySelector('input[name="processing-method"]:checked')?.value || 'complete';

            // Show upload progress
            this.showUploadProgress(file.name);

            let endpoint;
            switch (processingMethod) {
                case 'vision-only':
                    endpoint = '/api/ocr';
                    break;
                case 'ollama-only':
                    endpoint = '/api/analyze';
                    break;
                case 'complete':
                default:
                    endpoint = '/api/process/complete';
                    break;
            }

            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showUploadSuccess(result);
                // Refresh document list after 2 seconds
                setTimeout(() => {
                    this.loadDocuments();
                }, 2000);
            } else {
                this.showUploadError(result.detail || 'Upload fehlgeschlagen');
            }

        } catch (error) {
            console.error('Upload failed:', error);
            this.showUploadError('Upload fehlgeschlagen: ' + error.message);
        } finally {
            this.isUploading = false;
        }
    }

    showUploadProgress(filename) {
        const queue = document.getElementById('processing-queue');
        if (!queue) return;

        queue.innerHTML = `
            <div class="processing-item">
                <div class="processing-header">
                    <span class="processing-name">${filename}</span>
                    <span class="processing-status processing">Hochladen...</span>
                </div>
                <div class="processing-progress">
                    <div class="progress-bar" style="width: 50%;"></div>
                </div>
                <div class="processing-meta">
                    <span>Status: Upload läuft</span>
                    <span>Verarbeitung startet...</span>
                </div>
            </div>
        `;
    }

    showUploadSuccess(result) {
        const queue = document.getElementById('processing-queue');
        if (!queue) return;

        queue.innerHTML = `
            <div class="processing-item">
                <div class="processing-header">
                    <span class="processing-name">Upload erfolgreich</span>
                    <span class="processing-status completed">Abgeschlossen</span>
                </div>
                <div class="processing-progress">
                    <div class="progress-bar" style="width: 100%;"></div>
                </div>
                <div class="processing-meta">
                    <span>Job-ID: ${result.job_id || 'N/A'}</span>
                    <span>Status: ${result.status || 'queued'}</span>
                </div>
            </div>
        `;

        // Clear after 3 seconds
        setTimeout(() => {
            this.clearProcessingQueue();
        }, 3000);
    }

    showUploadError(message) {
        const queue = document.getElementById('processing-queue');
        if (!queue) return;

        queue.innerHTML = `
            <div class="processing-item">
                <div class="processing-header">
                    <span class="processing-name">Upload fehlgeschlagen</span>
                    <span class="processing-status failed">Fehler</span>
                </div>
                <div class="processing-meta">
                    <span>Fehler: ${message}</span>
                </div>
            </div>
        `;

        // Clear after 5 seconds
        setTimeout(() => {
            this.clearProcessingQueue();
        }, 5000);
    }

    clearProcessingQueue() {
        const queue = document.getElementById('processing-queue');
        if (queue) {
            queue.innerHTML = `
                <div class="queue-empty">
                    <i data-lucide="inbox"></i>
                    <span>Keine aktiven Verarbeitungen</span>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
        }
    }

    setupFilters() {
        const searchInput = document.getElementById('doc-search');
        const typeFilter = document.getElementById('doc-type-filter');
        const statusFilter = document.getElementById('doc-status-filter');

        if (searchInput) {
            searchInput.addEventListener('input', () => {
                this.applyFilters();
            });
        }

        if (typeFilter) {
            typeFilter.addEventListener('change', () => {
                this.applyFilters();
            });
        }

        if (statusFilter) {
            statusFilter.addEventListener('change', () => {
                this.applyFilters();
            });
        }
    }

    applyFilters() {
        const searchTerm = document.getElementById('doc-search')?.value.toLowerCase() || '';
        const typeFilter = document.getElementById('doc-type-filter')?.value || 'all';
        const statusFilter = document.getElementById('doc-status-filter')?.value || 'all';

        let filtered = this.documents.filter(doc => {
            const matchesSearch = !searchTerm || 
                doc.id.toLowerCase().includes(searchTerm) ||
                (doc.doc_type && doc.doc_type.toLowerCase().includes(searchTerm)) ||
                (doc.event_type && doc.event_type.toLowerCase().includes(searchTerm));

            const matchesType = typeFilter === 'all' || doc.doc_type === typeFilter;
            const matchesStatus = statusFilter === 'all' || doc.status === statusFilter;

            return matchesSearch && matchesType && matchesStatus;
        });

        this.renderDocumentGrid(filtered);
    }

    startPolling() {
        // Poll for updates every 10 seconds when processing section is active
        setInterval(() => {
            const activeSection = document.querySelector('.admin-section:not([style*="display: none"])');
            if (activeSection && activeSection.id === 'processing') {
                this.loadDocuments();
            }
        }, 10000);
    }

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

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleString('de-DE');
        } catch (error) {
            return dateString;
        }
    }

    showError(message) {
        console.error(message);
        // You could add a toast notification here
    }

    refresh() {
        this.loadDocuments();
    }
}

// Global functions for buttons
function showUploadModal() {
    const fileInput = document.getElementById('file-input');
    if (fileInput && window.documentProcessor && !window.documentProcessor.isUploading) {
        fileInput.click();
    }
}

function refreshDocuments() {
    if (window.documentProcessor) {
        window.documentProcessor.refresh();
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on the admin page and the processing section exists
    if (document.getElementById('processing')) {
        window.documentProcessor = new DocumentProcessor();
        
        // Initialize when processing section becomes active
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    const processingSection = document.getElementById('processing');
                    if (processingSection && !processingSection.style.display.includes('none')) {
                        if (!window.documentProcessor.initialized) {
                            window.documentProcessor.init();
                            window.documentProcessor.initialized = true;
                        }
                    }
                }
            });
        });

        observer.observe(document.getElementById('processing'), {
            attributes: true,
            attributeFilter: ['style']
        });
    }
});