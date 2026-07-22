#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ESP8266 Light Controller - Touch Portal Plugin
A plugin to control WS2812B addressable LED strip on ESP8266 via HTTP API.

Author: foloryx
Version: 1.0.0
License: MIT
"""

import sys
import os
import json
import logging
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urljoin
from datetime import datetime

try:
    import requests
    from TouchPortalAPI import TouchPortalAPI
except ImportError as e:
    print(f"Error: Required module not found. Please install dependencies: {e}")
    sys.exit(1)


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def setup_logging():
    """
    Configure logging system with file and console output.
    Logs are saved to plugin_logs.txt in the plugin directory.
    """
    log_dir = Path(__file__).parent
    log_file = log_dir / "plugin_logs.txt"

    logger = logging.getLogger("ESP8266LightController")
    logger.setLevel(logging.DEBUG)

    # File handler
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create file logger: {e}")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()


# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

class ConfigManager:
    """
    Manages plugin configuration and settings.
    Configuration is stored in a JSON file in the plugin directory.
    """

    DEFAULT_CONFIG = {
        'esp8266_ip': '192.168.1.100',
        'esp8266_port': 80,
        'connection_timeout': 5,
        'brightness_level': 0,
        'light_state': 'Off'
    }

    def __init__(self):
        """Initialize configuration manager."""
        self.config_file = Path(__file__).parent / "config.json"
        self.config = self._load_config()
        logger.info("Configuration manager initialized")

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        If file doesn't exist, create it with default values.

        Returns:
            Dictionary containing configuration values
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.debug(f"Configuration loaded from {self.config_file}")
                return config
            else:
                logger.info("Configuration file not found, creating with defaults")
                self._save_config(self.DEFAULT_CONFIG)
                return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self.DEFAULT_CONFIG.copy()

    def _save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to JSON file.

        Args:
            config: Configuration dictionary to save

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.debug(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value and save to file.

        Args:
            key: Configuration key
            value: Value to set

        Returns:
            True if successful, False otherwise
        """
        self.config[key] = value
        success = self._save_config(self.config)
        if success:
            logger.debug(f"Configuration updated: {key} = {value}")
        return success

    def update(self, updates: Dict[str, Any]) -> bool:
        """
        Update multiple configuration values.

        Args:
            updates: Dictionary of key-value pairs to update

        Returns:
            True if successful, False otherwise
        """
        self.config.update(updates)
        success = self._save_config(self.config)
        if success:
            logger.debug(f"Configuration updated: {updates}")
        return success

    def get_esp8266_url(self, endpoint: str = '') -> str:
        """
        Build ESP8266 API URL.

        Args:
            endpoint: API endpoint (e.g., '/api/on')

        Returns:
            Full URL to ESP8266 API endpoint
        """
        ip = self.get('esp8266_ip', '192.168.1.100')
        port = self.get('esp8266_port', 80)
        base_url = f"http://{ip}:{port}"
        return urljoin(base_url, endpoint.lstrip('/'))


# ============================================================================
# ESP8266 API CLIENT
# ============================================================================

