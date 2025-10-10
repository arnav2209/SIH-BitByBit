// Main JavaScript file for College Timetable Scheduler

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips and interactive elements
    initializeApp();
});

function initializeApp() {
    // Add smooth transitions to all buttons
    const buttons = document.querySelectorAll('button, .btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-1px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
                submitBtn.disabled = true;
            }
        });
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        type === 'warning' ? 'bg-yellow-500 text-black' :
        'bg-blue-500 text-white'
    }`;
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-${
                type === 'success' ? 'check-circle' :
                type === 'error' ? 'exclamation-triangle' :
                type === 'warning' ? 'exclamation-circle' :
                'info-circle'
            } mr-2"></i>
            ${message}
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Form validation helpers
function validateForm(formId) {
    const form = document.getElementById(formId);
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('border-red-500');
            isValid = false;
        } else {
            field.classList.remove('border-red-500');
        }
    });
    
    return isValid;
}

// Timetable specific functions
function highlightTimeSlot(day, timeSlot) {
    const cells = document.querySelectorAll(`[data-day="${day}"][data-time="${timeSlot}"]`);
    cells.forEach(cell => {
        cell.classList.add('bg-yellow-100', 'ring-2', 'ring-yellow-400');
    });
}

function exportTimetableJSON(batchName, timetableData) {
    const data = {
        batch: batchName,
        generated: new Date().toISOString(),
        timetable: timetableData
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${batchName}_timetable.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Dashboard specific functions
function refreshStats() {
    // Placeholder for refreshing dashboard statistics
    showNotification('Statistics refreshed', 'success');
}

// Setup wizard functions
function nextStep(currentStep) {
    const current = document.getElementById(`step-${currentStep}`);
    const next = document.getElementById(`step-${currentStep + 1}`);
    
    if (current && next) {
        current.classList.add('hidden');
        next.classList.remove('hidden');
    }
}

function prevStep(currentStep) {
    const current = document.getElementById(`step-${currentStep}`);
    const prev = document.getElementById(`step-${currentStep - 1}`);
    
    if (current && prev) {
        current.classList.add('hidden');
        prev.classList.remove('hidden');
    }
}

// Mobile responsiveness helpers
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

// Print functionality
function printPage() {
    window.print();
}

// Theme and UI enhancements
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
}

// Load saved theme
function loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}

// Initialize theme on load
loadTheme();