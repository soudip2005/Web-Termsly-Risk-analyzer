#!/usr/bin/env bash
set -o errexit

echo "--- Upgrading pip ---"
pip install --upgrade pip

echo "--- Installing Python dependencies ---"
pip install -r requirements.txt

echo "--- Installing Chrome Dependencies ---"
apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    libgconf-2-4 \
    libxi6 \
    libgomp1 \
    libnss3 \
    libatk-bridge2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2

echo "--- Installing Google Chrome ---"
if [ ! -f /usr/bin/google-chrome ]; then
    curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o chrome.deb
    apt-get install -y ./chrome.deb
    rm chrome.deb
fi

echo "--- Build Completed Successfully ---"