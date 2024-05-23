#!/bin/bash
set -e
ARCH="${ARCH:-x86_64}"
export PLATFORM="linux-${ARCH}"

# Build the application
pyinstaller installer/CGAspects.py --onedir --windowed --icon=res/app_icons/CGAspects.png --noconfirm --exclude-module=pytest

chmod +x dist/CGAspects/CGAspects
echo "Build completed for Linux"

