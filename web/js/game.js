/**
 * Racing Game Module for Distributed Leaderboard System
 * 
 * A simple 2D racing game inspired by HotlapDaily.
 * Players drive around a track and their lap times are submitted
 * to the distributed leaderboard.
 * 
 * Controls:
 * - Arrow keys: Steer left/right
 * - Up arrow: Accelerate
 * - Space: Start race
 * 
 * Rules:
 * - Go off track = DNF (Did Not Finish)
 * - Complete lap by crossing finish line
 */

// =============================================================================
// GAME CONSTANTS
// =============================================================================

const GAME_CONFIG = {
    // Canvas
    WIDTH: 600,
    HEIGHT: 500,
    
    // Car physics
    MAX_SPEED: 3,
    ACCELERATION: 0.15,
    DECELERATION: 0.05,
    FRICTION: 0.02,
    TURN_SPEED: 0.06,
    
    // Track
    TRACK_COLOR: '#3a3a4a',
    TRACK_BORDER: '#2a2a3a',
    GRASS_COLOR: '#1a1a2a',
    FINISH_LINE_WIDTH: 40,
    
    // Car
    CAR_WIDTH: 16,
    CAR_HEIGHT: 28,
    CAR_COLORS: ['#ff3366', '#00ffff', '#00ff88', '#ffff00', '#ff8800']
};

// =============================================================================
// GAME STATE
// =============================================================================

let canvas, ctx;
let gameState = 'waiting'; // waiting, racing, dnf
let car = null;
let track = null;
let timer = 0;
let lastTime = 0;
let lapStartTime = 0;
let personalBest = null;
let previousLapTime = null;
let playerName = '';
let isDNF = false;

// Input state
const keys = {
    left: false,
    right: false,
    up: false,
    down: false
};

// =============================================================================
// TRACK DEFINITION - Similar to HotlapDaily layout
// =============================================================================

// Track is defined as a series of points forming the center line
// The car must stay within the track boundaries

const TRACK_POINTS = [
    // Start/Finish area (right side, vertical section going UP)
    { x: 480, y: 420 },
    { x: 480, y: 360 },
    
    // Going up on the right
    { x: 475, y: 300 },
    { x: 460, y: 240 },
    
    // Top right curve
    { x: 430, y: 180 },
    { x: 380, y: 140 },
    { x: 320, y: 110 },
    
    // Top section going left
    { x: 250, y: 100 },
    { x: 180, y: 110 },
    
    // Top left curve going down
    { x: 120, y: 140 },
    { x: 90, y: 200 },
    { x: 85, y: 270 },
    
    // Left side going down
    { x: 100, y: 340 },
    { x: 130, y: 390 },
    
    // Bottom S-curve
    { x: 180, y: 420 },
    { x: 240, y: 400 },
    { x: 300, y: 420 },
    { x: 360, y: 400 },
    { x: 420, y: 430 },
    
    // Back to start/finish
    { x: 480, y: 420 }
];

const TRACK_WIDTH = 55;

// Finish line position (horizontal line on the right side)
const FINISH_LINE = {
    x1: 455,  // left edge
    x2: 505,  // right edge
    y: 420    // y position
};

// Starting position (just before finish line, facing UP)
const START_POSITION = {
    x: 480,
    y: 440,
    angle: -Math.PI / 2  // Facing UP (north)
};

// =============================================================================
// CAR CLASS
// =============================================================================

class Car {
    constructor(x, y, angle) {
        this.x = x;
        this.y = y;
        this.angle = angle;
        this.speed = 0;
        this.color = GAME_CONFIG.CAR_COLORS[Math.floor(Math.random() * GAME_CONFIG.CAR_COLORS.length)];
        this.width = GAME_CONFIG.CAR_WIDTH;
        this.height = GAME_CONFIG.CAR_HEIGHT;
        this.crossedFinish = false;
        this.hasStartedLap = false;  // Track if car has moved away from start
    }
    
    update(deltaTime) {
        // Frame-rate independent multiplier (normalize to 60 FPS)
        const dt = deltaTime * 60;
        
        // Handle acceleration
        if (keys.up) {
            this.speed += GAME_CONFIG.ACCELERATION * dt;
        } else {
            this.speed -= GAME_CONFIG.DECELERATION * dt;
        }
        
        // Apply friction
        this.speed -= GAME_CONFIG.FRICTION * dt;
        
        // Clamp speed
        this.speed = Math.max(0, Math.min(GAME_CONFIG.MAX_SPEED, this.speed));
        
        // Handle turning (only when moving)
        if (this.speed > 0.1) {
            if (keys.left) {
                this.angle -= GAME_CONFIG.TURN_SPEED * (this.speed / GAME_CONFIG.MAX_SPEED) * dt;
            }
            if (keys.right) {
                this.angle += GAME_CONFIG.TURN_SPEED * (this.speed / GAME_CONFIG.MAX_SPEED) * dt;
            }
        }
        
        // Update position (frame-rate independent)
        this.x += Math.cos(this.angle) * this.speed * dt;
        this.y += Math.sin(this.angle) * this.speed * dt;
        
        // Keep car in bounds
        this.x = Math.max(20, Math.min(GAME_CONFIG.WIDTH - 20, this.x));
        this.y = Math.max(20, Math.min(GAME_CONFIG.HEIGHT - 20, this.y));
        
        // Track if car has moved away from start area
        if (!this.hasStartedLap && this.y < 400) {
            this.hasStartedLap = true;
        }
        
        // Check track boundaries - DNF if off track
        return this.isOnTrack();
    }
    