class ESP8266Client:
    """
    HTTP client for communicating with ESP8266 device.
    Handles all API requests and error handling.
    """

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize ESP8266 client.

        Args:
            config_manager: ConfigManager instance
        """
        self.config = config_manager
        logger.info("ESP8266 client initialized")

    def _make_request(self, endpoint: str, timeout: Optional[int] = None) -> tuple[bool, Optional[str]]:
        """
        Make HTTP GET request to ESP8266.

        Args:
            endpoint: API endpoint
            timeout: Request timeout in seconds

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if timeout is None:
            timeout = self.config.get('connection_timeout', 5)

        url = self.config.get_esp8266_url(endpoint)
        logger.debug(f"Making request to: {url}")

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            logger.info(f"Request successful: {endpoint}")
            return True, None
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error: Cannot reach ESP8266 at {self.config.get('esp8266_ip')}"
            logger.error(f"{error_msg}: {e}")
            return False, error_msg
        except requests.exceptions.Timeout as e:
            error_msg = f"Timeout error: No response from ESP8266 (timeout: {timeout}s)"
            logger.error(f"{error_msg}: {e}")
            return False, error_msg
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error: {e.response.status_code} {e.response.reason}"
            logger.error(f"{error_msg}: {e}")
            return False, error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(f"{error_msg}: {e}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"{error_msg}: {e}")
            return False, error_msg

    def turn_on(self) -> tuple[bool, Optional[str]]:
        """
        Turn on the light.

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        logger.info("Action: Turn on light")
        success, error = self._make_request('/api/on')
        if success:
            self.config.set('light_state', 'On')
        return success, error

    def turn_off(self) -> tuple[bool, Optional[str]]:
        """
        Turn off the light.

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        logger.info("Action: Turn off light")
        success, error = self._make_request('/api/off')
        if success:
            self.config.set('light_state', 'Off')
        return success, error

    def set_brightness(self, brightness_percent: int) -> tuple[bool, Optional[str]]:
        """
        Set brightness level.

        Converts brightness from 0-100 percentage to 0-255 range for ESP8266.

        Args:
            brightness_percent: Brightness level in percentage (0-100)

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        # Validate brightness range
        if not 0 <= brightness_percent <= 100:
            error_msg = f"Invalid brightness value: {brightness_percent}. Must be 0-100"
            logger.error(error_msg)
            return False, error_msg

        # Convert percentage to 0-255 range
        brightness_value = int((brightness_percent / 100) * 255)

        logger.info(f"Action: Set brightness to {brightness_percent}% (value: {brightness_value})")

        endpoint = f'/api/brightness?value={brightness_value}'
        success, error = self._make_request(endpoint)

        if success:
            self.config.set('brightness_level', brightness_percent)
            if brightness_percent > 0:
                self.config.set('light_state', 'On')

        return success, error

    def get_connection_status(self) -> bool:
        """
        Check if ESP8266 is reachable.

        Returns:
            True if ESP8266 is reachable, False otherwise
        """
        success, _ = self._make_request('/api/on', timeout=2)
        return success


# ============================================================================
# TOUCH PORTAL PLUGIN
# ============================================================================

class ESP8266LightPlugin:
    """
    Touch Portal plugin for ESP8266 light control.
    Handles plugin lifecycle, actions, connectors, and state management.
    """

    def __init__(self):
        """Initialize the plugin."""
        logger.info("=" * 70)
        logger.info("ESP8266 Light Controller Plugin Starting")
        logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)

        self.config = ConfigManager()
        self.client = ESP8266Client(self.config)
        self.tp = TouchPortalAPI(self)
        self.running = True
        self.connector_thread = None

        # State update interval for connectors (in milliseconds)
        self.state_update_interval = 500

        logger.info("Plugin initialization completed")

    def start(self):
        """Start the plugin and connect to Touch Portal."""
        try:
            logger.info("Connecting to Touch Portal...")
            self.tp.connect()
            logger.info("Successfully connected to Touch Portal")

            # Update initial states
            self._update_states()

            # Start connector listening thread
            self._start_connector_thread()

            logger.info("Plugin started and listening for events")
        except Exception as e:
            logger.error(f"Fatal error during plugin startup: {e}")
            sys.exit(1)

    def _start_connector_thread(self):
        """Start thread for handling connector changes."""
        self.connector_thread = threading.Thread(
            target=self._connector_listener_thread,
            daemon=True
        )
        self.connector_thread.start()
        logger.debug("Connector listener thread started")

    def _connector_listener_thread(self):
        """
        Thread function for listening to connector value changes.
        Implements real-time brightness adjustment.
        """
        last_brightness = -1

        while self.running:
            try:
                current_brightness = self.config.get('brightness_level', 0)

                # Check if brightness changed
                if current_brightness != last_brightness:
                    last_brightness = current_brightness
                    logger.debug(f"Brightness connector value changed: {current_brightness}%")

                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in connector listener thread: {e}")
                time.sleep(1)

    def _update_states(self):
        """Update all Touch Portal states with current values."""
        try:
            light_state = self.config.get('light_state', 'Off')
            brightness = str(self.config.get('brightness_level', 0))

            self.tp.stateUpdate(state_id='light_state', value=light_state)
            self.tp.stateUpdate(state_id='brightness_value', value=brightness)

            logger.debug(f"States updated - Light: {light_state}, Brightness: {brightness}%")
        except Exception as e:
            logger.error(f"Error updating states: {e}")

    def _show_notification(self, title: str, msg: str, success: bool = True):
        """
        Show notification to user in Touch Portal.

        Args:
            title: Notification title
            msg: Notification message
            success: True for success (green), False for error (red)
        """
        try:
            notification_type = 'TPS-SHOW-NOTIFICATION' if success else 'TPS-SHOW-NOTIFICATION'
            # Touch Portal notification would be sent here
            logger.info(f"Notification: [{title}] {msg}")
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    # ========================================================================
    # TOUCH PORTAL EVENT HANDLERS
    # ========================================================================

    def onConnect(self, data):
        """
        Called when plugin connects to Touch Portal.

        Args:
            data: Connection data from Touch Portal
        """
        logger.info("Plugin connected to Touch Portal")
        self._update_states()

    def onDisconnect(self):
        """Called when plugin disconnects from Touch Portal."""
        logger.warning("Plugin disconnected from Touch Portal")

    def onShutdown(self):
        """Called when plugin is shutting down."""
        logger.info("Plugin shutdown signal received")
        self.running = False
        logger.info("=" * 70)
        logger.info("ESP8266 Light Controller Plugin Stopped")
        logger.info("=" * 70)

    def onInfo(self, data):
        """
        Called with plugin information from Touch Portal.

        Args:
            data: Plugin info data
        """
        logger.debug(f"Plugin info received: {data}")

    def onSettingUpdate(self, setting_name: str, setting_value: str, device_id: str):
        """
        Called when a plugin setting is updated.

        Args:
            setting_name: Name of the setting
            setting_value: New value of the setting
            device_id: Device ID that changed the setting
        """
        logger.info(f"Setting update: {setting_name} = {setting_value}")

        try:
            if setting_name == 'esp8266_ip':
                self.config.set('esp8266_ip', setting_value)
                logger.info(f"ESP8266 IP updated to: {setting_value}")
            elif setting_name == 'esp8266_port':
                try:
                    port = int(setting_value)
                    self.config.set('esp8266_port', port)
                    logger.info(f"ESP8266 port updated to: {port}")
                except ValueError:
                    logger.error(f"Invalid port value: {setting_value}")
            elif setting_name == 'connection_timeout':
                try:
                    timeout = int(setting_value)
                    self.config.set('connection_timeout', timeout)
                    logger.info(f"Connection timeout updated to: {timeout}s")
                except ValueError:
                    logger.error(f"Invalid timeout value: {setting_value}")
        except Exception as e:
            logger.error(f"Error updating setting {setting_name}: {e}")

    def onAction(self, action_id: str, data: list):
        """
        Called when a Touch Portal action is executed.

        Args:
            action_id: ID of the action executed
            data: Action data and parameters
        """
        logger.info(f"Action executed: {action_id}")

        try:
            if action_id == 'light_on':
                self._handle_light_on()
            elif action_id == 'light_off':
                self._handle_light_off()
            elif action_id == 'set_brightness':
                self._handle_set_brightness(data)
            else:
                logger.warning(f"Unknown action: {action_id}")
        except Exception as e:
            logger.error(f"Error executing action {action_id}: {e}")
            self._show_notification("Error", f"Action failed: {str(e)}", success=False)

    def onConnectorChange(self, connector_id: str, connector_value: str):
        """
        Called when a connector value changes.
        Used for real-time brightness slider adjustment.

        Args:
            connector_id: ID of the connector
            connector_value: New value of the connector
        """
        logger.info(f"Connector changed: {connector_id} = {connector_value}")

        try:
            if connector_id == 'brightness_slider':
                brightness = int(connector_value)
                self._handle_brightness_change(brightness)
            else:
                logger.warning(f"Unknown connector: {connector_id}")
        except ValueError:
            logger.error(f"Invalid connector value: {connector_value}")
        except Exception as e:
            logger.error(f"Error handling connector change: {e}")

    # ========================================================================
    # ACTION HANDLERS
    # ========================================================================

    def _handle_light_on(self):
        """Handle light ON action."""
        logger.debug("Processing Light ON action")
        success, error = self.client.turn_on()

        self._update_states()

        if success:
            self._show_notification("Success", "Light turned ON", success=True)
        else:
            self._show_notification("Error", f"Failed to turn on light: {error}", success=False)

    def _handle_light_off(self):
        """Handle light OFF action."""
        logger.debug("Processing Light OFF action")
        success, error = self.client.turn_off()

        self._update_states()

        if success:
            self._show_notification("Success", "Light turned OFF", success=True)
        else:
            self._show_notification("Error", f"Failed to turn off light: {error}", success=False)

    def _handle_set_brightness(self, data: list):
        """
        Handle set brightness action.

        Args:
            data: Action data containing brightness percentage
        """
        if not data or len(data) == 0:
            logger.error("Set brightness action missing brightness value")
            self._show_notification("Error", "Brightness value missing", success=False)
            return

        try:
            brightness_str = str(data[0]).strip()
            brightness_percent = int(brightness_str)

            logger.debug(f"Processing Set Brightness action: {brightness_percent}%")

            success, error = self.client.set_brightness(brightness_percent)

            self._update_states()

            if success:
                self._show_notification("Success", f"Brightness set to {brightness_percent}%", success=True)
            else:
                self._show_notification("Error", f"Failed to set brightness: {error}", success=False)
        except ValueError:
            error_msg = f"Invalid brightness value: {data[0]}"
            logger.error(error_msg)
            self._show_notification("Error", error_msg, success=False)
        except Exception as e:
            logger.error(f"Error in set brightness handler: {e}")
            self._show_notification("Error", f"Unexpected error: {str(e)}", success=False)

    def _handle_brightness_change(self, brightness_percent: int):
        """
        Handle brightness slider connector change (real-time adjustment).

        Args:
            brightness_percent: Brightness level 0-100
        """
        logger.debug(f"Processing brightness slider change: {brightness_percent}%")

        success, error = self.client.set_brightness(brightness_percent)

        self._update_states()

        if not success:
            logger.warning(f"Failed to set brightness from slider: {error}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the plugin."""
    try:
        plugin = ESP8266LightPlugin()
        plugin.start()

        # Keep plugin running
        while plugin.running:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(1)

    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
