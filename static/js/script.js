// DOM Elements
const reminderForm = document.getElementById('reminderForm');
const remindersList = document.getElementById('remindersList');
const successModal = document.getElementById('successModal');
const errorToast = document.getElementById('errorToast');
const errorMessage = document.getElementById('errorMessage');
const emailField = document.getElementById('emailField');
const phoneField = document.getElementById('phoneField');

// Time display elements (removed header time elements)
const heroCurrentTimeElement = document.getElementById('heroCurrentTime');
const heroCurrentDateElement = document.getElementById('heroCurrentDate');
const heroTimezoneElement = document.getElementById('heroTimezone');
const sectionCurrentTimeElement = document.getElementById('sectionCurrentTime');

// ADDED: Clear reminders elements
const clearAllBtn = document.getElementById('clearAllBtn');
const clearConfirmModal = document.getElementById('clearConfirmModal');
const clearSuccessModal = document.getElementById('clearSuccessModal');

// Time update interval
let timeUpdateInterval;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    loadReminders();
    setMinDate();
    setupMethodToggle();
    initializeTimeDisplay();
    setupClearReminders(); // ADDED: Setup clear functionality
    
    // Smooth scrolling for navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update active nav link
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });
});

// ADDED: Setup clear reminders functionality
function setupClearReminders() {
    clearAllBtn.addEventListener('click', function() {
        clearConfirmModal.style.display = 'block';
    });
    
    // Close modals when clicking outside
    clearConfirmModal.addEventListener('click', function(e) {
        if (e.target === clearConfirmModal) {
            closeClearModal();
        }
    });
    
    clearSuccessModal.addEventListener('click', function(e) {
        if (e.target === clearSuccessModal) {
            closeClearSuccessModal();
        }
    });
}

// ADDED: Clear modal functions
function closeClearModal() {
    clearConfirmModal.style.display = 'none';
}

function closeClearSuccessModal() {
    clearSuccessModal.style.display = 'none';
}

// ADDED: Confirm clear all reminders
async function confirmClearAll() {
    try {
        clearAllBtn.disabled = true;
        clearAllBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Clearing...';
        
        const response = await fetch('/api/reminders/clear', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            closeClearModal();
            clearSuccessModal.style.display = 'block';
            loadReminders(); // Reload the reminders list
            
            // Auto close success modal after 3 seconds
            setTimeout(() => {
                closeClearSuccessModal();
            }, 3000);
        } else {
            showError(result.error || 'Failed to clear reminders');
            closeClearModal();
        }
    } catch (error) {
        showError('Network error. Please try again.');
        closeClearModal();
    } finally {
        clearAllBtn.disabled = false;
        clearAllBtn.innerHTML = '<i class="fas fa-trash-alt"></i> Clear All Reminders';
    }
}

// Initialize and manage time display (removed header time)
function initializeTimeDisplay() {
    updateAllTimeDisplays();
    
    // Update time every second
    timeUpdateInterval = setInterval(updateAllTimeDisplays, 1000);
    
    // Update timezone information
    updateTimezoneInfo();
}

// Update all time displays (removed header time)
function updateAllTimeDisplays() {
    const now = new Date();
    
    // Format time (HH:MM:SS)
    const timeString = now.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    // Format date
    const dateString = now.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
    
    // Format time for hero (12-hour format)
    const heroTimeString = now.toLocaleTimeString('en-US', {
        hour12: true,
        hour: 'numeric',
        minute: '2-digit',
        second: '2-digit'
    });
    
    // Update hero time display
    if (heroCurrentTimeElement) {
        heroCurrentTimeElement.textContent = heroTimeString;
        heroCurrentTimeElement.classList.add('time-update');
        setTimeout(() => heroCurrentTimeElement.classList.remove('time-update'), 300);
    }
    
    if (heroCurrentDateElement) {
        heroCurrentDateElement.textContent = dateString;
    }
    
    // Update section time display
    if (sectionCurrentTimeElement) {
        sectionCurrentTimeElement.textContent = timeString;
        sectionCurrentTimeElement.classList.add('time-update');
        setTimeout(() => sectionCurrentTimeElement.classList.remove('time-update'), 300);
    }
}

// Update timezone information
function updateTimezoneInfo() {
    if (heroTimezoneElement) {
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const offset = new Date().getTimezoneOffset();
        const offsetHours = Math.abs(Math.floor(offset / 60));
        const offsetMinutes = Math.abs(offset % 60);
        const offsetSign = offset <= 0 ? '+' : '-';
        
        heroTimezoneElement.textContent = `${timezone} (UTC${offsetSign}${offsetHours.toString().padStart(2, '0')}:${offsetMinutes.toString().padStart(2, '0')})`;
    }
}

// Set minimum date to today
function setMinDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').setAttribute('min', today);
}

