/**
 * WebSocket Client for Distributed Leaderboard System
 * 
 * This module handles WebSocket communication with the server.
 * 
 * Computer Networks Concepts:
 * - WebSocket Protocol (built on TCP)
 * - Full-duplex communication
 * - JSON message format
 * - Connection lifecycle management
 * 
 * Protocol:
 *   Client -> Server:
 *     {"type": "hello", "hostname": "BROWSER-USER"}
 *     {"type": "submit", "username": "player1", "score": 9.300}
 *   
 *   Server -> Client:
 *     {"type": "leaderboard", "data": [...]}
 */

// WebSocket connection
let ws = null;
let isConnected = false;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000;

// Server configuration
// Change this to server IP for LAN demo
const WS_HOST = window.location.hostname || 'localhost';
const WS_PORT = 8765;
const WS_URL = `ws://${WS_HOST}:${WS_PORT}`;

// Callbacks for game integration
let onLeaderboardUpdate = null;
let onConnectionChange = null;

/**
 * Initialize WebSocket connection
 */
function initWebSocket() {
    console.log(`[WS] Connecting to ${WS_URL}...`);
    updateConnectionStatus('connecting');
    
    try {
        ws = new WebSocket(WS_URL);
        
        // Connection opened
        ws.onopen = handleOpen;
        
        // Message received
        ws.onmessage = handleMessage;
        
        // Connection closed
        ws.onclose = handleClose;
        
        // Connection error
        ws.onerror = handleError;
        
    } catch (error) {
        console.error('[WS] Failed to create WebSocket:', error);
        updateConnectionStatus('disconnected');
        scheduleReconnect();
    }
}

/**
 * Handle WebSocket connection opened
 */
function handleOpen(event) {
    console.log('[WS] Connected to server');
    isConnected = true;
    reconnectAttempts = 0;
    updateConnectionStatus('connected');
    
    // Send hello message with hostname
    const hostname = `Browser-${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
    sendMessage({
        type: 'hello',
        hostname: hostname
    });
    
    // Notify callback
    if (onConnectionChange) {
        onConnectionChange(true);
    }
}

/**
 * Handle incoming WebSocket message
 */
function handleMessage(event) {
    try {
        const data = JSON.parse(event.data);
        console.log('[WS] Received:', data.type);
        
        switch (data.type) {
            case 'leaderboard':
                handleLeaderboardUpdate(data.data);
                break;
                
            case 'welcome':
                console.log('[WS] Welcome message received');
                break;
            
            case 'client_count':
                updateClientCount(data.count);
                break;
                
            default:
                console.log('[WS] Unknown message type:', data.type);
        }
        
    } catch (error) {
        console.error('[WS] Error parsing message:', error);
    }
}

/**
 * Handle leaderboard update from server
 */
function handleLeaderboardUpdate(leaderboardData) {
    console.log('[WS] Leaderboard update:', leaderboardData.length, 'entries');
    
    // Update client count from leaderboard size
    updateClientCount(leaderboardData.length);
    
    // Call the leaderboard update callback
    if (onLeaderboardUpdate) {
        onLeaderboardUpdate(leaderboardData);
    }
    
    // Also update via global function if available
    if (typeof updateLeaderboardDisplay === 'function') {
        updateLeaderboardDisplay(leaderboardData);
    }
}

/**
 * Update the client count display
 */
function updateClientCount(count) {
    const clientCountEl = document.getElementById('clientCount');
    if (clientCountEl) {
        clientCountEl.textContent = `Clients: ${count}`;
    }
}

/**
 * Handle WebSocket connection closed
 */
function handleClose(event) {
    console.log('[WS] Connection closed:', event.code, event.reason);
    isConnected = false;
    updateConnectionStatus('disconnected');
    
    // Notify callback
    if (onConnectionChange) {
        onConnectionChange(false);
    }
    
    // Attempt to reconnect
    scheduleReconnect();
}

/**
 * Handle WebSocket error
 */
function handleError(event) {
    console.error('[WS] Error:', event);
    updateConnectionStatus('disconnected');
}

/**
 * Schedule reconnection attempt
 */
function scheduleReconnect() {
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        console.log('[WS] Max reconnect attempts reached');
        updateConnectionStatus('failed');
        return;
    }
    
    reconnectAttempts++;
    console.log(`[WS] Reconnecting in ${RECONNECT_DELAY/1000}s (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
    
    setTimeout(() => {
        if (!isConnected) {
            initWebSocket();
        }
    }, RECONNECT_DELAY);
}

/**
 * Send message to server
 */
function sendMessage(data) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.error('[WS] Cannot send - not connected');
        return false;
    }
    
    try {
        ws.send(JSON.stringify(data));
        console.log('[WS] Sent:', data.type);
        return true;
    } catch (error) {
        console.error('[WS] Send error:', error);
        return false;
    }
}

/**
 * Submit a lap time to the server
 * @param {string} username - Player's username
 * @param {number} score - Lap time in seconds
 */
function submitLapTime(username, score) {
    if (!username || typeof score !== 'number') {
        console.error('[WS] Invalid lap time submission');
        return false;
    }
    
    return sendMessage({
        type: 'submit',
        username: username,
        score: parseFloat(score.toFixed(3))
    });
}

/**
 * Update connection status UI
 */
function updateConnectionStatus(status) {
    const statusElement = document.getElementById('connectionStatus');
    if (!statusElement) return;
    
    const dot = statusElement.querySelector('.status-dot');
    const text = statusElement.querySelector('.status-text');
    
    // Remove all status classes
    dot.classList.remove('connected', 'disconnected');
    
    switch (status) {
        case 'connected':
            dot.classList.add('connected');
            text.textContent = 'Connected';
            break;
            
        case 'connecting':
            dot.classList.add('disconnected');
            text.textContent = 'Connecting...';
            break;
            
        case 'disconnected':
            dot.classList.add('disconnected');
            text.textContent = 'Disconnected';
            break;
            
        case 'failed':
            dot.classList.add('disconnected');
            text.textContent = 'Connection failed';
            break;
    }
}

/**
 * Check if connected to server
 */
function isWebSocketConnected() {
    return isConnected && ws && ws.readyState === WebSocket.OPEN;
}

/**
 * Set callback for leaderboard updates
 */
function setLeaderboardCallback(callback) {
    onLeaderboardUpdate = callback;
}

/**
 * Set callback for connection state changes
 */
function setConnectionCallback(callback) {
    onConnectionChange = callback;
}

/**
 * Close WebSocket connection
 */
function closeWebSocket() {
    if (ws) {
        ws.close();
        ws = null;
    }
}

// Initialize WebSocket when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Small delay to ensure all scripts are loaded
    setTimeout(initWebSocket, 100);
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    closeWebSocket();
});