    draw(ctx) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle + Math.PI / 2);
        
        // Car body
        ctx.fillStyle = this.color;
        ctx.fillRect(-this.width / 2, -this.height / 2, this.width, this.height);
        
        // Windshield (front of car)
        ctx.fillStyle = '#1a1a2a';
        ctx.fillRect(-this.width / 2 + 2, -this.height / 2 + 3, this.width - 4, 8);
        
        // Racing stripe
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(-1.5, -this.height / 2, 3, this.height);
        
        ctx.restore();
    }
    
    isOnTrack() {
        // Simple distance check to track center line
        let minDist = Infinity;
        
        for (let i = 0; i < TRACK_POINTS.length - 1; i++) {
            const dist = this.distToSegment(
                this.x, this.y,
                TRACK_POINTS[i].x, TRACK_POINTS[i].y,
                TRACK_POINTS[i + 1].x, TRACK_POINTS[i + 1].y
            );
            minDist = Math.min(minDist, dist);
        }
        
        return minDist < TRACK_WIDTH / 2;
    }
    
    distToSegment(px, py, x1, y1, x2, y2) {
        const dx = x2 - x1;
        const dy = y2 - y1;
        const len2 = dx * dx + dy * dy;
        
        if (len2 === 0) return Math.hypot(px - x1, py - y1);
        
        let t = ((px - x1) * dx + (py - y1) * dy) / len2;
        t = Math.max(0, Math.min(1, t));
        
        return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy));
    }
    
    checkFinishLine() {
        // Check if car crossed finish line (horizontal line)
        const nearFinish = this.x > FINISH_LINE.x1 && 
                          this.x < FINISH_LINE.x2 && 
                          Math.abs(this.y - FINISH_LINE.y) < 20;
        
        // Must be going upward (negative y direction) and have completed lap
        const goingUp = Math.sin(this.angle) < -0.3;
        
        if (nearFinish && !this.crossedFinish && this.speed > 0.5 && goingUp && this.hasStartedLap) {
            this.crossedFinish = true;
            return true;
        } else if (!nearFinish) {
            this.crossedFinish = false;
        }
        
        return false;
    }
    
    reset() {
        this.x = START_POSITION.x;
        this.y = START_POSITION.y;
        this.angle = START_POSITION.angle;
        this.speed = 0;
        this.crossedFinish = false;
        this.hasStartedLap = false;
    }
}

// =============================================================================
// TRACK RENDERING
// =============================================================================

function drawTrack(ctx) {
    // Draw grass/off-track background
    ctx.fillStyle = GAME_CONFIG.GRASS_COLOR;
    ctx.fillRect(0, 0, GAME_CONFIG.WIDTH, GAME_CONFIG.HEIGHT);
    
    // Draw grid pattern
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
    ctx.lineWidth = 1;
    for (let x = 0; x < GAME_CONFIG.WIDTH; x += 50) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, GAME_CONFIG.HEIGHT);
        ctx.stroke();
    }
    for (let y = 0; y < GAME_CONFIG.HEIGHT; y += 50) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(GAME_CONFIG.WIDTH, y);
        ctx.stroke();
    }
    
    // Draw track border (outer)
    ctx.strokeStyle = GAME_CONFIG.TRACK_BORDER;
    ctx.lineWidth = TRACK_WIDTH + 6;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    ctx.beginPath();
    ctx.moveTo(TRACK_POINTS[0].x, TRACK_POINTS[0].y);
    for (let i = 1; i < TRACK_POINTS.length; i++) {
        ctx.lineTo(TRACK_POINTS[i].x, TRACK_POINTS[i].y);
    }
    ctx.stroke();
    
    // Draw main track
    ctx.strokeStyle = GAME_CONFIG.TRACK_COLOR;
    ctx.lineWidth = TRACK_WIDTH;
    
    ctx.beginPath();
    ctx.moveTo(TRACK_POINTS[0].x, TRACK_POINTS[0].y);
    for (let i = 1; i < TRACK_POINTS.length; i++) {
        ctx.lineTo(TRACK_POINTS[i].x, TRACK_POINTS[i].y);
    }
    ctx.stroke();
    
    // Draw finish line
    drawFinishLine(ctx);
    
    // Draw direction arrows on track
    drawTrackArrows(ctx);
}

