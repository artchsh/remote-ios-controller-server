# Virtual Gamepad WebSocket Server

A Python-based WebSocket server that emulates an Xbox 360 controller using the vgamepad library. This server accepts JSON data over WebSockets and translates it into virtual gamepad inputs through the ViGEm Bus Driver.

## Requirements

- Windows OS (required for ViGEm Bus Driver)
- Python 3.7+
- [ViGEm Bus Driver](https://github.com/ViGEm/ViGEmBus/releases) must be installed

## Dependencies

```
fastapi==0.104.1
uvicorn==0.23.2
websockets==11.0.3
vgamepad==0.1.0
python-multipart==0.0.6
```

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the server:

```bash
python main.py
```

By default, the server will run on port 8000. You can connect to it using a WebSocket client by connecting to `ws://YOUR_IP:8000/ws`.

## JSON Format

The server expects JSON data in the following format:

```js
{
    'button': 'lt', 
    'type': 'button', 
    'action': 'release'
}
```

## Features

- Emulates an Xbox 360 controller (XInput)
- Real-time control via WebSockets
- Low-latency response
- Compatible with any WebSocket client that can send the appropriate JSON format

## Related Projects

- **iOS Client App**: [https://github.com/artchsh/remote-ios-controller-app](https://github.com/artchsh/remote-ios-controller-app) - Use your iPhone as a gamepad controller with this server

## Contributions

Contributions of any kind are welcome! Feel free to submit issues or pull requests.

## License

[MIT License](LICENSE)