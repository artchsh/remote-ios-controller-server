from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, json, threading, vgamepad as vg, os, socket

SERVER_IP = '0.0.0.0'
SERVER_PORT = 8000

app = FastAPI(title="Remote Controller Websocket API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gamepad = vg.VX360Gamepad()

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

DPAD_MAPPING = {
    "up": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
    "right": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    "down": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    "left": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
}

# Lock for thread safety
controller_lock = threading.Lock()

# Button state dictionary
button_states = {
    "a": " ",
    "b": " ",
    "x": " ",
    "y": " ",
    "lb": " ",
    "rb": " ",
    "start": " ",
    "back": " ",
    "home": " ",
    "up": " ",
    "right": " ",
    "down": " ",
    "left": " ",
    "lt": " ",
    "rt": " ",
    "ls": " ",
    "rs": " ",
}

# WebSocket connection status
websocket_connected = False

# ANSI color codes
class Color:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

def get_local_ip():
    """Gets the local IP address (Windows only)."""
    if os.name == 'nt':
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            return ip_address
        except Exception:
            return "N/A"
    else:
        return "N/A (Windows only)"

def update_table():
    """Updates the console table with button states, IP, and connection status."""
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear console

    local_ip = get_local_ip()
    connection_status = Color.GREEN + "Connected" + Color.RESET if websocket_connected else Color.RED + "Disconnected" + Color.RESET

    # Helper function to format cells with padding
    def format_cell(text, width=4):
        padding = width - len(text)
        return " " * (padding // 2) + text + " " * (padding - padding // 2)

    # First row (buttons)
    button_row1_keys = ["a", "b", "x", "y", "lb", "rb", "start", "back", "home"]
    button_row1_labels = " | ".join([format_cell(key) for key in button_row1_keys])
    button_row1_values = " | ".join([format_cell(button_states[key]) for key in button_row1_keys])

    # Second row (d-pad, triggers, sticks)
    button_row2_keys = ["up", "right", "down", "left", "lt", "rt", "ls", "rs"]
    button_row2_labels = " | ".join([format_cell(key) for key in button_row2_keys])
    button_row2_values = " | ".join([format_cell(button_states[key]) for key in button_row2_keys])

    print(Color.CYAN + "------------------------------------------------------------------" + Color.RESET)
    print(Color.YELLOW + f"| {button_row1_labels} |" + Color.RESET)
    print(Color.CYAN + "------------------------------------------------------------------" + Color.RESET)
    print(Color.WHITE + f"| {button_row1_values} |" + Color.RESET)
    print(Color.CYAN + "------------------------------------------------------------------" + Color.RESET)
    print(Color.YELLOW + f"| {button_row2_labels} |" + Color.RESET)
    print(Color.CYAN + "------------------------------------------------------------------" + Color.RESET)
    print(Color.WHITE + f"| {button_row2_values} |" + Color.RESET)
    print(Color.CYAN + "------------------------------------------------------------------" + Color.RESET)
    print(Color.MAGENTA + f"WebSocket Status: {connection_status}" + Color.RESET)
    print(Color.GREEN + "Author: Artyom Chshyogolev" + Color.RESET)

@app.get("/")
async def read_root():
    return {"message": "Xbox 360 Controller API is running"}

@app.get("/ping")
async def ping():
    return {"status": "online"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global websocket_connected
    websocket_connected = True
    update_table()
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)

                if "ping" in message_data:
                    await websocket.send_text(json.dumps({"status": "pong"}))
                    continue
                
                with controller_lock:
                    if "button" in message_data and "action" in message_data:
                        button = message_data.get("button")
                        action = message_data.get("action") 
                        
                        # Handle D-pad (POV hat)
                        if button in DPAD_MAPPING:
                            if action == "press":
                                gamepad.press_button(DPAD_MAPPING[button])
                                button_states[button] = "X"
                            elif action == "release":
                                gamepad.release_button(DPAD_MAPPING[button])
                                button_states[button] = " "
                            gamepad.update()
                            update_table()
                            await websocket.send_text(json.dumps({"status": "success"}))

                        elif button in BUTTON_MAPPING:
                            if action == "press":
                                gamepad.press_button(BUTTON_MAPPING[button])
                                button_states[button] = "X"
                            elif action == "release":
                                gamepad.release_button(BUTTON_MAPPING[button])
                                button_states[button] = " "
                            gamepad.update()
                            update_table()
                            await websocket.send_text(json.dumps({"status": "success"}))
                        else:
                            await websocket.send_text(json.dumps({"status": "error", "message": "Invalid button"}))
                            
                        if button in ["lt", "rt"]:
                            if action == "press":
                                gamepad.left_trigger(255) if button == "lt" else gamepad.right_trigger(255)
                                button_states[button] = "X"
                            elif action == "release":
                                gamepad.left_trigger(0) if button == "lt" else gamepad.right_trigger(0)
                                button_states[button] = " "
                            gamepad.update()
                            update_table()
                            await websocket.send_text(json.dumps({"status": "success"}))
                            
                        if button in ["rs", "ls"]:
                            if action == "press":
                                gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB) if button == "ls" else gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
                                button_states[button] = "X"
                            elif action == "release":
                                gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB) if button == "ls" else gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
                                button_states[button] = " "
                            gamepad.update()
                            update_table()
                            await websocket.send_text(json.dumps({"status": "success"}))


                    elif "stick" in message_data and "x" in message_data and "y" in message_data:
                        stick = message_data.get("stick")
                        x_value = message_data.get("x")
                        y_value = message_data.get("y")
                        
                        if stick == "left" or stick == "right":
                            x_value = max(-32768, min(32767, x_value))
                            y_value = max(-32768, min(32767, y_value))
                            
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
    finally:
        websocket_connected = False
        update_table()

if __name__ == "__main__":
    local_ip = get_local_ip()
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear console
    os.system('title Remote Controller Websocket API')  # Set console title
    print(Color.CYAN + "---------------------------------" + Color.RESET)
    print(Color.CYAN + f"Local IP: {local_ip}" + Color.RESET)
    print(Color.CYAN + "---------------------------------" + Color.RESET)
    print(Color.CYAN + f"PORT: {SERVER_PORT}" + Color.RESET)
    print(Color.CYAN + "---------------------------------" + Color.RESET)
    print(Color.RED + "Press Ctrl+C to exit" + Color.RESET)
    uvicorn.run(app, host=SERVER_IP, port=SERVER_PORT, log_level="critical")
