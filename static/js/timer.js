// Timer functionality for Good Work sessions

let timer;
let startTime;
let elapsedSeconds = 0;
let isRunning = false;

// Initialize timer with a specific start time (for active sessions)
function initializeTimer(sessionStartTime) {
    startTime = sessionStartTime;
    isRunning = true;
    
    // Update immediately
    updateTimerDisplay();
    
    // Then update every second
    timer = setInterval(updateTimerDisplay, 1000);
}

// Start a new timer
function startTimer() {
    if (!isRunning) {
        startTime = Date.now() - (elapsedSeconds * 1000);
        isRunning = true;
        timer = setInterval(updateTimerDisplay, 1000);
    }
}

// Pause the timer
function pauseTimer() {
    if (isRunning) {
        clearInterval(timer);
        isRunning = false;
        elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
    }
}

// Reset the timer
function resetTimer() {
    clearInterval(timer);
    isRunning = false;
    elapsedSeconds = 0;
    updateTimerDisplay();
}

// Update the timer display
function updateTimerDisplay() {
    const timerElement = document.getElementById('timer');
    if (!timerElement) return;
    
    if (isRunning) {
        elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
    }
    
    const hours = Math.floor(elapsedSeconds / 3600);
    const minutes = Math.floor((elapsedSeconds % 3600) / 60);
    const seconds = elapsedSeconds % 60;
    
    timerElement.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    
    // Update document title with timer
    document.title = `${timerElement.textContent} - Good Work Timer`;
    
    // Visual indication for milestones
    if (elapsedSeconds >= 40 * 60) { // 40 minutes for daily task
        timerElement.classList.add('text-success');
        timerElement.classList.remove('text-danger', 'text-warning');
    } else if (elapsedSeconds >= 30 * 60) { // 30 minutes
        timerElement.classList.add('text-warning');
        timerElement.classList.remove('text-danger', 'text-success');
    } else if (elapsedSeconds >= 20 * 60) { // 20 minutes
        timerElement.classList.add('text-primary');
        timerElement.classList.remove('text-danger', 'text-warning', 'text-success');
    }
}

// Export functions for use in other scripts
window.timerFunctions = {
    initializeTimer,
    startTimer,
    pauseTimer,
    resetTimer
};
