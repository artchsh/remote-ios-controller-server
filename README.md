# Virtual Gamepad WebSocket Server

A Python-based WebSocket server that emulates an Xbox 360 controller using the vgamepad library. This server accepts JSON data over WebSockets and translates it into virtual gamepad inputs through the ViGEm Bus Driver.

## Requirements

- Windows OS (required for ViGEm Bus Driver)
- **ViGEm Bus Driver** ([https://github.com/ViGEm/ViGEmBus/releases](https://github.com/ViGEm/ViGEmBus/releases)) **must be installed**

**Note:** For users who do not wish to install Python and its dependencies, a pre-compiled `remote-controller-server.exe` is available for download in the releases section of this repository. Only the ViGEm Bus Driver is required to be installed.

## Dependencies (Only required if running from source)

```
fastapi==0.104.1
uvicorn==0.23.2
websockets==11.0.3
vgamepad==0.1.0
python-multipart==0.0.6
```

## Installation (Only required if running from source)

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

**Running the compiled executable (recommended for most users):**

1. Download `remote-controller-server.exe` from the releases section.
2. Ensure the [ViGEm Bus Driver](https://github.com/ViGEm/ViGEmBus/releases) is installed.
3. Run `remote-controller-server.exe`.

**Running from source (if Python is installed):**

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
- **Pre-compiled executable available for easy setup (no Python installation required)**

## Related Projects

- **iOS Client App**: [https://github.com/artchsh/remote-ios-controller-app](https://github.com/artchsh/remote-ios-controller-app) - Use your iPhone as a gamepad controller with this server

## Contributions

Contributions of any kind are welcome! Feel free to submit issues or pull requests.

## License

[MIT License](LICENSE)
