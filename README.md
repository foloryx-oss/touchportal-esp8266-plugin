````markdown name=README.md
# ESP8266 Light Controller - Touch Portal Plugin

A professional Touch Portal plugin for controlling WS2812B addressable LED strips on ESP8266 devices via HTTP API.

## Features

- **Turn Light On/Off** - Simple on/off control via touch portal
- **Brightness Control** - Set brightness 0-100% with automatic conversion to 0-255 range
- **Real-time Slider** - Live brightness adjustment using Touch Portal connector
- **State Tracking** - Monitor light status and brightness in real-time
- **Error Handling** - Robust error handling with detailed logging
- **Configuration** - Store and manage ESP8266 settings (IP, port, timeout)
- **Logging** - Comprehensive logging for debugging and monitoring

## Requirements

- Touch Portal (any recent version)
- Python 3.7+
- ESP8266 with HTTP API endpoint
  - GET `/api/on` - Turn on light
  - GET `/api/off` - Turn off light
  - GET `/api/brightness?value=0-255` - Set brightness

## Installation

### 1. Download and Extract

Download the plugin files and extract them to your Touch Portal plugins directory:

**Windows:**
```
C:\Users\[YourUsername]\AppData\Roaming\TouchPortal\plugins\ESP8266LightController\
```

**Linux:**
```
~/.local/share/TouchPortal/plugins/ESP8266LightController/
```

**macOS:**
```
~/Library/Application Support/TouchPortal/plugins/ESP8266LightController/
```

### 2. Install Python Dependencies

Open Command Prompt/Terminal and navigate to the plugin directory, then run:

```bash
pip install -r requirements.txt
```

Or for Python 3 specifically:

```bash
pip3 install -r requirements.txt
```

### 3. Restart Touch Portal

Close and reopen Touch Portal to load the new plugin.

## Configuration

### Plugin Settings

After installation, configure the following settings in Touch Portal:

1. **ESP8266 IP Address**
   - The IP address of your ESP8266 device
   - Example: `192.168.1.100`
   - Default: `192.168.1.100`

2. **ESP8266 Port**
   - HTTP port on your ESP8266
   - Example: `80`
   - Default: `80`

3. **Connection Timeout**
   - Time to wait for ESP8266 response (seconds)
   - Example: `5`
   - Default: `5`

### Configuration File

Settings are automatically saved in `config.json` in the plugin directory:

```json
{
  "esp8266_ip": "192.168.1.100",
  "esp8266_port": 80,
  "connection_timeout": 5,
  "brightness_level": 0,
  "light_state": "Off"
}
```

You can manually edit this file if needed. Changes take effect immediately.

## Usage

### Actions

#### Light ON
Turns on the ESP8266 light.

**Usage:**
- Add action "Light ON" to your button/event
- Press the button to turn on the light
- Light state updates automatically

#### Light OFF
Turns off the ESP8266 light.

**Usage:**
- Add action "Light OFF" to your button/event
- Press the button to turn off the light
- Light state updates automatically

#### Set Brightness
Sets the brightness level (0-100%).

**Usage:**
- Add action "Set Brightness to {1}%"
- Enter a value between 0 and 100
- Plugin converts the percentage to 0-255 range automatically
- Light turns on when brightness > 0

### Connectors

#### Brightness Slider
Real-time brightness adjustment using a slider connector.

**Range:** 0-100%

**Features:**
- Move slider to adjust brightness in real-time
- No button press required
- Automatic HTTP requests to ESP8266
- Instant feedback in Touch Portal
- Brightness value displays in States

**Usage:**
1. Add "Brightness" connector in Touch Portal designer
2. Drag slider to adjust brightness
3. Changes are sent to ESP8266 immediately

### States

#### Light State
Displays current state of the light.

**Values:**
- `On` - Light is on
- `Off` - Light is off

**Updates automatically when:**
- Light ON action is executed
- Light OFF action is executed
- Brightness is set above 0%

#### Brightness
Displays current brightness level.

**Values:** 0-100%

**Updates automatically when:**
- Brightness is set via action
- Brightness is adjusted via slider

## Building (Optional)

A build script is provided to package the plugin:

### Windows

```bash
build.bat
```

This creates `ESP8266LightController.zip` ready for distribution.

### Linux/macOS

```bash
chmod +x build.sh
./build.sh
```

## API Reference

### ESP8266 Endpoints

The plugin communicates with the following HTTP API endpoints on your ESP8266:

#### Turn Light On
```
GET http://[IP]:[PORT]/api/on
```

**Response:** HTTP 200 OK

#### Turn Light Off
```
GET http://[IP]:[PORT]/api/off
```

**Response:** HTTP 200 OK

#### Set Brightness
```
GET http://[IP]:[PORT]/api/brightness?value=[0-255]
```

**Parameters:**
- `value` - Brightness value (0-255)

**Example:**
```
GET http://192.168.1.100:80/api/brightness?value=127
```

**Response:** HTTP 200 OK

## Troubleshooting

