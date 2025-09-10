// Main Application JavaScript
class CivicApp {
    constructor() {
        this.baseURL = 'http://localhost:8002';
        this.token = localStorage.getItem('access_token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
        this.init();
    }

    init() {
        // Check if user is authenticated on page load
        if (this.token && this.user) {
            this.redirectToDashboard();
        }
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Phone number form submission
        const phoneForm = document.getElementById('phoneForm');
        if (phoneForm) {
            phoneForm.addEventListener('submit', (e) => this.handlePhoneSubmit(e));
        }

        // OTP form submission
        const otpForm = document.getElementById('otpForm');
        if (otpForm) {
            otpForm.addEventListener('submit', (e) => this.handleOTPSubmit(e));
        }

        // Issue form submission
        const issueForm = document.getElementById('issueForm');
        if (issueForm) {
            issueForm.addEventListener('submit', (e) => this.handleIssueSubmit(e));
        }

        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

        // File upload preview
        const photoUpload = document.getElementById('photoUpload');
        if (photoUpload) {
            photoUpload.addEventListener('change', (e) => this.handleFilePreview(e));
        }
    }

    async handlePhoneSubmit(e) {
        e.preventDefault();
        let phoneNumber = document.getElementById('phoneNumber').value;
        
        if (!phoneNumber || phoneNumber.length !== 10) {
            this.showError('Please enter a valid 10-digit phone number');
            return;
        }

        // Add India country code if not present
        if (!phoneNumber.startsWith('+')) {
            phoneNumber = '+91' + phoneNumber;
        }

        try {
            this.showLoading('phoneForm', true);
            
            const response = await fetch(`${this.baseURL}/auth/send-otp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ phone_number: phoneNumber })
            });

            const data = await response.json();

            if (response.ok) {
                // Hide phone form, show OTP form
                document.getElementById('phoneSection').style.display = 'none';
                document.getElementById('otpSection').style.display = 'block';
                document.getElementById('otpMessage').textContent = `OTP sent to ${phoneNumber}`;
                
                // Store phone number for OTP verification
                sessionStorage.setItem('phone_number', phoneNumber);
            } else {
                this.showError(data.detail || 'Failed to send OTP');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        } finally {
            this.showLoading('phoneForm', false);
        }
    }

    async handleOTPSubmit(e) {
        e.preventDefault();
        const otp = document.getElementById('otp').value;
        const phoneNumber = sessionStorage.getItem('phone_number');

        if (!otp || otp.length !== 6) {
            this.showError('Please enter a valid 6-digit OTP');
            return;
        }

        try {
            this.showLoading('otpForm', true);
            
            const response = await fetch(`${this.baseURL}/auth/verify-otp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    phone_number: phoneNumber,
                    otp: otp 
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Store token and user data
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user));
                
                this.token = data.access_token;
                this.user = data.user;
                
                // Redirect to dashboard
                this.redirectToDashboard();
            } else {
                this.showError(data.detail || 'Invalid OTP');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        } finally {
            this.showLoading('otpForm', false);
        }
    }

    async handleIssueSubmit(e) {
        e.preventDefault();
        
        const title = document.getElementById('title').value;
        const description = document.getElementById('description').value;
        const category = document.getElementById('category').value;
        const priority = document.getElementById('priority').value;
        const location = document.getElementById('location').value;
        const photoFile = document.getElementById('photoUpload').files[0];

        if (!title || !description || !category || !location) {
            this.showError('Please fill in all required fields');
            return;
        }

        try {
            this.showLoading('issueForm', true);
            
            const formData = new FormData();
            formData.append('title', title);
            formData.append('description', description);
            formData.append('category', category);
            formData.append('priority', priority);
            formData.append('location', location);
            
            if (photoFile) {
                formData.append('photo', photoFile);
            }

            const response = await fetch(`${this.baseURL}/users/issues`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccess('Issue reported successfully!');
                document.getElementById('issueForm').reset();
                document.getElementById('photoPreview').innerHTML = '';
                
                // Refresh the issues list
                setTimeout(() => {
                    this.loadUserIssues();
                }, 1000);
            } else {
                this.showError(data.detail || 'Failed to report issue');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        } finally {
            this.showLoading('issueForm', false);
        }
    }

    async loadUserIssues() {
        try {
            const response = await fetch(`${this.baseURL}/users/my-issues`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.displayIssues(data.issues);
            } else {
                console.error('Failed to load issues:', data.detail);
            }
        } catch (error) {
            console.error('Error loading issues:', error);
        }
    }

    displayIssues(issues) {
        const issuesList = document.getElementById('issuesList');
        if (!issuesList) return;

        if (issues.length === 0) {
            issuesList.innerHTML = '<p class="no-issues">No issues reported yet.</p>';
            return;
        }

        const issuesHTML = issues.map(issue => `
            <div class="issue-card">
                <div class="issue-header">
                    <h3>${issue.title}</h3>
                    <span class="status-badge status-${issue.status.toLowerCase()}">${issue.status}</span>
                </div>
                <p class="issue-description">${issue.description}</p>
                <div class="issue-meta">
                    <span class="category">${issue.category}</span>
                    <span class="priority priority-${issue.priority.toLowerCase()}">${issue.priority}</span>
                    <span class="location">${issue.location}</span>
                </div>
                <div class="issue-footer">
                    <small>Reported on ${new Date(issue.created_at).toLocaleDateString()}</small>
                    ${issue.photo_url ? `<a href="${issue.photo_url}" target="_blank" class="photo-link">View Photo</a>` : ''}
                </div>
            </div>
        `).join('');

        issuesList.innerHTML = issuesHTML;
    }

    handleFilePreview(e) {
        const file = e.target.files[0];
        const preview = document.getElementById('photoPreview');
        
        if (file) {
            if (file.size > 5 * 1024 * 1024) { // 5MB limit
                this.showError('File size must be less than 5MB');
                e.target.value = '';
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `
                    <div class="file-preview">
                        <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px; border-radius: 8px;">
                        <p>${file.name}</p>
                    </div>
                `;
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = '';
        }
    }

    redirectToDashboard() {
        if (window.location.pathname !== '/pages/dashboard.html') {
            window.location.href = '/pages/dashboard.html';
        } else {
            // If already on dashboard, load user data
            this.loadDashboardData();
        }
    }

    loadDashboardData() {
        if (this.user) {
            const userInfo = document.getElementById('userInfo');
            if (userInfo) {
                userInfo.textContent = `Welcome, ${this.user.phone_number}`;
            }
            
            this.loadUserIssues();
        }
    }

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        sessionStorage.clear();
        window.location.href = '/index.html';
    }

    showLoading(formId, show) {
        const form = document.getElementById(formId);
        if (form) {
            if (show) {
                form.classList.add('loading');
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Loading...';
                }
            } else {
                form.classList.remove('loading');
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    // Restore original text based on form
                    if (formId === 'phoneForm') submitBtn.textContent = 'Send OTP';
                    if (formId === 'otpForm') submitBtn.textContent = 'Verify OTP';
                    if (formId === 'issueForm') submitBtn.textContent = 'Report Issue';
                }
            }
        }
    }

    showError(message) {
        this.showMessage(message, 'error');
    }

    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    showMessage(message, type) {
        // Remove existing messages
        const existingMessage = document.querySelector('.message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // Create new message
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        
        // Insert at top of body
        document.body.insertBefore(messageDiv, document.body.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.civicApp = new CivicApp();
});
