/**
 * Progress bar and level progress functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Update XP Progress Bar
    function updateXpProgressBar() {
        const progressBars = document.querySelectorAll('.progress-bar[role="progressbar"]');
        
        progressBars.forEach(progressBar => {
            const value = parseFloat(progressBar.getAttribute('aria-valuenow'));
            const max = parseFloat(progressBar.getAttribute('aria-valuemax'));
            
            if (!isNaN(value) && !isNaN(max) && max > 0) {
                const percentage = (value / max) * 100;
                progressBar.style.width = `${percentage}%`;
                
                // Update text content if needed
                if (progressBar.textContent.includes('/')) {
                    progressBar.textContent = `${value}/${max} XP`;
                }
            }
        });
    }
    
    // Format numbers for display
    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
    
    // Update all progress displays
    function updateAllProgress() {
        updateXpProgressBar();
        
        // Find and update any other progress elements as needed
        const progressElements = document.querySelectorAll('[data-progress]');
        progressElements.forEach(element => {
            const current = parseFloat(element.getAttribute('data-current'));
            const target = parseFloat(element.getAttribute('data-target'));
            
            if (!isNaN(current) && !isNaN(target) && target > 0) {
                const percentage = (current / target) * 100;
                element.style.width = `${percentage}%`;
            }
        });
    }
    
    // For real-time progress updates via WebSocket (if implemented)
    function setupProgressWebSocket() {
        // This is a placeholder for WebSocket implementation
        // It would connect to a WebSocket server and update progress in real-time
        
        /*
        const socket = new WebSocket('ws://your-websocket-url/progress/');
        
        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.type === 'progress_update') {
                // Update specific progress element
                const element = document.querySelector(`[data-progress-id="${data.id}"]`);
                if (element) {
                    element.setAttribute('data-current', data.current);
                    element.setAttribute('data-target', data.target);
                    updateAllProgress();
                }
            }
        };
        
        socket.onclose = function(event) {
            console.log('WebSocket closed. Reconnecting in 5 seconds...');
            setTimeout(setupProgressWebSocket, 5000);
        };
        
        socket.onerror = function(error) {
            console.error('WebSocket error:', error);
            socket.close();
        };
        */
    }
    
    // Poll for updates (fallback if WebSockets aren't used)
    function setupProgressPolling() {
        // This would make an AJAX request every few seconds to check for updates
        // Not implemented here to avoid unnecessary traffic
    }
    
    // Initialize progress displays
    updateAllProgress();
    
    // Event delegation for dynamic elements
    document.addEventListener('click', function(event) {
        // Handle progress-related clicks
        if (event.target.matches('[data-action="refresh-progress"]')) {
            updateAllProgress();
        }
    });
    
    // Additional progress event listeners
    document.addEventListener('progress-updated', function(event) {
        updateAllProgress();
    });
    
    // Expose functions globally for use in other scripts
    window.gamifyProgress = {
        updateXpProgressBar,
        formatNumber,
        updateAllProgress
    };
});