### Plugin Won't Start

1. **Check Python Installation**
   ```bash
   python --version
   # or
   python3 --version
   ```
   Ensure Python 3.7 or higher is installed.

2. **Verify Dependencies**
   ```bash
   pip list | grep TouchPortal
   pip list | grep requests
   ```

3. **Check Plugin Directory**
   Ensure all files are in the correct location.

### Cannot Connect to ESP8266

1. **Verify IP Address**
   - Check ESP8266 IP in your router
   - Ping the device: `ping 192.168.1.100`

2. **Check Port Number**
   - Ensure ESP8266 is listening on the configured port
   - Default is port 80

3. **Check Network**
   - Ensure your device is on the same network as ESP8266
   - Check firewall settings

4. **Check Logs**
   See the "Logging" section below.

### Slow Response

1. **Increase Timeout**
   - Increase "Connection Timeout" in settings
   - Default: 5 seconds

2. **Check Network Speed**
   - ESP8266 is slow on slow networks
   - Consider using a wired connection if possible

3. **Check ESP8266**
   - Restart the ESP8266
   - Check for interference (WiFi channel)

### Logging

Detailed logs are saved in `plugin_logs.txt` in the plugin directory.

**Log Location:**
- Windows: `%APPDATA%\TouchPortal\plugins\ESP8266LightController\plugin_logs.txt`
- Linux: `~/.local/share/TouchPortal/plugins/ESP8266LightController/plugin_logs.txt`
- macOS: `~/Library/Application Support/TouchPortal/plugins/ESP8266LightController/plugin_logs.txt`

**View Logs:**
```bash
# Windows
type plugin_logs.txt

# Linux/macOS
cat plugin_logs.txt
```

**Log Levels:**
- `DEBUG` - Detailed debugging information
- `INFO` - General information
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

## Development

### Project Structure

```
ESP8266LightController/
├── plugin.py              # Main plugin implementation
├── manifest.json          # Plugin configuration
├── entry.tp               # Plugin entry point documentation
├── requirements.txt       # Python dependencies
├── config.json            # Plugin configuration (auto-generated)
├── plugin_logs.txt        # Plugin logs (auto-generated)
├── README.md              # This file
├── build.bat              # Windows build script
└── assets/                # Plugin icons
    ├── light_on.png
    ├── light_off.png
    └── brightness.png
```

### Adding Features

To extend the plugin:

1. **New Action:** Add to `manifest.json` and handle in `onAction()` method
2. **New Connector:** Add to `manifest.json` and handle in `onConnectorChange()` method
3. **New State:** Add to `manifest.json` and update in `_update_states()` method
4. **New Setting:** Add to `manifest.json` and handle in `onSettingUpdate()` method

### Code Style

- Follow PEP 8 Python style guide
- Use type hints for clarity
- Add docstrings to all functions and classes
- Log important operations and errors

## Error Handling

The plugin handles the following errors gracefully:

1. **Connection Error** - ESP8266 is unreachable
   - Logs error with IP address
   - Shows notification to user
   - Continues running

2. **Timeout Error** - No response from ESP8266
   - Logs timeout with configured timeout value
   - Shows notification to user
   - Continues running

3. **HTTP Error** - ESP8266 returns error status
   - Logs HTTP status code
   - Shows notification to user
   - Continues running

4. **Invalid Configuration** - Bad IP/port/timeout
   - Validates input
   - Logs validation error
   - Uses default values

5. **File I/O Error** - Cannot read/write config
   - Logs error details
   - Uses in-memory defaults
   - Continues running

## Performance

- **Brightness Slider:** Real-time updates with 500ms refresh interval
- **State Updates:** Automatic after each action
- **Connector Listener:** Runs in separate thread to avoid blocking
- **HTTP Requests:** Non-blocking with configurable timeout

## Security

- No authentication currently supported (configure ESP8266 firewall)
- All connections over HTTP (not HTTPS)
- No data encryption
- Plugin runs with local access only

For production use, consider:
- Adding authentication to ESP8266
- Using HTTPS instead of HTTP
- Restricting network access to ESP8266

## Limitations

- Requires HTTP API on ESP8266 (no MQTT support)
- Only supports numeric brightness values
- No group control (one ESP8266 per plugin instance)
- No scheduling or automation

## License

MIT License - See LICENSE file for details

## Support

For issues, bugs, or feature requests:

1. **Check Logs** - Review `plugin_logs.txt` for error details
2. **Check Configuration** - Verify `config.json` has correct values
3. **Check Network** - Ensure ESP8266 is reachable
4. **GitHub Issues** - Report issues on the GitHub repository

## Version History

### 1.0.0 (Initial Release)
- Initial release
- Light on/off control
- Brightness adjustment
- Real-time slider connector
- State tracking
- Comprehensive logging
- Full documentation

## Credits

Developed by foloryx

## Changelog

See CHANGELOG.md for detailed version history.

---

**Last Updated:** 2024
**Plugin Version:** 1.0.0
**Author:** foloryx
````
