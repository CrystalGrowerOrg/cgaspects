#!/bin/bash
set -e
ARCH="${ARCH:-arm64}"

# pyinstaller requires universal2
ARCH=${ARCH/universal/universal2}

echo "Running pyinstaller"
pyinstaller installer/CGAspects.py --onedir --windowed \
    --name=CGAspects \
    --icon=res/app_icons/CGAspects.icns --noconfirm \
    --target-architecture="${ARCH}" \
    --exclude-module=pytest

echo "Running ad hoc code signing"
export APP="dist/CGAspects.app"
export CONTENTS_DIR="${APP}/Contents"

codesign --force --deep --sign - "${CONTENTS_DIR}/MacOS/CGAspects"
find "${CONTENTS_DIR}/MacOS" "${CONTENTS_DIR}/Frameworks" \
     "${CONTENTS_DIR}/Resources" \
     -name '*.dylib' \
     -o -name '*.framework' \
     -maxdepth 1 \
     -exec codesign --force --sign - {} \;
codesign --force --deep --sign - ${APP}