function drawFinishLine(ctx) {
    const x1 = FINISH_LINE.x1;
    const x2 = FINISH_LINE.x2;
    const y = FINISH_LINE.y;
    const height = 30;
    
    // Checkered pattern (horizontal finish line)
    const squareSize = 8;
    const numSquaresX = Math.floor((x2 - x1) / squareSize);
    const numSquaresY = Math.floor(height / squareSize);
    
    for (let i = 0; i < numSquaresX; i++) {
        for (let j = 0; j < numSquaresY; j++) {
            ctx.fillStyle = (i + j) % 2 === 0 ? '#ffffff' : '#000000';
            ctx.fillRect(
                x1 + i * squareSize,
                y - height / 2 + j * squareSize,
                squareSize,
                squareSize
            );
        }
    }
}

function drawTrackArrows(ctx) {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.12)';
    
    // Draw small arrows along the track
    for (let i = 0; i < TRACK_POINTS.length - 1; i += 2) {
        const p1 = TRACK_POINTS[i];
        const p2 = TRACK_POINTS[i + 1];
        const mx = (p1.x + p2.x) / 2;
        const my = (p1.y + p2.y) / 2;
        const angle = Math.atan2(p2.y - p1.y, p2.x - p1.x);
        
        ctx.save();
        ctx.translate(mx, my);
        ctx.rotate(angle);
        
        // Arrow shape
        ctx.beginPath();
        ctx.moveTo(8, 0);
        ctx.lineTo(-4, -5);
        ctx.lineTo(-4, 5);
        ctx.closePath();
        ctx.fill();
        
        ctx.restore();
    }
}

// =============================================================================
// GAME LOOP
// =============================================================================

function gameLoop(currentTime) {
    // Calculate delta time
    const deltaTime = (currentTime - lastTime) / 1000;
    lastTime = currentTime;
    
    // Update
    update(deltaTime);
    
    // Render
    render();
    
    // Continue loop
    requestAnimationFrame(gameLoop);
}

function update(deltaTime) {
    if (gameState === 'racing') {
        // Update timer
        timer = (performance.now() - lapStartTime) / 1000;
        updateTimerDisplay();
        
        // Update car and check if on track
        const onTrack = car.update(deltaTime);
        
        // DNF if off track
        if (!onTrack) {
            triggerDNF();
            return;
        }
        
        // Check finish line
        if (car.checkFinishLine()) {
            completeLap();
        }
    }
}

function render() {
    // Clear canvas
    ctx.clearRect(0, 0, GAME_CONFIG.WIDTH, GAME_CONFIG.HEIGHT);
    
    // Draw track
    drawTrack(ctx);
    
    // Draw car
    if (car) {
        car.draw(ctx);
    }
    
    // Draw game state overlays
    if (gameState === 'waiting') {
        drawWaitingOverlay();
    } else if (gameState === 'dnf') {
        drawDNFOverlay();
    }
}

function drawWaitingOverlay() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, GAME_CONFIG.WIDTH, GAME_CONFIG.HEIGHT);
    
    ctx.fillStyle = '#ffffff';
    ctx.font = '16px "Press Start 2P", cursive';
    ctx.textAlign = 'center';
    ctx.fillText('PRESS SPACE TO START', GAME_CONFIG.WIDTH / 2, GAME_CONFIG.HEIGHT / 2);
    
    ctx.font = '12px "Orbitron", sans-serif';
    ctx.fillStyle = '#888888';
    ctx.fillText('Use arrow keys to drive', GAME_CONFIG.WIDTH / 2, GAME_CONFIG.HEIGHT / 2 + 40);
}

function drawDNFOverlay() {
    // Semi-transparent overlay
    ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
    ctx.fillRect(0, 0, GAME_CONFIG.WIDTH, GAME_CONFIG.HEIGHT);
    
    // DNF text
    ctx.fillStyle = '#ff3366';
    ctx.font = '32px "Press Start 2P", cursive';
    ctx.textAlign = 'center';
    ctx.fillText('DNF', GAME_CONFIG.WIDTH / 2, GAME_CONFIG.HEIGHT / 2 - 20);
    
    ctx.font = '12px "Orbitron", sans-serif';
    ctx.fillStyle = '#ffffff';
    ctx.fillText('You went off track!', GAME_CONFIG.WIDTH / 2, GAME_CONFIG.HEIGHT / 2 + 20);
    
    ctx.fillStyle = '#888888';
    ctx.fillText('Press SPACE to try again', GAME_CONFIG.WIDTH / 2, GAME_CONFIG.HEIGHT / 2 + 50);
}

