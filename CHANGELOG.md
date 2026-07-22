# ESP8266 Light Controller - Touch Portal Plugin
# Version 1.0.0

## Overview

This plugin enables Touch Portal to control WS2812B addressable LED strips on ESP8266 microcontrollers via HTTP API.

The plugin communicates with an ESP8266 device running a simple HTTP API server that handles light control requests.

## Features

- **Light Control**: Turn light on/off via Touch Portal buttons
- **Brightness Adjustment**: Set brightness from 0-100% with automatic conversion to device range (0-255)
- **Real-time Slider**: Use Touch Portal slider connector for live brightness adjustment
- **State Monitoring**: Track light state and brightness in real-time
- **Error Handling**: Comprehensive error handling for network issues
- **Configuration**: Manage ESP8266 IP, port, and timeout settings
- **Logging**: Detailed logs for debugging and monitoring

## Quick Start

### Installation

1. Extract plugin files to Touch Portal plugins folder:
   - **Windows**: `C:\Users\[Username]\AppData\Roaming\TouchPortal\plugins\ESP8266LightController\`
   - **Linux**: `~/.local/share/TouchPortal/plugins/ESP8266LightController/`
   - **macOS**: `~/Library/Application Support/TouchPortal/plugins/ESP8266LightController/`

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Restart Touch Portal

4. Configure plugin settings:
   - Set ESP8266 IP address (default: 192.168.1.100)
   - Set port (default: 80)
   - Set timeout in seconds (default: 5)

### Configuration

Edit `config.json` to customize settings:

```json
{
  "esp8266_ip": "192.168.1.100",
  "esp8266_port": 80,
  "connection_timeout": 5,
  "brightness_level": 0,
  "light_state": "Off"
}
```

## Plugin Structure

- **plugin.py** - Main plugin implementation
  - ConfigManager: Handles configuration persistence
  - ESP8266Client: HTTP API client for device communication
  - ESP8266LightPlugin: Main Touch Portal plugin class

- **manifest.json** - Plugin configuration for Touch Portal
  - Defines actions, connectors, states, and categories

- **entry.tp** - Plugin documentation and entry point info

- **config.json** - User configuration file (auto-generated/updated)

- **plugin_logs.txt** - Debug and error logs (auto-generated)

- **requirements.txt** - Python package dependencies

- **build.bat** / **build.sh** - Build scripts for packaging

## API Endpoints

The plugin sends the following HTTP GET requests to the ESP8266:

### Turn Light On
```
GET http://[IP]:[PORT]/api/on
```

### Turn Light Off
```
GET http://[IP]:[PORT]/api/off
```

### Set Brightness
```
GET http://[IP]:[PORT]/api/brightness?value=[0-255]
```

Example:
```
GET http://192.168.1.100:80/api/brightness?value=128
```

## Code Architecture

### ConfigManager Class

Manages plugin configuration with automatic persistence:
- Loads/saves configuration from JSON file
- Provides default values
- Validates settings
- Updates configuration dynamically

Key Methods:
- `get(key, default)` - Retrieve configuration value
- `set(key, value)` - Update single configuration value
- `update(updates)` - Update multiple values
- `get_esp8266_url(endpoint)` - Build API URLs

### ESP8266Client Class

Handles all communication with the ESP8266 device:
- Makes HTTP GET requests
- Comprehensive error handling
- Timeout management
- Connection validation

Key Methods:
- `_make_request(endpoint, timeout)` - Core HTTP request handler
- `turn_on()` - Send light on command
- `turn_off()` - Send light off command
- `set_brightness(brightness_percent)` - Set brightness level
- `get_connection_status()` - Check device availability

Features:
- Connection error handling
- Timeout error handling
- HTTP error handling
- Automatic state updates after commands

### ESP8266LightPlugin Class

Main Touch Portal plugin implementation:
- Lifecycle management (connect, disconnect, shutdown)
- Event handling (actions, connectors, settings)
- State updates
- Error notifications
- Threading for connector listening

Key Methods:
- `onConnect()` - Called when connected to Touch Portal
- `onAction(action_id, data)` - Handle action execution
- `onConnectorChange(connector_id, value)` - Handle slider changes
- `onSettingUpdate(setting_name, value, device_id)` - Handle settings updates
- `_update_states()` - Update all Touch Portal states
- `_show_notification(title, msg, success)` - Display user notifications

## Error Handling

The plugin handles the following error scenarios gracefully:

### Connection Errors
- ESP8266 is unreachable/offline
- Logs error with device IP
- Shows error notification
- Plugin continues running

### Timeout Errors
- No response from ESP8266 within configured timeout
- Logs timeout with timeout value
- Shows error notification
- User can retry or adjust timeout

### HTTP Errors
- ESP8266 returns error status code
- Logs HTTP status and reason
- Shows error notification
- Plugin continues running

### Configuration Errors
- Invalid IP address format
- Invalid port number
- Invalid timeout value
- Validation errors logged
- Defaults used if validation fails

### File I/O Errors
- Cannot read configuration file
- Cannot write configuration file
- In-memory defaults used
- Error logged
- Plugin continues running

## Logging

Comprehensive logging to `plugin_logs.txt`:

Log Levels:
- **DEBUG**: Detailed debugging information
- **INFO**: General operational information
- **WARNING**: Warning messages (recoverable issues)
- **ERROR**: Error messages (failures but plugin continues)
- **CRITICAL**: Critical errors (fatal issues)

Example Log Output:
```
2024-01-15 10:30:45 - INFO - Plugin initialization completed
2024-01-15 10:30:46 - INFO - Connecting to Touch Portal...
2024-01-15 10:30:46 - INFO - Successfully connected to Touch Portal
2024-01-15 10:30:50 - INFO - Action executed: light_on
2024-01-15 10:30:50 - INFO - Request successful: /api/on
2024-01-15 10:30:50 - DEBUG - States updated - Light: On, Brightness: 0%
```

## Building the Plugin

### Windows

```bash
build.bat
```

Creates `ESP8266LightController_v1.0.0.zip`

### Linux/macOS

```bash
chmod +x build.sh
./build.sh
```

Creates `ESP8266LightController_v1.0.0.zip`

## Actions

### Light ON
- **ID**: `light_on`
- **Description**: Turn on the ESP8266 light
- **Parameters**: None
- **API Call**: `GET /api/on`
- **State Update**: Sets light state to "On"

### Light OFF
- **ID**: `light_off`
- **Description**: Turn off the ESP8266 light
- **Parameters**: None
- **API Call**: `GET /api/off`
- **State Update**: Sets light state to "Off"

### Set Brightness
- **ID**: `set_brightness`
- **Description**: Set brightness level (0-100%)
- **Parameters**: Brightness percentage (0-100)
- **Format**: "Set brightness to {1}%"
- **Validation**: Regex: `^(100|[0-9]{1,2})$`
- **Conversion**: 0-100% → 0-255 value
- **API Call**: `GET /api/brightness?value=[0-255]`
- **State Updates**: 
  - Sets brightness level
  - Sets light state to "On" if brightness > 0

## Connectors

### Brightness Slider
- **ID**: `brightness_slider`
- **Type**: Slider
- **Name**: Brightness
- **Range**: 0-100
- **Value Type**: Number
- **Category**: ESP Camera Light
- **Features**:
  - Real-time adjustment (no button press required)
  - Automatic HTTP requests to ESP8266
  - Updates states immediately
  - 500ms refresh interval
  - Runs in separate thread

## States

### Light State
- **ID**: `light_state`
- **Type**: Text
- **Description**: Light State
- **Default**: "Off"
- **Values**: "On", "Off"
- **Updates When**:
  - Light ON action executed
  - Light OFF action executed
  - Brightness set above 0%

### Brightness
- **ID**: `brightness_value`
- **Type**: Text
- **Description**: Brightness
- **Default**: "0"
- **Range**: "0" to "100"
- **Updates When**:
  - Set Brightness action executed
  - Brightness slider changed
  - Any successful brightness adjustment

## Troubleshooting

### Plugin Won't Start

**Check Python Installation**:
```bash
python --version
# or
python3 --version
```

Ensure Python 3.7+ is installed.

**Check Dependencies**:
```bash
pip list | grep TouchPortal
pip list | grep requests
```

Install missing packages:
```bash
pip install -r requirements.txt
```

### Cannot Connect to ESP8266

**Verify IP Address**:
```bash
ping 192.168.1.100
```

Check ESP8266 IP in router or device log.

**Check Port**:
Ensure ESP8266 is listening on configured port (default: 80).

**Check Network**:
- Ensure device is on same network as ESP8266
- Check firewall settings
- Check router connectivity

**Check Logs**:
Review `plugin_logs.txt` for detailed error messages.

### Slow Response

- Increase timeout value in settings
- Check network speed and latency
- Ensure ESP8266 WiFi signal is strong
- Consider wired network connection for stability

## Requirements

- Touch Portal (any recent version)
- Python 3.7 or higher
- TouchPortalAPI package
- requests package
- ESP8266 with HTTP API server

## Dependencies

From `requirements.txt`:
- TouchPortalAPI==3.6 - Official Touch Portal Python API
- requests==2.31.0 - HTTP library for API requests
- urllib3==2.1.0 - HTTP client for requests
- charset-normalizer==3.3.2 - Character encoding
- idna==3.6 - International domain names
- certifi==2023.7.22 - SSL certificates

## Performance

- **State Updates**: Immediate after action execution
- **Slider Response**: Real-time with minimal latency
- **API Requests**: Non-blocking with configurable timeout
- **Threading**: Connector listener runs in separate thread
- **Logging**: Asynchronous file writing

## Security Notes

- No authentication currently supported
- Uses HTTP (not HTTPS)
- No data encryption
- Local network access only

For production:
- Configure ESP8266 firewall
- Consider adding authentication
- Use HTTPS if possible
- Restrict network access

## Version History

### 1.0.0 (Initial Release)
- Light on/off control
- Brightness adjustment (0-100%)
- Real-time slider connector
- State tracking
- Comprehensive error handling
- Detailed logging
- Full documentation
- Build scripts for packaging

## License

MIT License

## Support

For issues or feature requests:
1. Check `plugin_logs.txt` for error details
2. Verify ESP8266 configuration
3. Check network connectivity
4. Review README.md for troubleshooting

## Author

foloryx

---

**Version**: 1.0.0
**Last Updated**: 2024
**SDK Version**: 6
**Minimum Python**: 3.7
