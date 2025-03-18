from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import threading
import vgamepad as vg

SERVER_IP = '0.0.0.0'
SERVER_PORT = 8000

# Initialize FastAPI app
app = FastAPI(title="Xbox 360 Controller")

# Add CORS middleware to allow requests from the PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vGamepad controller
gamepad = vg.VX360Gamepad()

# Xbox 360 button mapping to vGamepad buttons
BUTTON_MAPPING = {
    "a": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    "b": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    "x": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    "y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    "lb": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    "rb": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "start": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
    "back": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
    "home": vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE,
}

# D-pad mapping to vGamepad buttons
DPAD_MAPPING = {
    "up": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
    "right": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    "down": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    "left": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
}

# Lock for thread safety
controller_lock = threading.Lock()

@app.get("/")
async def read_root():
    return {"message": "Xbox 360 Controller API is running"}

@app.get("/ping")
async def ping():
    return {"status": "online"}

# Function to reset gamepad
def reset_gamepad():
    for btn in BUTTON_MAPPING.values():
        gamepad.release_button(btn)
    # Center sticks and triggers
    gamepad.left_joystick(0, 0)
    gamepad.right_joystick(0, 0)
    gamepad.left_trigger(0)
    gamepad.right_trigger(0)
    gamepad.update()

@app.get("/reset")
async def reset_controller():
    with controller_lock:
        reset_gamepad()
    return {"status": "success", "message": "Controller reset"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                
                # Handle ping messages
                if "ping" in message_data:
                    await websocket.send_text(json.dumps({"status": "pong"}))
                    continue
                
                with controller_lock:
                    print(f"Received message: {message_data}")  # Debug log
                    # Handle button press/release
                    if "button" in message_data and "action" in message_data:
                        button = message_data.get("button")
                        action = message_data.get("action")  # "press" or "release"
                        print(f"Received button: {button}, action: {action}")  # Debug log
                        
                        # Handle D-pad (POV hat)
                        if button in DPAD_MAPPING:
                            if action == "press":
                                gamepad.press_button(DPAD_MAPPING[button])
                            elif action == "release":
                                gamepad.release_button(DPAD_MAPPING[button])
                            gamepad.update()
                            await websocket.send_text(json.dumps({"status": "success"}))
                        
                        # Handle regular buttons
                        elif button in BUTTON_MAPPING:
                            if action == "press":
                                gamepad.press_button(BUTTON_MAPPING[button])
                            elif action == "release":
                                gamepad.release_button(BUTTON_MAPPING[button])
                            gamepad.update()
                            await websocket.send_text(json.dumps({"status": "success"}))
                        else:
                            await websocket.send_text(json.dumps({"status": "error", "message": "Invalid button"}))
                            
                        if button in ["lt", "rt"]:
                            if action == "press":
                                gamepad.left_trigger(255) if button == "lt" else gamepad.right_trigger(255)
                            elif action == "release":
                                gamepad.left_trigger(0) if button == "lt" else gamepad.right_trigger(0)
                            gamepad.update()
                            await websocket.send_text(json.dumps({"status": "success"}))
                            
                        if button in ["rs", "ls"]:
                            if action == "press":
                                gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB) if button == "ls" else gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
                            elif action == "release":
                                gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB) if button == "ls" else gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
                            gamepad.update()
                            await websocket.send_text(json.dumps({"status": "success"}))

                    
                    # Handle analog stick movement
                    elif "stick" in message_data and "x" in message_data and "y" in message_data:
                        stick = message_data.get("stick")
                        x_value = message_data.get("x")
                        y_value = message_data.get("y")
                        print(f"1: Received stick: {stick}, x: {x_value}, y: {y_value}")  # Debug log
                        
                        if stick == "left" or stick == "right":
                            x_value = max(-32768, min(32767, x_value))
                            y_value = max(-32768, min(32767, y_value))
                            print(f"2: Received stick: {stick}, x: {x_value}, y: {y_value}")  # Debug log
                            
                            if stick == "left":
                                gamepad.left_joystick(x_value, -y_value)
                            else:
                                gamepad.right_joystick(x_value, -y_value)
                            gamepad.update()
                        await websocket.send_text(json.dumps({"status": "success"}))
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"status": "error", "message": "Invalid JSON"}))
            except Exception as e:
                print(f"Error processing message: {e}")
                await websocket.send_text(json.dumps({"status": "error", "message": str(e)}))
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    print("Starting Xbox 360 Controller API...")
    print(f"Server running at http://{SERVER_IP}:{SERVER_PORT}")
    print("Make sure vJoy is installed and configured properly")
    uvicorn.run(app, host=SERVER_IP, port=SERVER_PORT)