// =============================================================================
// GAME CONTROLS
// =============================================================================

function triggerDNF() {
    gameState = 'dnf';
    isDNF = true;
    
    // Update timer display to show DNF
    const timerEl = document.getElementById('timerDisplay');
    if (timerEl) {
        timerEl.textContent = timer.toFixed(3) + ' (DNF)';
        timerEl.style.color = '#ff3366';
    }
    
    // Show DNF message
    showMessage('DNF', '#ff3366');
}

function startRace() {
    if (gameState !== 'waiting' && gameState !== 'dnf') return;
    
    // Get player name
    const nameInput = document.getElementById('playerName');
    playerName = nameInput ? nameInput.value.trim() : '';
    
    if (!playerName) {
        playerName = 'Player' + Math.floor(Math.random() * 1000);
        if (nameInput) nameInput.value = playerName;
    }
    
    // Update leaderboard module
    setCurrentPlayer(playerName);
    
    // Reset DNF state
    isDNF = false;
    
    // Reset timer display color
    const timerEl = document.getElementById('timerDisplay');
    if (timerEl) {
        timerEl.style.color = '#ffffff';
    }
    
    // Initialize car at start position
    car = new Car(START_POSITION.x, START_POSITION.y, START_POSITION.angle);
    
    // Start racing immediately
    gameState = 'racing';
    lapStartTime = performance.now();
    timer = 0;
    
    // Brief "GO!" message
    showMessage('GO!', '#00ff88');
    setTimeout(() => {
        hideMessage();
    }, 500);
}

function completeLap() {
    const lapTime = timer;
    
    // Check if new personal best
    const isNewBest = personalBest === null || lapTime < personalBest;
    
    if (isNewBest) {
        personalBest = lapTime;
        updatePersonalBest(lapTime);
    }
    
    // Update previous time
    previousLapTime = lapTime;
    updatePreviousTime(lapTime);
    
    // Show lap message
    showLapMessage(lapTime, isNewBest);
    
    // Submit to server
    submitLapTime(playerName, lapTime);
    
    // Reset for next lap
    gameState = 'waiting';
    car.reset();
    timer = 0;
    updateTimerDisplay();
}

function updateTimerDisplay() {
    const timerEl = document.getElementById('timerDisplay');
    if (timerEl) {
        timerEl.textContent = timer.toFixed(3);
    }
}

function showMessage(text, color = '#ffffff') {
    const msgEl = document.getElementById('lapMessage');
    if (msgEl) {
        msgEl.textContent = text;
        msgEl.style.color = color;
        msgEl.classList.add('show');
    }
}

function hideMessage() {
    const msgEl = document.getElementById('lapMessage');
    if (msgEl) {
        msgEl.classList.remove('show');
    }
}

// =============================================================================
// INPUT HANDLING
// =============================================================================

function handleKeyDown(e) {
    switch (e.code) {
        case 'ArrowLeft':
            keys.left = true;
            e.preventDefault();
            break;
        case 'ArrowRight':
            keys.right = true;
            e.preventDefault();
            break;
        case 'ArrowUp':
            keys.up = true;
            e.preventDefault();
            break;
        case 'ArrowDown':
            keys.down = true;
            e.preventDefault();
            break;
        case 'Space':
            if (gameState === 'waiting' || gameState === 'dnf') {
                startRace();
            }
            e.preventDefault();
            break;
    }
}

function handleKeyUp(e) {
    switch (e.code) {
        case 'ArrowLeft':
            keys.left = false;
            break;
        case 'ArrowRight':
            keys.right = false;
            break;
        case 'ArrowUp':
            keys.up = false;
            break;
        case 'ArrowDown':
            keys.down = false;
            break;
    }
}

// =============================================================================
// INITIALIZATION
// =============================================================================

function initGame() {
    // Get canvas
    canvas = document.getElementById('gameCanvas');
    if (!canvas) {
        console.error('Canvas not found!');
        return;
    }
    
    ctx = canvas.getContext('2d');
    
    // Set canvas size
    canvas.width = GAME_CONFIG.WIDTH;
    canvas.height = GAME_CONFIG.HEIGHT;
    
    // Initialize car at start position
    car = new Car(START_POSITION.x, START_POSITION.y, START_POSITION.angle);
    
    // Set up input handlers
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
    
    // Start button click handler
    const startBtn = document.getElementById('startButton');
    if (startBtn) {
        startBtn.addEventListener('click', startRace);
    }
    
    // Name input handler
    const nameInput = document.getElementById('playerName');
    if (nameInput) {
        nameInput.addEventListener('change', () => {
            playerName = nameInput.value.trim();
            setCurrentPlayer(playerName);
        });
    }
    
    // Start game loop
    lastTime = performance.now();
    requestAnimationFrame(gameLoop);
    
    console.log('[Game] Initialized');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initGame);
