#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download and install Google Chrome (required for Selenium)
apt-get update && apt-get install -y wget curl unzip libgconf-2-4 libxi6 libgomp1 libnss3

# Install Chrome Browser
if [ ! -f /usr/bin/google-chrome ]; then
    echo "Installing Google Chrome..."
    curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o chrome.deb
    apt-get install -y ./chrome.deb
    rm chrome.deb
fi