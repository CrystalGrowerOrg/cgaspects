$ErrorActionPreference = "Stop"

$ARCH = if ($env:ARCH) { $env:ARCH } else { "x86_64" }
$PLATFORM = "windows-${ARCH}"

# Variables
$APP_PATH = "dist\CGAspects"
$ZIP_FILE_PATH = "CGAspects-${PLATFORM}.zip"

# Create a temporary folder
$tempFolder = New-Item -ItemType Directory -Path "temp" -Force

# Copy the application to the temporary folder
Copy-Item -Path $APP_PATH -Destination $tempFolder -Recurse

# Create the zip file
Compress-Archive -Path $tempFolder\* -DestinationPath $ZIP_FILE_PATH -Force

# Remove the temporary folder
Remove-Item -Path $tempFolder -Recurse -Force

Write-Host "Zip file created successfully: $ZIP_FILE_PATH"
