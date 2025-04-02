/**
 * Good Work Timer functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get timer elements
    const startButton = document.getElementById('start-timer');
    const stopButton = document.getElementById('stop-timer');
    const timerDisplay = document.getElementById('timer-display');
    const timerCard = document.getElementById('timer-card');
    const timerStatus = document.getElementById('timer-status');
    const timerMessage = document.getElementById('timer-message');

    // Timer state
    let timerInterval;
    let startTime;
    let isRunning = false;
    
    // If there's an active session already
    if (document.getElementById('session-id')) {
        isRunning = true;
        const sessionStartTime = new Date(document.getElementById('start-time').value);
        startTime = sessionStartTime;
        
        // Start the timer
        startTimer();
    }
    
    // Set up event listeners
    if (startButton) {
        startButton.addEventListener('click', function() {
            fetch('/tasks/start-timer/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Set session id and start time
                    const sessionId = data.session_id;
                    startTime = new Date(data.start_time);
                    
                    // Create hidden input for session id
                    const sessionIdInput = document.createElement('input');
                    sessionIdInput.type = 'hidden';
                    sessionIdInput.id = 'session-id';
                    sessionIdInput.value = sessionId;
                    document.body.appendChild(sessionIdInput);
                    
                    // Create hidden input for start time
                    const startTimeInput = document.createElement('input');
                    startTimeInput.type = 'hidden';
                    startTimeInput.id = 'start-time';
                    startTimeInput.value = data.start_time;
                    document.body.appendChild(startTimeInput);
                    
                    // Update UI
                    startTimer();
                    
                    // Replace start button with stop button
                    startButton.innerHTML = '<i class="fas fa-stop-circle me-2"></i> Stop Timer';
                    startButton.className = 'btn btn-danger btn-lg';
                    startButton.id = 'stop-timer';
                    
                    // Update timer card
                    timerCard.classList.add('timer-active');
                    timerStatus.textContent = 'Timer Running';
                    timerMessage.textContent = `Timer started at ${new Date().toLocaleTimeString()}`;
                    
                    // Refresh the page to show stop button
                    window.location.reload();
                } else {
                    alert('Error starting timer: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('There was an error starting the timer. Please try again.');
            });
        });
    }
    
    if (stopButton) {
        stopButton.addEventListener('click', function() {
            const sessionId = document.getElementById('session-id').value;
            
            fetch('/tasks/stop-timer/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `session_id=${sessionId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Stop the timer
                    clearInterval(timerInterval);
                    isRunning = false;
                    
                    // Show success message
                    alert(`Timer stopped! You completed ${data.duration_minutes} minutes and earned ${data.xp_earned} XP.`);
                    
                    // Refresh the page
                    window.location.reload();
                } else {
                    alert('Error stopping timer: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('There was an error stopping the timer. Please try again.');
            });
        });
    }
    
    function startTimer() {
        isRunning = true;
        
        // Update the timer display immediately
        updateTimerDisplay();
        
        // Update every second
        timerInterval = setInterval(updateTimerDisplay, 1000);
    }
    
    function updateTimerDisplay() {
        if (!isRunning) return;
        
        const now = new Date();
        const elapsed = now - startTime; // in milliseconds
        
        // Calculate hours, minutes, seconds
        const hours = Math.floor(elapsed / (1000 * 60 * 60));
        const minutes = Math.floor((elapsed % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((elapsed % (1000 * 60)) / 1000);
        
        // Format numbers with leading zeros
        const formattedHours = hours.toString().padStart(2, '0');
        const formattedMinutes = minutes.toString().padStart(2, '0');
        const formattedSeconds = seconds.toString().padStart(2, '0');
        
        // Update the display
        if (timerDisplay) {
            timerDisplay.innerHTML = `<span id="hours">${formattedHours}</span>:<span id="minutes">${formattedMinutes}</span>:<span id="seconds">${formattedSeconds}</span>`;
        }
    }
    
    // Get CSRF token from cookie
    function getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
