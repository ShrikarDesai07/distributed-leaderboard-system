/**
 * Leaderboard Display Module for Distributed Leaderboard System
 * 
 * This module handles rendering and updating the leaderboard UI.
 * It receives updates from the WebSocket module and displays
 * the current rankings with animations.
 */

// Current leaderboard data
let leaderboardData = [];
let currentPlayerName = '';

/**
 * Update the leaderboard display with new data
 * @param {Array} data - Array of leaderboard entries
 */
function updateLeaderboardDisplay(data) {
    leaderboardData = data || [];
    renderLeaderboard();
    updatePlayerRank();
}

/**
 * Set the current player's name (for highlighting)
 * @param {string} name - Player's username
 */
function setCurrentPlayer(name) {
    currentPlayerName = name;
    renderLeaderboard();
    updatePlayerRank();
}

/**
 * Render the leaderboard HTML
 */
function renderLeaderboard() {
    const container = document.getElementById('leaderboardList');
    if (!container) return;
    
    // Empty state
    if (!leaderboardData || leaderboardData.length === 0) {
        container.innerHTML = `
            <div class="leaderboard-empty">
                Waiting for players...
            </div>
        `;
        return;
    }
    
    // Build leaderboard HTML
    let html = '';
    
    leaderboardData.forEach((entry, index) => {
        const rank = entry.rank || index + 1;
        const username = entry.username || 'Unknown';
        const score = entry.score || 0;
        
        // Determine CSS classes
        let entryClass = 'leaderboard-entry';
        let rankClass = 'entry-rank';
        
        // Highlight current player
        if (username.toLowerCase() === currentPlayerName.toLowerCase()) {
            entryClass += ' current-player';
        }
        
        // Top 3 styling
        if (rank <= 3) {
            entryClass += ' top-3';
            if (rank === 1) rankClass += ' gold';
            else if (rank === 2) rankClass += ' silver';
            else if (rank === 3) rankClass += ' bronze';
        }
        
        // Format time display
        const timeDisplay = formatTime(score);
        
        html += `
            <div class="${entryClass}" data-rank="${rank}">
                <span class="${rankClass}">${rank}.</span>
                <span class="entry-name">${escapeHtml(username)}</span>
                <span class="entry-time">${timeDisplay}</span>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Add animation to new entries
    animateNewEntries();
}

/**
 * Format time for display
 * @param {number} seconds - Time in seconds
 * @returns {string} Formatted time string
 */
function formatTime(seconds) {
    if (typeof seconds !== 'number' || isNaN(seconds)) {
        return '--:--';
    }
    
    // Round to 3 decimal places
    const rounded = Math.round(seconds * 1000) / 1000;
    
    // Format based on magnitude
    if (rounded >= 60) {
        const mins = Math.floor(rounded / 60);
        const secs = (rounded % 60).toFixed(3);
        return `${mins}:${secs.padStart(6, '0')}`;
    }
    
    return `${rounded.toFixed(3)}s`;
}

/**
 * Update the player's rank display
 */
function updatePlayerRank() {
    const rankDisplay = document.getElementById('yourRank');
    if (!rankDisplay) return;
    
    if (!currentPlayerName || leaderboardData.length === 0) {
        rankDisplay.textContent = 'Rank: --';
        return;
    }
    
    // Find player in leaderboard
    const playerEntry = leaderboardData.find(
        entry => entry.username.toLowerCase() === currentPlayerName.toLowerCase()
    );
    
    if (playerEntry) {
        rankDisplay.textContent = `Rank: #${playerEntry.rank}`;
        rankDisplay.style.color = getRankColor(playerEntry.rank);
    } else {
        rankDisplay.textContent = 'Rank: --';
    }
}

/**
 * Get color for rank display
 */
function getRankColor(rank) {
    if (rank === 1) return '#ffd700'; // Gold
    if (rank === 2) return '#c0c0c0'; // Silver
    if (rank === 3) return '#cd7f32'; // Bronze
    if (rank <= 10) return '#00ffff'; // Cyan for top 10
    return '#888899'; // Default gray
}

/**
 * Animate new/updated entries
 */
function animateNewEntries() {
    const entries = document.querySelectorAll('.leaderboard-entry');
    entries.forEach((entry, index) => {
        entry.style.opacity = '0';
        entry.style.transform = 'translateX(-10px)';
        
        setTimeout(() => {
            entry.style.transition = 'all 0.3s ease';
            entry.style.opacity = '1';
            entry.style.transform = 'translateX(0)';
        }, index * 50);
    });
}

/**
 * Get player's best time from leaderboard
 * @param {string} username - Player's username
 * @returns {number|null} Best time or null if not found
 */
function getPlayerBestTime(username) {
    if (!username || leaderboardData.length === 0) return null;
    
    const entry = leaderboardData.find(
        e => e.username.toLowerCase() === username.toLowerCase()
    );
    
    return entry ? entry.score : null;
}

/**
 * Get player's rank from leaderboard
 * @param {string} username - Player's username
 * @returns {number|null} Rank or null if not found
 */
function getPlayerRank(username) {
    if (!username || leaderboardData.length === 0) return null;
    
    const entry = leaderboardData.find(
        e => e.username.toLowerCase() === username.toLowerCase()
    );
    
    return entry ? entry.rank : null;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show lap completion message
 * @param {number} lapTime - The completed lap time
 * @param {boolean} isNewBest - Whether this is a new personal best
 */
function showLapMessage(lapTime, isNewBest) {
    const messageEl = document.getElementById('lapMessage');
    if (!messageEl) return;
    
    const timeStr = formatTime(lapTime);
    
    if (isNewBest) {
        messageEl.innerHTML = `NEW BEST!<br>${timeStr}`;
        messageEl.style.color = '#00ff88';
    } else {
        messageEl.innerHTML = `LAP: ${timeStr}`;
        messageEl.style.color = '#ffffff';
    }
    
    messageEl.classList.add('show');
    
    // Hide after 2 seconds
    setTimeout(() => {
        messageEl.classList.remove('show');
    }, 2000);
}

/**
 * Update personal best display
 * @param {number} time - Best lap time
 */
function updatePersonalBest(time) {
    const bestEl = document.getElementById('personalBest');
    if (bestEl) {
        bestEl.textContent = formatTime(time);
    }
}

/**
 * Update previous time display
 * @param {number} time - Previous lap time
 */
function updatePreviousTime(time) {
    const prevEl = document.getElementById('previousTime');
    if (prevEl) {
        prevEl.textContent = formatTime(time);
    }
}
