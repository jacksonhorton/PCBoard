#!/bin/bash

set -e

# Get directory of the current script
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../services" && pwd)"
# Define the service file path
MICBOARD_SERVICE_FILE="$SOURCE_DIR/micboard.service"
KIOSK_SERVICE_FILE="$SOURCE_DIR/kiosk.service"

# INSTALL MICBOARD Service File
# Check if the file exists
if [[ ! -f "$MICBOARD_SERVICE_FILE" ]]; then
    echo "Error: micboard.service not found in $SOURCE_DIR"
    exit 1
fi

# Copy to systemd
sudo cp "$MICBOARD_SERVICE_FILE" /etc/systemd/system/micboard.service

# Reload systemd daemon
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable micboard.service
sudo systemctl start micboard.service

echo "✅ micboard.service installed, enabled, and started successfully."

# INSTALL KIOSK Service File
# Check if the file exists
if [[ ! -f "$KIOSK_SERVICE_FILE" ]]; then
    echo "Error: kiosk.service not found in $SOURCE_DIR"
    exit 1
fi

# Copy to systemd
sudo cp "$KIOSK_SERVICE_FILE" /etc/systemd/system/kiosk.service

# Reload systemd daemon
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service

echo "✅ kiosk.service installed, enabled, and started successfully."