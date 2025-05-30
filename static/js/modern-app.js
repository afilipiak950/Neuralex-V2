// NeuraLex Platform - Modern Interactive JavaScript

class NeuraLexApp {
    constructor() {
        this.initializeApp();
        this.setupEventListeners();
        this.startAnimations();
        this.loadDashboardData();
    }

    initializeApp() {
        // Initialize particle system
        this.createParticleSystem();
        
        // Setup intersection observer for animations
        this.setupScrollAnimations();
        
        // Initialize counters
        this.animateCounters();
        
        // Setup real-time updates
        this.setupRealTimeUpdates();
    }

    createParticleSystem() {
        const canvas = document.createElement('canvas');
        canvas.id = 'particle-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '-1';
        canvas.style.opacity = '0.3';
        
        document.body.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        let particles = [];
        
        const resizeCanvas = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };
        
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();
        
        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = (Math.random() - 0.5) * 0.5;
                this.size = Math.random() * 2 + 1;
                this.opacity = Math.random() * 0.5 + 0.2;
            }
            
            update() {
                this.x += this.vx;
                this.y += this.vy;
                
                if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
                if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
            }
            
            draw() {
                ctx.save();
                ctx.globalAlpha = this.opacity;
                ctx.fillStyle = '#ff3838';
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }
        
        // Create particles
        for (let i = 0; i < 50; i++) {
            particles.push(new Particle());
        }
        
        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            particles.forEach(particle => {
                particle.update();
                particle.draw();
            });
            
            // Draw connections
            particles.forEach((particle, i) => {
                particles.slice(i + 1).forEach(otherParticle => {
                    const dx = particle.x - otherParticle.x;
                    const dy = particle.y - otherParticle.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance < 100) {
                        ctx.save();
                        ctx.globalAlpha = (100 - distance) / 100 * 0.2;
                        ctx.strokeStyle = '#ff3838';
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.moveTo(particle.x, particle.y);
                        ctx.lineTo(otherParticle.x, otherParticle.y);
                        ctx.stroke();
                        ctx.restore();
                    }
                });
            });
            
            requestAnimationFrame(animate);
        };
        
        animate();
    }

    setupScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.glass-card, .feature-card, .stat-card').forEach(el => {
            observer.observe(el);
        });
    }

    animateCounters() {
        const counters = document.querySelectorAll('.stat-number');
        
        counters.forEach(counter => {
            const target = parseInt(counter.textContent);
            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;
            
            const timer = setInterval(() => {
                current += step;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                counter.textContent = Math.floor(current);
            }, 16);
        });
    }

    setupEventListeners() {
        // Form submission
        const uploadForm = document.getElementById('upload-form');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => this.handleFormSubmission(e));
        }

        // File drag and drop
        const uploadContainer = document.querySelector('.upload-container');
        if (uploadContainer) {
            this.setupDragAndDrop(uploadContainer);
        }

        // Navigation smooth scrolling
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', (e) => this.handleNavClick(e));
        });

        // Real-time job status updates
        this.setupJobStatusPolling();
    }

    setupDragAndDrop(container) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            container.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            container.addEventListener(eventName, () => this.highlight(container), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            container.addEventListener(eventName, () => this.unhighlight(container), false);
        });

        container.addEventListener('drop', (e) => this.handleDrop(e), false);
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    highlight(container) {
        container.classList.add('drag-over');
        container.style.borderColor = '#ff3838';
        container.style.background = 'rgba(255, 56, 56, 0.1)';
    }

    unhighlight(container) {
        container.classList.remove('drag-over');
        container.style.borderColor = '';
        container.style.background = '';
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            this.processFiles(files);
        }
    }

    processFiles(files) {
        Array.from(files).forEach(file => {
            if (file.type === 'text/plain' || file.type === 'application/json') {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const textArea = document.getElementById('text_content');
                    if (textArea) {
                        textArea.value = e.target.result;
                        this.showToast('File content loaded successfully!', 'success');
                    }
                };
                reader.readAsText(file);
            } else {
                this.showToast('Please upload text or JSON files only.', 'error');
            }
        });
    }

    async handleFormSubmission(e) {
        e.preventDefault();
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        // Show loading state
        submitBtn.innerHTML = '<span class="loading-spinner"></span> Processing...';
        submitBtn.disabled = true;
        
        try {
            const formData = new FormData(e.target);
            const response = await fetch('/ingest-form', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.text();
                
                // Check if response contains success message
                if (result.includes('successfully')) {
                    this.showToast('Document submitted successfully!', 'success');
                    e.target.reset();
                    this.updateDashboard();
                } else {
                    this.showToast('Error processing document', 'error');
                }
            } else {
                throw new Error('Network response was not ok');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showToast('Error submitting document', 'error');
        } finally {
            // Reset button state
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    handleNavClick(e) {
        const href = e.target.getAttribute('href');
        if (href && href.startsWith('#')) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }

    setupJobStatusPolling() {
        // Poll for job updates every 5 seconds
        setInterval(() => {
            this.updateJobStatuses();
        }, 5000);
    }

    async updateJobStatuses() {
        try {
            const response = await fetch('/jobs?limit=10');
            const data = await response.json();
            
            if (data.jobs) {
                this.updateJobDisplay(data.jobs);
                this.updateStatistics(data.jobs);
            }
        } catch (error) {
            console.error('Error fetching job statuses:', error);
        }
    }

    updateJobDisplay(jobs) {
        const jobsList = document.getElementById('recent-jobs');
        if (!jobsList) return;
        
        jobsList.innerHTML = '';
        
        jobs.forEach(job => {
            const jobElement = this.createJobElement(job);
            jobsList.appendChild(jobElement);
        });
    }

    createJobElement(job) {
        const div = document.createElement('div');
        div.className = 'job-item glass-card';
        div.style.marginBottom = '1rem';
        
        const statusClass = `status-${job.status}`;
        const statusIcon = this.getStatusIcon(job.status);
        
        div.innerHTML = `
            <div class="status-header">
                <div>
                    <strong>Job ${job.id.substring(0, 8)}</strong>
                    <div class="status-indicator ${statusClass}">
                        ${statusIcon} ${job.status.toUpperCase()}
                    </div>
                </div>
                <small>${new Date(job.created_at).toLocaleString()}</small>
            </div>
            ${job.status === 'processing' ? this.createProgressBar() : ''}
            ${job.entities ? this.createEntitiesDisplay(job.entities) : ''}
        `;
        
        return div;
    }

    getStatusIcon(status) {
        const icons = {
            pending: '⏳',
            processing: '⚡',
            completed: '✅',
            failed: '❌'
        };
        return icons[status] || '📄';
    }

    createProgressBar() {
        return `
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${Math.random() * 100}%"></div>
            </div>
        `;
    }

    createEntitiesDisplay(entities) {
        if (!entities || entities.length === 0) return '';
        
        const entitiesHtml = entities.map(entity => `
            <span class="entity-tag" style="
                display: inline-block;
                background: rgba(255, 56, 56, 0.1);
                color: #ff3838;
                padding: 0.25rem 0.5rem;
                border-radius: 12px;
                font-size: 0.8rem;
                margin: 0.25rem;
            ">
                ${entity.type}: ${entity.text} (${Math.floor(entity.confidence * 100)}%)
            </span>
        `).join('');
        
        return `<div style="margin-top: 1rem;">${entitiesHtml}</div>`;
    }

    updateStatistics(jobs) {
        const total = jobs.length;
        const completed = jobs.filter(j => j.status === 'completed').length;
        const pending = jobs.filter(j => j.status === 'pending').length;
        const processing = jobs.filter(j => j.status === 'processing').length;
        
        this.updateStatElement('total-docs', total);
        this.updateStatElement('completed-docs', completed);
        this.updateStatElement('pending-docs', pending);
        this.updateStatElement('processing-docs', processing);
    }

    updateStatElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    async updateDashboard() {
        try {
            const response = await fetch('/jobs?limit=1000');
            const data = await response.json();
            
            if (data.jobs) {
                this.updateStatistics(data.jobs);
                this.updateJobDisplay(data.jobs.slice(0, 10));
            }
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }

    async loadDashboardData() {
        await this.updateDashboard();
        this.startRealTimeUpdates();
    }

    startRealTimeUpdates() {
        // Update dashboard every 3 seconds
        setInterval(() => {
            this.updateDashboard();
        }, 3000);
    }

    startAnimations() {
        // Typing animation for hero text
        this.typeWriter();
        
        // Floating animation for cards
        this.startFloatingAnimation();
    }

    typeWriter() {
        const element = document.querySelector('.hero h1');
        if (!element) return;
        
        const text = element.textContent;
        element.textContent = '';
        
        let i = 0;
        const timer = setInterval(() => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
            }
        }, 100);
    }

    startFloatingAnimation() {
        const cards = document.querySelectorAll('.glass-card, .feature-card');
        
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.2}s`;
            card.classList.add('floating');
        });
    }

    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }

    setupRealTimeUpdates() {
        // Simulate real-time WebSocket-like updates
        setInterval(() => {
            const processingJobs = document.querySelectorAll('.status-processing');
            processingJobs.forEach(job => {
                const progressBar = job.parentElement.querySelector('.progress-fill');
                if (progressBar) {
                    const currentWidth = parseInt(progressBar.style.width) || 0;
                    const newWidth = Math.min(currentWidth + Math.random() * 10, 100);
                    progressBar.style.width = `${newWidth}%`;
                }
            });
        }, 1000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new NeuraLexApp();
});

// Add floating animation CSS
const style = document.createElement('style');
style.textContent = `
    .floating {
        animation: floating 3s ease-in-out infinite;
    }
    
    @keyframes floating {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .drag-over {
        transform: scale(1.02);
        transition: transform 0.2s ease;
    }
`;
document.head.appendChild(style);