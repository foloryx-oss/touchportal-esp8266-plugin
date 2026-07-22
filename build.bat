@echo off
REM ESP8266 Light Controller - Touch Portal Plugin Build Script
REM This script builds and packages the plugin for distribution

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo ESP8266 Light Controller - Build Script
echo ============================================================
echo.

REM Define plugin name and version
set PLUGIN_NAME=ESP8266LightController
set PLUGIN_VERSION=1.0.0
set OUTPUT_FILE=%PLUGIN_NAME%_v%PLUGIN_VERSION%.zip

REM Check if 7-Zip is installed
where /q 7z
if errorlevel 1 (
    echo Warning: 7-Zip not found. Trying to use built-in Windows compression...
    echo Note: This may require manual zip creation.
)

REM Define files to include in the package
set FILES_TO_INCLUDE=^
    plugin.py ^
    manifest.json ^
    entry.tp ^
    requirements.txt ^
    README.md ^
    config.json ^
    plugin_logs.txt ^
    assets\*

echo Preparing to build package...
echo Package name: %OUTPUT_FILE%
echo Plugin version: %PLUGIN_VERSION%
echo.

REM Check if files exist
echo Checking required files...
if not exist "plugin.py" (
    echo Error: plugin.py not found!
    exit /b 1
)
if not exist "manifest.json" (
    echo Error: manifest.json not found!
    exit /b 1
)

echo All required files found.
echo.

REM Create temporary build directory
if exist "build_temp" (
    rmdir /s /q build_temp
)
mkdir build_temp\%PLUGIN_NAME%

echo Copying files...
copy plugin.py build_temp\%PLUGIN_NAME%\ >nul
copy manifest.json build_temp\%PLUGIN_NAME%\ >nul
copy entry.tp build_temp\%PLUGIN_NAME%\ >nul
copy requirements.txt build_temp\%PLUGIN_NAME%\ >nul
copy README.md build_temp\%PLUGIN_NAME%\ >nul

if exist "config.json" (
    copy config.json build_temp\%PLUGIN_NAME%\ >nul
)

if exist "assets" (
    xcopy assets build_temp\%PLUGIN_NAME%\assets /e /i /y >nul
)

echo Files copied successfully.
echo.

REM Create zip file using 7-Zip if available
where /q 7z
if errorlevel 1 (
    echo Creating zip using PowerShell...
    powershell -nologo -noprofile -command "Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::CreateFromDirectory('build_temp\%PLUGIN_NAME%', '%OUTPUT_FILE%')"
    if errorlevel 1 (
        echo Error: Failed to create zip file!
        exit /b 1
    )
) else (
    echo Creating zip using 7-Zip...
    cd build_temp
    7z a -tzip ..\%OUTPUT_FILE% %PLUGIN_NAME%\ >nul
    cd ..
    if errorlevel 1 (
        echo Error: Failed to create zip file!
        exit /b 1
    )
)

REM Clean up temporary directory
rmdir /s /q build_temp

echo.
echo ============================================================
echo Build completed successfully!
echo ============================================================
echo.
echo Output file: %OUTPUT_FILE%
echo Size: 
for %%A in (%OUTPUT_FILE%) do echo %%~zA bytes
echo.
echo The plugin package is ready for distribution.
echo You can now upload it to Touch Portal or distribute it manually.
echo.
echo Installation instructions:
echo 1. Extract the zip file to your Touch Portal plugins folder
echo 2. Windows: %%APPDATA%%\TouchPortal\plugins\
echo 3. Linux: ~/.local/share/TouchPortal/plugins/
echo 4. macOS: ~/Library/Application Support/TouchPortal/plugins/
echo 5. Run: pip install -r requirements.txt
echo 6. Restart Touch Portal
echo.
echo ============================================================
echo.
