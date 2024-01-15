# use pyinstaller 5.13.2, for some reason 6.3 is flagging the bundle as malicious
# TODO check for workarounds involving flagging as safe
pyinstaller .\installer\CrystalAspects.py --onedir --icon=.\res\app_icons\CrystalAspects.png --noconfirm --windowed