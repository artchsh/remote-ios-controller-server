// Controller app
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const connectionStatus = document.getElementById('connection-status');
    const resetButton = document.getElementById('reset-button');
    
    // Hardcoded server address
    const SERVER_ADDRESS = '192.168.1.39:8000';
    
    // Controller buttons
    const buttons = [
        'up', 'down', 'left', 'right',
        'a', 'b', 'x', 'y',
        'lb', 'rb',
        'start', 'select', 'home'
    ];
    
    // WebSocket connection
    let socket = null;
    let isConnected = false;
    let serverBaseUrl = '';
    
    // Analog stick variables
    let leftStickActive = false;
    let rightStickActive = false;
    const leftStick = document.getElementById('left-stick');
    const rightStick = document.getElementById('right-stick');
    const leftStickBase = document.querySelector('.left-stick .analog-base');
    const rightStickBase = document.querySelector('.right-stick .analog-base');
    
    // Analog stick max range (from center)
    const maxRange = 32767;
    
    // Connect to WebSocket server
    function connectToServer() {
        // Close existing connection if any
        if (socket) {
            socket.close();
        }
        
        // Create new WebSocket connection
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            let wsUrl = SERVER_ADDRESS;
            
            // Add protocol if not present
            if (!wsUrl.startsWith('ws://') && !wsUrl.startsWith('wss://')) {
                wsUrl = protocol + wsUrl;
            }
            
            // Store base URL for API calls
            serverBaseUrl = wsUrl.replace(/\/ws$/, '');
            if (serverBaseUrl.startsWith('ws://')) {
                serverBaseUrl = 'http://' + serverBaseUrl.substring(5);
            } else if (serverBaseUrl.startsWith('wss://')) {
                serverBaseUrl = 'https://' + serverBaseUrl.substring(6);
            }
            
            // Add /ws endpoint if not present
            if (!wsUrl.endsWith('/ws')) {
                wsUrl = wsUrl + '/ws';
            }
            
            socket = new WebSocket(wsUrl);
            
            // WebSocket event handlers
            socket.onopen = () => {
                console.log('Connected to server');
                connectionStatus.textContent = 'Connected';
                connectionStatus.classList.remove('disconnected');
                connectionStatus.classList.add('connected');
                isConnected = true;
                resetButton.disabled = false;
            };
            
            socket.onclose = () => {
                console.log('Disconnected from server');
                connectionStatus.textContent = 'Disconnected';
                connectionStatus.classList.remove('connected');
                connectionStatus.classList.add('disconnected');
                isConnected = false;
                resetButton.disabled = true;
            };
            
            socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                connectionStatus.textContent = 'Error';
                connectionStatus.classList.remove('connected');
                connectionStatus.classList.add('disconnected');
                isConnected = false;
                resetButton.disabled = true;
            };
            
            socket.onmessage = (event) => {
                console.log('Message from server:', event.data);
                try {
                    const response = JSON.parse(event.data);
                    if (response.status === 'error') {
                        console.error('Server error:', response.message);
                    }
                } catch (e) {
                    console.error('Error parsing server message:', e);
                }
            };
        } catch (error) {
            console.error('Connection error:', error);
            alert('Failed to connect to server: ' + error.message);
        }
    }
    
    // Reset controller state
    function resetController() {
        if (!serverBaseUrl) {
            alert('Please connect to a server first');
            return;
        }
        
        fetch(`${serverBaseUrl}/reset`)
            .then(response => response.json())
            .then(data => {
                console.log('Reset response:', data);
                if (data.status === 'success') {
                    console.log('Controller reset successfully');
                } else {
                    console.error('Failed to reset controller: ' + (data.message || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Reset error:', error);
                alert('Failed to reset controller: ' + error.message);
            });
    }
    
    // Send button press/release to server
    function sendButtonAction(button, action) {
        if (!isConnected || !socket) {
            return;
        }
        console.log("Sending button action:", button, action); // Added log
        try {
            const message = JSON.stringify({
                button: button,
                action: action
            });
            socket.send(message);
        } catch (error) {
            console.error('Error sending button action:', error);
        }
    }
    
    // Send analog stick position to server
    function sendAnalogPosition(stick, x, y) {
        if (!isConnected || !socket) {
            return;
        }
        
        try {
            const message = JSON.stringify({
                stick: stick,
                x: x,
                y: y
            });
            socket.send(message);
        } catch (error) {
            console.error('Error sending analog position:', error);
        }
    }
    
    // Handle stick movement based on touch/mouse position
    function handleStickMovement(stick, stickElement, baseElement, clientX, clientY) {
        const baseBounds = baseElement.getBoundingClientRect();
        const baseRadius = baseBounds.width / 2;
        const stickRadius = stickElement.offsetWidth / 2;
        
        // Calculate position relative to center of base
        let x = clientX - (baseBounds.left + baseRadius);
        let y = clientY - (baseBounds.top + baseRadius);
        
        // Calculate distance from center
        const distance = Math.sqrt(x * x + y * y);
        
        // Limit movement to the base radius
        if (distance > baseRadius - stickRadius) {
            const angle = Math.atan2(y, x);
            x = (baseRadius - stickRadius) * Math.cos(angle);
            y = (baseRadius - stickRadius) * Math.sin(angle);
        }
        
        // Move the stick
        stickElement.style.transform = `translate(${x}px, ${y}px)`;
        
        // Normalize coordinates to -1 to 1 range
        const normalizedX = x / (baseRadius - stickRadius);
        const normalizedY = y / (baseRadius - stickRadius);
        
        // Convert to Xbox 360 controller range (-32767 to 32767)
        const xbox360X = Math.round(normalizedX * maxRange);
        const xbox360Y = Math.round(normalizedY * maxRange);
        
        // Send to server
        sendAnalogPosition(stick, xbox360X, xbox360Y);
    }
    
    // Reset stick position
    function resetStickPosition(stick, stickElement) {
        stickElement.style.transform = 'translate(0px, 0px)';
        if (isConnected) {
            sendAnalogPosition(stick, 0, 0);
        }
    }
    
    // Set up analog sticks
    if (leftStick && leftStickBase) {
        // Left stick touch events
        leftStickBase.addEventListener('touchstart', (e) => {
            e.preventDefault();
            leftStickActive = true;
            handleStickMovement('left_stick', leftStick, leftStickBase, e.touches[0].clientX, e.touches[0].clientY);
        });
        
        leftStickBase.addEventListener('touchmove', (e) => {
            if (leftStickActive) {
                e.preventDefault();
                handleStickMovement('left_stick', leftStick, leftStickBase, e.touches[0].clientX, e.touches[0].clientY);
            }
        });
        
        leftStickBase.addEventListener('touchend', (e) => {
            e.preventDefault();
            leftStickActive = false;
            resetStickPosition('left_stick', leftStick);
        });
        
        // Left stick mouse events
        leftStickBase.addEventListener('mousedown', (e) => {
            leftStickActive = true;
            handleStickMovement('left_stick', leftStick, leftStickBase, e.clientX, e.clientY);
        });
        
        document.addEventListener('mousemove', (e) => {
            if (leftStickActive) {
                handleStickMovement('left_stick', leftStick, leftStickBase, e.clientX, e.clientY);
            }
        });
        
        document.addEventListener('mouseup', () => {
            if (leftStickActive) {
                leftStickActive = false;
                resetStickPosition('left_stick', leftStick);
            }
        });
    }
    
    if (rightStick && rightStickBase) {
        // Right stick touch events
        rightStickBase.addEventListener('touchstart', (e) => {
            e.preventDefault();
            rightStickActive = true;
            handleStickMovement('right_stick', rightStick, rightStickBase, e.touches[0].clientX, e.touches[0].clientY);
        });
        
        rightStickBase.addEventListener('touchmove', (e) => {
            if (rightStickActive) {
                e.preventDefault();
                handleStickMovement('right_stick', rightStick, rightStickBase, e.touches[0].clientX, e.touches[0].clientY);
            }
        });
        
        rightStickBase.addEventListener('touchend', (e) => {
            e.preventDefault();
            rightStickActive = false;
            resetStickPosition('right_stick', rightStick);
        });
        
        // Right stick mouse events
        rightStickBase.addEventListener('mousedown', (e) => {
            rightStickActive = true;
            handleStickMovement('right_stick', rightStick, rightStickBase, e.clientX, e.clientY);
        });
        
        document.addEventListener('mousemove', (e) => {
            if (rightStickActive) {
                handleStickMovement('right_stick', rightStick, rightStickBase, e.clientX, e.clientY);
            }
        });
        
        document.addEventListener('mouseup', () => {
            if (rightStickActive) {
                rightStickActive = false;
                resetStickPosition('right_stick', rightStick);
            }
        });
    }
    
    // Set up button event listeners
    buttons.forEach(buttonId => {
        const buttonElement = document.getElementById(buttonId);
        if (buttonElement) {
            // Touch events for mobile
            buttonElement.addEventListener('touchstart', (e) => {
                e.preventDefault();
                buttonElement.classList.add('active');
                sendButtonAction(buttonId, 'press');
            });
            
            buttonElement.addEventListener('touchend', (e) => {
                e.preventDefault();
                buttonElement.classList.remove('active');
                sendButtonAction(buttonId, 'release');
            });
            
            // Mouse events for desktop
            buttonElement.addEventListener('mousedown', () => {
                buttonElement.classList.add('active');
                sendButtonAction(buttonId, 'press');
            });
            
            buttonElement.addEventListener('mouseup', () => {
                buttonElement.classList.remove('active');
                sendButtonAction(buttonId, 'release');
            });
            
            buttonElement.addEventListener('mouseleave', () => {
                if (buttonElement.classList.contains('active')) {
                    buttonElement.classList.remove('active');
                    sendButtonAction(buttonId, 'release');
                }
            });
            
            // Prevent context menu on right-click
            buttonElement.addEventListener('contextmenu', (e) => {
                e.preventDefault();
            });
        }
    });
    
    // Add LT/RT event listeners
    const ltButton = document.getElementById('lt');
    const rtButton = document.getElementById('rt');
    if (ltButton) {
        ltButton.addEventListener('touchstart', e => {
            e.preventDefault();
            sendTriggerAction('lt', 255);
        });
        ltButton.addEventListener('touchend', e => {
            e.preventDefault();
            sendTriggerAction('lt', 0);
        });
        ltButton.addEventListener('mousedown', () => {
            sendTriggerAction('lt', 255);
        });
        ltButton.addEventListener('mouseup', () => {
            sendTriggerAction('lt', 0);
        });
    }
    if (rtButton) {
        rtButton.addEventListener('touchstart', e => {
            e.preventDefault();
            sendTriggerAction('rt', 255);
        });
        rtButton.addEventListener('touchend', e => {
            e.preventDefault();
            sendTriggerAction('rt', 0);
        });
        rtButton.addEventListener('mousedown', () => {
            sendTriggerAction('rt', 255);
        });
        rtButton.addEventListener('mouseup', () => {
            sendTriggerAction('rt', 0);
        });
    }
    
    // Function to send trigger values
    function sendTriggerAction(trigger, value) {
        if (!isConnected || !socket) return;
        try {
            const message = JSON.stringify({
                trigger: trigger,
                value: value
            });
            socket.send(message);
        } catch (error) {
            console.error('Error sending trigger action:', error);
        }
    }
    
    // Reset button event listener
    resetButton.addEventListener('click', resetController);
    
    // Disable reset button initially
    resetButton.disabled = true;
    
    // Ping server periodically to keep connection alive
    setInterval(() => {
        if (isConnected && socket) {
            try {
                socket.send(JSON.stringify({ ping: true }));
            } catch (error) {
                console.error('Error sending ping:', error);
            }
        }
    }, 30000); // Every 30 seconds
    
    // Lock screen orientation to landscape if possible
    if (screen.orientation && screen.orientation.lock) {
        try {
            screen.orientation.lock('landscape');
        } catch (error) {
            console.error('Could not lock screen orientation:', error);
        }
    }
    
    // Auto-connect on page load
    connectToServer();
});