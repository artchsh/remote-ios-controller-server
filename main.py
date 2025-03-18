from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, json, threading, vgamepad as vg, os, socket, asyncio
from contextlib import asynccontextmanager

SERVER_IP = '0.0.0.0'
SERVER_PORT = 8000

@asynccontextmanager
async def lifespan(app: FastAPI):
    global main_loop
    main_loop = asyncio.get_running_loop()
    yield

app = FastAPI(title="Remote Controller API", version="0.1", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    **{k: v for k, v in {
        "up": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
        "right": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
        "down": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
        "left": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
    }.items()}
}

controller_lock = threading.Lock()
active_connections = set()
connections_lock = threading.Lock()
callback_registered = False
main_loop = None

async def send_message(websocket: WebSocket, msg: dict):
    try:
        await websocket.send_text(json.dumps(msg))
    except Exception as e:
        print(f"Error sending message: {e}")

def vibration_callback(client, target, large_motor, small_motor, led_number, user_data):
    message = {"vibration": {"large_motor": large_motor, "small_motor": small_motor}}
    print(f"Vibration update: {message}")
    
    with connections_lock:
        connections = list(active_connections)
    
    for websocket in connections:
        asyncio.run_coroutine_threadsafe(
            send_message(websocket, message),
            main_loop
        )

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "N/A"

@app.get("/")
async def root():
    return {"message": "Controller API operational"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global callback_registered
    
    await websocket.accept()
    with connections_lock:
        active_connections.add(websocket)
    
    if not callback_registered:
        gamepad.register_notification(vibration_callback)
        callback_registered = True
        gamepad.update()

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                
                if msg.get("ping"):
                    await send_message(websocket, {"status": "pong"})
                    continue
                
                with controller_lock:
                    if "button" in msg and "action" in msg:
                        button, action = msg["button"], msg["action"]
                        
                        if button in BUTTON_MAPPING:
                            (gamepad.press_button if action == "press" else gamepad.release_button)(BUTTON_MAPPING[button])
                        
                        elif button in ["lt", "rt"]:
                            value = 255 if action == "press" else 0
                            (gamepad.left_trigger if button == "lt" else gamepad.right_trigger)(value)
                        
                        elif button in ["ls", "rs"]:
                            btn = vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB if button == "ls" else vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB
                            (gamepad.press_button if action == "press" else gamepad.release_button)(btn)
                        
                        else:
                            await send_message(websocket, {"status": "error", "message": "Invalid button"})
                            continue
                        
                        gamepad.update()
                        await send_message(websocket, {"status": "success"})
                    
                    elif "stick" in msg:
                        stick = msg["stick"]
                        x = max(-32768, min(32767, msg.get("x", 0)))
                        y = max(-32768, min(32767, msg.get("y", 0)))
                        
                        if stick == "left":
                            gamepad.left_joystick(x, -y)
                        elif stick == "right":
                            gamepad.right_joystick(x, -y)
                        
                        gamepad.update()
                        await send_message(websocket, {"status": "success"})
                    
                    elif "vibration" in msg:
                        vib = msg["vibration"]
                        gamepad.set_vibration(vib.get("large_motor", 0), vib.get("small_motor", 0))
                        gamepad.update()
                        await send_message(websocket, {"status": "success"})
            
            except json.JSONDecodeError:
                await send_message(websocket, {"status": "error", "message": "Invalid JSON"})
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        with connections_lock:
            active_connections.remove(websocket)

if __name__ == "__main__":
    print(f"\033[96mLocal IP: {get_local_ip()}\nPort: {SERVER_PORT}\033[0m")
    uvicorn.run(app, host=SERVER_IP, port=SERVER_PORT, log_level="critical")