#!/bin/bash

# ESP8266 Light Controller - Touch Portal Plugin Build Script
# This script builds and packages the plugin for distribution on Linux/macOS

set -e

# Define plugin name and version
PLUGIN_NAME="ESP8266LightController"
PLUGIN_VERSION="1.0.0"
OUTPUT_FILE="${PLUGIN_NAME}_v${PLUGIN_VERSION}.zip"

echo ""
echo "============================================================"
echo "ESP8266 Light Controller - Build Script"
echo "============================================================"
echo ""

# Check if required files exist
echo "Checking required files..."

if [ ! -f "plugin.py" ]; then
    echo "Error: plugin.py not found!"
    exit 1
fi

if [ ! -f "manifest.json" ]; then
    echo "Error: manifest.json not found!"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found!"
    exit 1
fi

echo "All required files found."
echo ""

# Check if zip command is available
if ! command -v zip &> /dev/null; then
    echo "Error: zip command not found. Please install zip utility."
    exit 1
fi

# Create temporary build directory
echo "Preparing build directory..."
if [ -d "build_temp" ]; then
    rm -rf build_temp
fi

mkdir -p "build_temp/${PLUGIN_NAME}"

# Copy files
echo "Copying files..."
cp plugin.py "build_temp/${PLUGIN_NAME}/"
cp manifest.json "build_temp/${PLUGIN_NAME}/"
cp entry.tp "build_temp/${PLUGIN_NAME}/"
cp requirements.txt "build_temp/${PLUGIN_NAME}/"
cp README.md "build_temp/${PLUGIN_NAME}/"

if [ -f "config.json" ]; then
    cp config.json "build_temp/${PLUGIN_NAME}/"
fi

if [ -d "assets" ]; then
    cp -r assets "build_temp/${PLUGIN_NAME}/"
fi

echo "Files copied successfully."
echo ""

# Create zip file
echo "Creating zip archive..."
cd build_temp
zip -r "../${OUTPUT_FILE}" "${PLUGIN_NAME}" > /dev/null
cd ..

if [ $? -ne 0 ]; then
    echo "Error: Failed to create zip file!"
    exit 1
fi

# Clean up temporary directory
rm -rf build_temp

echo ""
echo "============================================================"
echo "Build completed successfully!"
echo "============================================================"
echo ""
echo "Output file: ${OUTPUT_FILE}"
echo "Size: $(du -h "${OUTPUT_FILE}" | cut -f1)"
echo ""
echo "The plugin package is ready for distribution."
echo "You can now upload it to Touch Portal or distribute it manually."
echo ""
echo "Installation instructions:"
echo "1. Extract the zip file to your Touch Portal plugins folder"
echo "2. Linux: ~/.local/share/TouchPortal/plugins/"
echo "3. macOS: ~/Library/Application Support/TouchPortal/plugins/"
echo "4. Run: pip install -r requirements.txt (or pip3)"
echo "5. Restart Touch Portal"
echo ""
echo "============================================================"
echo ""
