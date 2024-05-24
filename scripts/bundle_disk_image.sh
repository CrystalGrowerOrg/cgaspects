#!/bin/bash
set -e
ARCH="${ARCH:-arm64}"
export PLATFORM="macos-${ARCH}"

# Variables
FOLDER_PATH="CGAspects-MacOS-bundle/"
APP_PATH="dist/CGAspects.app"
DISK_IMAGE_PATH="CGAspects-${PLATFORM}.dmg"
VOLUME_NAME="CGAspects"

# Create the folder structure
mkdir -p "$FOLDER_PATH"

# Copy the application
cp -r "$APP_PATH" "$FOLDER_PATH/"

# Create a symlink to the Applications folder
ln -s /Applications "$FOLDER_PATH/Applications"

# Create the disk image
hdiutil create -volname "$VOLUME_NAME" -srcfolder "$FOLDER_PATH" -ov -format UDZO "$DISK_IMAGE_PATH"

rm -r "$FOLDER_PATH"
