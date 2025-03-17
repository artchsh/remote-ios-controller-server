# Xbox 360 Controller

A Progressive Web App (PWA) that allows you to use your phone as a virtual Xbox 360 controller for your PC.

## Features

- Virtual Xbox 360 gamepad with D-pad, action buttons, shoulder buttons, triggers, and analog sticks
- WebSocket communication for real-time control
- PWA support for installation on mobile devices
- Uses vJoy to create a virtual Xbox 360 controller on your PC
- Red and black theme inspired by Xbox controllers
- Fully functional analog sticks with proper Xbox 360 axis values
- Responsive design that works in both landscape and portrait orientations

## Requirements

- Python 3.7+
- vJoy (virtual joystick driver) installed on your PC
- A modern web browser on your mobile device
- Both devices on the same network

## Installation

1. Install vJoy:
   - Download and install vJoy from [the official site](http://vjoystick.sourceforge.net/site/index.php/download-a-install/download)
   - Configure vJoy to have at least 12 buttons, 1 POV hat, and 4 axes (X, Y, RX, RY)
   - Make sure vJoy device #1 is enabled

2. Clone this repository:
   ```
   git clone https://github.com/yourusername/xbox-controller.git
   cd xbox-controller
   ```

3. Create a virtual environment and install dependencies:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # OR
   source .venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

4. Configure your server IP:
   - Edit the `settings.json` file to set your PC's IP address
   - Default port is 8000, which can also be changed in the settings file

## Usage

1. Start the server:
   ```
   python main.py
   ```

2. The server will start on the IP and port specified in settings.json

3. On your mobile device, open a web browser and navigate to:
   ```
   http://<your-pc-ip-address>:8000/app
   ```

4. The controller will automatically connect to the server.

5. Use the virtual controller to send inputs to your PC. The inputs will be sent to the vJoy virtual controller, which can be used in games that support Xbox 360 controllers.

## Xbox 360 Button Mapping

The controller is mapped to a standard Xbox 360 controller layout:

- A, B, X, Y buttons - Maps to corresponding vJoy buttons
- LB, RB (Left/Right Bumpers) - Maps to corresponding vJoy buttons
- LT, RT (Left/Right Triggers) - Maps as buttons (not analog)
- D-Pad - Maps to vJoy POV hat
- Left and Right analog sticks - Maps to X, Y, RX, RY axes
- Start, Back, and Guide buttons - Maps to corresponding vJoy buttons

## Game Compatibility

This virtual controller works with:
- Games that support Xbox 360 controllers
- Any application that can use vJoy input devices
- Steam games with controller support
- Emulators that support gamepads

## Troubleshooting

- If you encounter issues with vJoy, make sure it's properly installed and configured
- Check that vJoy device #1 is enabled in the vJoy configuration
- Ensure your game recognizes the vJoy device as an Xbox 360 controller
- If the controller isn't responding, try using the Reset button
- For best experience, use the controller in landscape orientation
- Make sure your vJoy device has at least 4 axes configured for proper analog stick support

## Installing as a PWA

On your mobile device:

1. Open the controller in your browser
2. For iOS: Tap the Share button, then "Add to Home Screen"
3. For Android: Tap the menu button, then "Add to Home Screen" or "Install App"

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.