// Setup reminder method toggle
function setupMethodToggle() {
    const methodRadios = document.querySelectorAll('input[name="reminder_method"]');
    
    methodRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'email') {
                emailField.style.display = 'block';
                phoneField.style.display = 'none';
                document.getElementById('email_address').required = true;
                document.getElementById('phone_number').required = false;
            } else if (this.value === 'sms') {
                emailField.style.display = 'none';
                phoneField.style.display = 'block';
                document.getElementById('email_address').required = false;
                document.getElementById('phone_number').required = true;
            }
        });
    });
}

// Handle form submission
reminderForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitBtn = document.querySelector('.submit-btn');
    const formData = new FormData(this);
    
    const reminderData = {
        date: formData.get('date'),
        time: formData.get('time'),
        message: formData.get('message'),
        reminder_method: formData.get('reminder_method'),
        email_address: formData.get('email_address'),
        phone_number: formData.get('phone_number')
    };
    
    // Add loading state
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/api/reminder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(reminderData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccessModal();
            reminderForm.reset();
            setupMethodToggle(); // Reset field visibility
            loadReminders();
        } else {
            showError(result.error || 'Failed to create reminder');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    } finally {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
    }
});

// Load and display reminders
async function loadReminders() {
    try {
        const response = await fetch('/api/reminders');
        const result = await response.json();
        
        if (response.ok) {
            displayReminders(result.reminders);
            updateClearButtonState(result.reminders.length); // ADDED: Update clear button state
        } else {
            showError('Failed to load reminders');
        }
    } catch (error) {
        showError('Failed to load reminders');
    }
}

// ADDED: Update clear button state based on reminders count
function updateClearButtonState(reminderCount) {
    if (reminderCount === 0) {
        clearAllBtn.disabled = true;
        clearAllBtn.innerHTML = '<i class="fas fa-trash-alt"></i> No Reminders to Clear';
    } else {
        clearAllBtn.disabled = false;
        clearAllBtn.innerHTML = `<i class="fas fa-trash-alt"></i> Clear All Reminders (${reminderCount})`;
    }
}

// Display reminders in the grid
function displayReminders(reminders) {
    if (reminders.length === 0) {
        remindersList.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: #666;">
                <i class="fas fa-bell-slash" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                <p>No reminders yet. Create your first reminder above!</p>
            </div>
        `;
        return;
    }
    
    remindersList.innerHTML = reminders.map(reminder => `
        <div class="reminder-card">
            <div class="reminder-header">
                <div class="reminder-date-time">
                    <i class="fas fa-calendar"></i> ${formatDate(reminder.date)}
                    <br>
                    <i class="fas fa-clock"></i> ${formatTime(reminder.time)}
                </div>
                <div class="reminder-status">
                    <span class="reminder-method">
                        <i class="fas fa-${reminder.reminder_method === 'email' ? 'envelope' : 'sms'}"></i>
                        ${reminder.reminder_method.toUpperCase()}
                    </span>
                    <span class="reminder-sent ${reminder.is_sent ? 'sent' : 'pending'}">
                        <i class="fas fa-${reminder.is_sent ? 'check-circle' : 'clock'}"></i>
                        ${reminder.is_sent ? 'Sent' : 'Pending'}
                    </span>
                </div>
            </div>
            <div class="reminder-message">${reminder.message}</div>
            <div class="reminder-contact">
                <i class="fas fa-${reminder.reminder_method === 'email' ? 'envelope' : 'phone'}"></i>
                ${reminder.reminder_method === 'email' ? reminder.email_address : reminder.phone_number}
            </div>
            <div class="reminder-created">
                Created: ${formatDateTime(reminder.created_at)}
            </div>
        </div>
    `).join('');
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(timeString) {
    const [hours, minutes] = timeString.split(':');
    const date = new Date();
    date.setHours(parseInt(hours), parseInt(minutes));
    return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

// Modal and toast functions
function showSuccessModal() {
    successModal.style.display = 'block';
    setTimeout(() => {
        successModal.style.display = 'none';
    }, 3000);
}

function closeModal() {
    successModal.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorToast.style.display = 'flex';
    setTimeout(() => {
        errorToast.style.display = 'none';
    }, 5000);
}

// Close modal when clicking outside
successModal.addEventListener('click', function(e) {
    if (e.target === successModal) {
        closeModal();
    }
});

// Cleanup function for when page is unloaded
window.addEventListener('beforeunload', function() {
    if (timeUpdateInterval) {
        clearInterval(timeUpdateInterval);
    }
});

// Handle visibility change to pause/resume time updates
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden, clear interval to save resources
        if (timeUpdateInterval) {
            clearInterval(timeUpdateInterval);
        }
    } else {
        // Page is visible again, restart time updates
        updateAllTimeDisplays();
        timeUpdateInterval = setInterval(updateAllTimeDisplays, 1000);
    }
});
