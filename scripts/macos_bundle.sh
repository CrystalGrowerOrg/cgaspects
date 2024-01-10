pyinstaller installer/CrystalAspects.py --onedir --windowed --icon=icons/CrystalAspects.icns --noconfirm
echo "Running ad hoc code signing"
export APP="dist/CrystalAspects.app"
export CONTENTS_DIR="${APP}/Contents"
codesign --force --deep --sign - "${CONTENTS_DIR}/MacOS/CrystalAspects"
find "${CONTENTS_DIR}/MacOS" "${CONTENTS_DIR}/Frameworks" \
     "${CONTENTS_DIR}/Resources" \
     -name '*.dylib' \
     -o -name '*.framework' \
     -maxdepth 1 \
     -exec codesign --force --sign - {} \;
codesign --force --deep --sign - ${APP}
