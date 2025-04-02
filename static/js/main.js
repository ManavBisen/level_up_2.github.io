// Main JavaScript file for Gamify

document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips everywhere
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert-dismissible').alert('close');
    }, 5000);

    // Add confirm dialog to delete buttons
    document.querySelectorAll('.btn-delete').forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
                return false;
            }
        });
    });

    // File input customization
    document.querySelectorAll('.custom-file-input').forEach(function(input) {
        input.addEventListener('change', function(e) {
            var fileName = this.files[0].name;
            var nextSibling = this.nextElementSibling;
            nextSibling.innerText = fileName;
        });
    });

    // Increment/decrement buttons for number inputs
    document.querySelectorAll('.increment-btn').forEach(function(button) {
        button.addEventListener('click', function() {
            var input = document.querySelector(this.getAttribute('data-target'));
            var step = parseInt(input.getAttribute('step') || 1);
            input.value = parseInt(input.value || 0) + step;
            // Trigger change event
            var event = new Event('change');
            input.dispatchEvent(event);
        });
    });

    document.querySelectorAll('.decrement-btn').forEach(function(button) {
        button.addEventListener('click', function() {
            var input = document.querySelector(this.getAttribute('data-target'));
            var step = parseInt(input.getAttribute('step') || 1);
            var minValue = parseInt(input.getAttribute('min') || 0);
            var newValue = parseInt(input.value || 0) - step;
            input.value = newValue >= minValue ? newValue : minValue;
            // Trigger change event
            var event = new Event('change');
            input.dispatchEvent(event);
        });
    });

    // Sidebar toggle on mobile
    var sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            document.body.classList.toggle('sidebar-toggled');
            document.querySelector('.sidebar').classList.toggle('toggled');
        });
    }

    // Close alerts when clicked
    document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
        alert.addEventListener('click', function() {
            this.classList.add('fade');
            setTimeout(function() {
                alert.remove();
            }, 150);
        });
    });

    // Highlight active navbar link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-nav a.nav-link').forEach(function(link) {
        const linkPath = link.getAttribute('href');
        if (linkPath && currentPath.startsWith(linkPath) && linkPath !== '/') {
            link.classList.add('active');
        } else if (linkPath === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    });
});

// Function to format time in HH:MM:SS
function formatTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return [
        h.toString().padStart(2, '0'),
        m.toString().padStart(2, '0'),
        s.toString().padStart(2, '0')
    ].join(':');
}

// Function to format number with commas
function formatNumber(num) {
    return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
}

// Function to copy text to clipboard
function copyToClipboard(text) {
    const tempInput = document.createElement('input');
    tempInput.value = text;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
    
    // Show a toast notification
    const toastEl = document.createElement('div');
    toastEl.classList.add('toast', 'show', 'bg-success', 'text-white');
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.style.position = 'fixed';
    toastEl.style.bottom = '20px';
    toastEl.style.right = '20px';
    toastEl.style.minWidth = '200px';
    toastEl.innerHTML = `
        <div class="toast-header bg-success text-white">
            <strong class="me-auto">Copied</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            Text copied to clipboard!
        </div>
    `;
    
    document.body.appendChild(toastEl);
    
    // Remove the toast after 3 seconds
    setTimeout(() => {
        toastEl.remove();
    }, 3000);
}
