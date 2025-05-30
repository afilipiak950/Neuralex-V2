/**
 * NeuraLex Platform - Frontend JavaScript
 * Handles interactive functionality, real-time updates, and API communication
 */

class NeuraLexApp {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.pollInterval = 5000; // 5 seconds
        this.activePollTimers = new Set();
        this.init();
    }

    init() {
        console.log('NeuraLex Platform initialized');
        this.setupEventListeners();
        this.setupPolling();
        this.initializeComponents();
    }

    setupEventListeners() {
        // Document upload form
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', this.handleDocumentUpload.bind(this));
        }

        // Refresh buttons
        document.querySelectorAll('[data-action="refresh"]').forEach(btn => {
            btn.addEventListener('click', this.refreshData.bind(this));
        });

        // Job detail buttons
        document.querySelectorAll('[data-action="view-job"]').forEach(btn => {
            btn.addEventListener('click', this.viewJobDetails.bind(this));
        });

        // Status filter
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', this.filterJobs.bind(this));
        }

        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('autoRefreshToggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', this.toggleAutoRefresh.bind(this));
        }
    }

    setupPolling() {
        // Auto-refresh dashboard data if on dashboard page
        if (document.getElementById('dashboard')) {
            this.startPolling();
        }
    }

    initializeComponents() {
        // Initialize tooltips
        this.initTooltips();
        
        // Initialize progress bars
        this.updateProgressBars();
        
        // Initialize status indicators
        this.updateStatusIndicators();
        
        // Check health status
        this.checkHealthStatus();
    }

    async handleDocumentUpload(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        try {
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Processing...';
            
            // Prepare request data
            const requestData = {};
            
            const gcsUri = formData.get('gcs_uri');
            const textContent = formData.get('text_content');
            
            if (gcsUri && gcsUri.trim()) {
                requestData.gcs_uri = gcsUri.trim();
            } else if (textContent && textContent.trim()) {
                requestData.payload = {
                    text: textContent.trim(),
                    metadata: {
                        source: 'manual_input',
                        timestamp: new Date().toISOString()
                    }
                };
            } else {
                throw new Error('Please provide either a GCS URI or text content');
            }
            
            // Submit to API
            const response = await fetch(`${this.apiBaseUrl}/ingest`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Upload failed');
            }
            
            const result = await response.json();
            
            // Show success message
            this.showNotification(`Document submitted successfully! Job ID: ${result.job_id}`, 'success');
            
            // Reset form
            form.reset();
            
            // Redirect to dashboard or refresh current view
            if (window.location.pathname === '/') {
                window.location.href = '/dashboard';
            } else {
                this.refreshData();
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showNotification(error.message, 'error');
        } finally {
            // Restore button state
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    async refreshData() {
        if (document.getElementById('dashboard')) {
            await this.refreshDashboard();
        }
    }

    async refreshDashboard() {
        try {
            // Show loading indicator
            this.showLoadingIndicator();
            
            // Fetch fresh data
            const [statsResponse, jobsResponse] = await Promise.all([
                fetch(`${this.apiBaseUrl}/api/stats`),
                fetch(`${this.apiBaseUrl}/jobs?limit=20`)
            ]);
            
            // Update stats if endpoint exists
            if (statsResponse.ok) {
                const stats = await statsResponse.json();
                this.updateStatsDisplay(stats);
            }
            
            // Update jobs table
            if (jobsResponse.ok) {
                const jobsData = await jobsResponse.json();
                this.updateJobsTable(jobsData.jobs);
            }
            
            this.hideLoadingIndicator();
            
        } catch (error) {
            console.error('Refresh error:', error);
            this.showNotification('Failed to refresh data', 'error');
            this.hideLoadingIndicator();
        }
    }

    updateStatsDisplay(stats) {
        const statsElements = {
            'total-documents': stats.total_documents,
            'processed-documents': stats.processed_documents,
            'pending-documents': stats.pending_documents,
            'success-rate': stats.success_rate
        };
        
        Object.entries(statsElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                // Animate number change
                this.animateNumber(element, value);
            }
        });
    }

    updateJobsTable(jobs) {
        const tbody = document.querySelector('#jobsTable tbody');
        if (!tbody) return;
        
        if (!jobs || jobs.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted">
                        No processing jobs found
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = jobs.map(job => `
            <tr>
                <td>
                    <code class="text-orange">${job.job_id.substring(0, 8)}</code>
                </td>
                <td>
                    <span class="badge badge-${this.getStatusBadgeClass(job.status)}">
                        ${job.status}
                    </span>
                </td>
                <td>${job.doc_type || '-'}</td>
                <td>${job.event_type || '-'}</td>
                <td>
                    ${job.confidence ? `${(job.confidence * 100).toFixed(1)}%` : '-'}
                </td>
                <td>${this.formatDateTime(job.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-outline" 
                            data-action="view-job" 
                            data-job-id="${job.job_id}">
                        View
                    </button>
                </td>
            </tr>
        `).join('');
        
        // Re-attach event listeners for new buttons
        tbody.querySelectorAll('[data-action="view-job"]').forEach(btn => {
            btn.addEventListener('click', this.viewJobDetails.bind(this));
        });
    }

    async viewJobDetails(event) {
        const jobId = event.target.dataset.jobId;
        if (!jobId) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/jobs/${jobId}`);
            if (!response.ok) {
                throw new Error('Failed to fetch job details');
            }
            
            const job = await response.json();
            this.showJobModal(job);
            
        } catch (error) {
            console.error('Error fetching job details:', error);
            this.showNotification('Failed to load job details', 'error');
        }
    }

    showJobModal(job) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Job Details</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="job-details">
                        <div class="detail-row">
                            <strong>Job ID:</strong>
                            <code>${job.job_id}</code>
                        </div>
                        <div class="detail-row">
                            <strong>Status:</strong>
                            <span class="badge badge-${this.getStatusBadgeClass(job.status)}">
                                ${job.status}
                            </span>
                        </div>
                        <div class="detail-row">
                            <strong>Document Type:</strong>
                            <span>${job.doc_type || 'Not classified'}</span>
                        </div>
                        <div class="detail-row">
                            <strong>Event Type:</strong>
                            <span>${job.event_type || 'Not classified'}</span>
                        </div>
                        <div class="detail-row">
                            <strong>Confidence:</strong>
                            <span>${job.confidence ? `${(job.confidence * 100).toFixed(2)}%` : 'N/A'}</span>
                        </div>
                        <div class="detail-row">
                            <strong>Created:</strong>
                            <span>${this.formatDateTime(job.created_at)}</span>
                        </div>
                        ${job.updated_at ? `
                            <div class="detail-row">
                                <strong>Updated:</strong>
                                <span>${this.formatDateTime(job.updated_at)}</span>
                            </div>
                        ` : ''}
                        ${job.error_message ? `
                            <div class="detail-row">
                                <strong>Error:</strong>
                                <span class="text-error">${job.error_message}</span>
                            </div>
                        ` : ''}
                        ${job.entities && job.entities.length > 0 ? `
                            <div class="detail-section">
                                <strong>Extracted Entities:</strong>
                                <div class="entities-list">
                                    ${job.entities.map(entity => `
                                        <div class="entity-item">
                                            <span class="entity-type">${entity.entity_type}</span>
                                            <span class="entity-text">"${entity.text}"</span>
                                            <span class="entity-confidence">${(entity.confidence * 100).toFixed(1)}%</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        // Add modal styles
        const style = document.createElement('style');
        style.textContent = `
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            }
            .modal-content {
                background: var(--tertiary-black);
                border-radius: var(--radius-lg);
                max-width: 600px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: var(--shadow-xl);
            }
            .modal-header {
                padding: var(--spacing-lg);
                border-bottom: 1px solid var(--surface-black);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .modal-close {
                background: none;
                border: none;
                color: var(--text-secondary);
                font-size: 1.5rem;
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .modal-body {
                padding: var(--spacing-lg);
            }
            .detail-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: var(--spacing-md);
                padding-bottom: var(--spacing-sm);
                border-bottom: 1px solid var(--surface-black);
            }
            .detail-section {
                margin-top: var(--spacing-lg);
            }
            .entities-list {
                margin-top: var(--spacing-md);
            }
            .entity-item {
                background: var(--surface-black);
                padding: var(--spacing-sm);
                margin-bottom: var(--spacing-sm);
                border-radius: var(--radius-sm);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .entity-type {
                background: var(--primary-orange);
                color: white;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 0.75rem;
                font-weight: 600;
            }
            .entity-text {
                flex: 1;
                margin: 0 var(--spacing-sm);
                color: var(--text-primary);
            }
            .entity-confidence {
                color: var(--text-muted);
                font-size: 0.875rem;
            }
            .text-error {
                color: var(--error);
            }
            .text-orange {
                color: var(--primary-orange);
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(modal);
        
        // Close modal handlers
        const closeModal = () => {
            document.body.removeChild(modal);
            document.head.removeChild(style);
        };
        
        modal.querySelector('.modal-close').addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
        
        // Close on escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
    }

    filterJobs() {
        const filter = document.getElementById('statusFilter').value;
        const rows = document.querySelectorAll('#jobsTable tbody tr');
        
        rows.forEach(row => {
            if (filter === 'all') {
                row.style.display = '';
            } else {
                const statusBadge = row.querySelector('.badge');
                const status = statusBadge ? statusBadge.textContent.trim() : '';
                row.style.display = status === filter ? '' : 'none';
            }
        });
    }

    toggleAutoRefresh(event) {
        const enabled = event.target.checked;
        
        if (enabled) {
            this.startPolling();
        } else {
            this.stopPolling();
        }
    }

    startPolling() {
        this.stopPolling(); // Clear existing timers
        
        const timer = setInterval(() => {
            this.refreshData();
        }, this.pollInterval);
        
        this.activePollTimers.add(timer);
    }

    stopPolling() {
        this.activePollTimers.forEach(timer => {
            clearInterval(timer);
        });
        this.activePollTimers.clear();
    }

    async checkHealthStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const healthIndicator = document.getElementById('healthStatus');
            
            if (healthIndicator) {
                if (response.ok) {
                    healthIndicator.className = 'health-indicator health-ok';
                    healthIndicator.textContent = 'System Healthy';
                } else {
                    healthIndicator.className = 'health-indicator health-warning';
                    healthIndicator.textContent = 'System Issues';
                }
            }
        } catch (error) {
            const healthIndicator = document.getElementById('healthStatus');
            if (healthIndicator) {
                healthIndicator.className = 'health-indicator health-error';
                healthIndicator.textContent = 'System Offline';
            }
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add notification styles
        const style = document.createElement('style');
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: var(--spacing-md);
                border-radius: var(--radius-md);
                color: white;
                font-weight: 500;
                z-index: 1000;
                min-width: 300px;
                animation: slideIn 0.3s ease-out;
            }
            .notification-success {
                background: var(--success);
            }
            .notification-error {
                background: var(--error);
            }
            .notification-warning {
                background: var(--warning);
                color: var(--primary-black);
            }
            .notification-info {
                background: var(--info);
            }
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideIn 0.3s ease-out reverse';
                setTimeout(() => {
                    document.body.removeChild(notification);
                    document.head.removeChild(style);
                }, 300);
            }
        }, 5000);
    }

    showLoadingIndicator() {
        const indicator = document.getElementById('loadingIndicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
    }

    hideLoadingIndicator() {
        const indicator = document.getElementById('loadingIndicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    animateNumber(element, targetValue) {
        const currentValue = parseFloat(element.textContent) || 0;
        const increment = (targetValue - currentValue) / 20;
        let current = currentValue;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= targetValue) || 
                (increment < 0 && current <= targetValue)) {
                current = targetValue;
                clearInterval(timer);
            }
            
            element.textContent = typeof targetValue === 'number' && targetValue % 1 !== 0 
                ? current.toFixed(1) 
                : Math.round(current);
        }, 50);
    }

    getStatusBadgeClass(status) {
        const statusMap = {
            'pending': 'pending',
            'processing': 'processing',
            'completed': 'success',
            'failed': 'error',
            'queued': 'info'
        };
        return statusMap[status] || 'info';
    }

    formatDateTime(dateString) {
        if (!dateString) return '-';
        
        const date = new Date(dateString);
        return date.toLocaleString();
    }

    updateProgressBars() {
        document.querySelectorAll('.progress-bar').forEach(bar => {
            const value = bar.dataset.value;
            if (value) {
                bar.style.width = `${value}%`;
            }
        });
    }

    updateStatusIndicators() {
        // Update any status indicators on the page
        document.querySelectorAll('[data-status]').forEach(indicator => {
            const status = indicator.dataset.status;
            indicator.className = `status-indicator status-${status}`;
        });
    }

    initTooltips() {
        // Simple tooltip implementation
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            element.addEventListener('mouseenter', this.showTooltip.bind(this));
            element.addEventListener('mouseleave', this.hideTooltip.bind(this));
        });
    }

    showTooltip(event) {
        const text = event.target.dataset.tooltip;
        if (!text) return;
        
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        
        document.body.appendChild(tooltip);
        
        const rect = event.target.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2}px`;
        tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
        
        event.target._tooltip = tooltip;
    }

    hideTooltip(event) {
        if (event.target._tooltip) {
            document.body.removeChild(event.target._tooltip);
            delete event.target._tooltip;
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.neuralex = new NeuraLexApp();
});

// Add tooltip styles
const tooltipStyles = document.createElement('style');
tooltipStyles.textContent = `
    .tooltip {
        position: absolute;
        background: var(--primary-black);
        color: var(--text-primary);
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--radius-sm);
        font-size: 0.875rem;
        white-space: nowrap;
        z-index: 1000;
        border: 1px solid var(--surface-black);
        box-shadow: var(--shadow-md);
        transform: translateX(-50%);
    }
    
    .health-indicator {
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--radius-sm);
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .health-ok {
        background: var(--success);
        color: white;
    }
    
    .health-warning {
        background: var(--warning);
        color: var(--primary-black);
    }
    
    .health-error {
        background: var(--error);
        color: white;
    }
    
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: var(--spacing-xs);
    }
    
    .status-pending {
        background: var(--primary-orange);
    }
    
    .status-processing {
        background: var(--primary-red);
        animation: pulse 2s infinite;
    }
    
    .status-completed {
        background: var(--success);
    }
    
    .status-failed {
        background: var(--error);
    }
`;

document.head.appendChild(tooltipStyles);
