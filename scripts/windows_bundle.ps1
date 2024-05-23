$ErrorActionPreference = "Stop"

$ARCH = if ($env:ARCH) { $env:ARCH } else { "x86_64" }
$PLATFORM = "windows-${ARCH}"

pyinstaller .installer\CrystalAspects.py --onefile --windowed --name=CGAspects `
    --icon=.res\app_icons\CrystalAspects.png `
    --noconfirm --exclude-module=pytest 

Write-Host "Build completed successfully."
