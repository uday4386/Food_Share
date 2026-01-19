# PowerShell script to download and install SQLite3 for Windows

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "SQLite3 Installation Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if SQLite3 is already installed
$sqlite3Path = Get-Command sqlite3 -ErrorAction SilentlyContinue
if ($sqlite3Path) {
    Write-Host "SQLite3 is already installed!" -ForegroundColor Green
    Write-Host "Location: $($sqlite3Path.Source)" -ForegroundColor Green
    Write-Host "Version:" -ForegroundColor Yellow
    sqlite3 --version
    exit 0
}

Write-Host "Downloading SQLite3..." -ForegroundColor Yellow

# Create temp directory
$tempDir = "$env:TEMP\sqlite3_download"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# Download SQLite3 (Precompiled Binaries for Windows)
# Using the official SQLite website download link
$downloadUrl = "https://www.sqlite.org/2024/sqlite-tools-win-x64-3500100.zip"
$zipFile = "$tempDir\sqlite3.zip"

try {
    Write-Host "Downloading from: $downloadUrl" -ForegroundColor Cyan
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
    Write-Host "Download completed!" -ForegroundColor Green
} catch {
    Write-Host "Error downloading. Trying alternative method..." -ForegroundColor Red
    # Alternative: Download using .NET WebClient
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($downloadUrl, $zipFile)
    Write-Host "Download completed!" -ForegroundColor Green
}

# Extract ZIP file
Write-Host "Extracting files..." -ForegroundColor Yellow
Expand-Archive -Path $zipFile -DestinationPath $tempDir -Force

# Find sqlite3.exe
$sqlite3Exe = Get-ChildItem -Path $tempDir -Filter "sqlite3.exe" -Recurse | Select-Object -First 1

if ($sqlite3Exe) {
    Write-Host "Found sqlite3.exe at: $($sqlite3Exe.FullName)" -ForegroundColor Green
    
    # Copy to project directory
    $projectPath = (Get-Location).Path
    $destination = "$projectPath\sqlite3.exe"
    Copy-Item -Path $sqlite3Exe.FullName -Destination $destination -Force
    Write-Host "Copied to project directory: $destination" -ForegroundColor Green
    
    # Ask if user wants to add to PATH
    $addToPath = Read-Host "Do you want to add SQLite3 to system PATH? (Y/N)"
    if ($addToPath -eq 'Y' -or $addToPath -eq 'y') {
        $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
        $sqlite3Dir = Split-Path -Parent $sqlite3Exe.FullName
        
        if ($currentPath -notlike "*$sqlite3Dir*") {
            [Environment]::SetEnvironmentVariable("Path", "$currentPath;$sqlite3Dir", "User")
            Write-Host "Added to PATH! You may need to restart your terminal." -ForegroundColor Green
        } else {
            Write-Host "Already in PATH." -ForegroundColor Yellow
        }
    }
    
    # Test installation
    Write-Host ""
    Write-Host "Testing installation..." -ForegroundColor Yellow
    & "$destination" --version
    
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "Installation Complete!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now use:" -ForegroundColor Cyan
    Write-Host "  .\sqlite3.exe instance\food_redistribution.db" -ForegroundColor Yellow
    Write-Host "  or" -ForegroundColor Cyan
    Write-Host "  sqlite3 instance\food_redistribution.db" -ForegroundColor Yellow
    Write-Host ""
    
} else {
    Write-Host "Error: Could not find sqlite3.exe in downloaded files" -ForegroundColor Red
    Write-Host "Please download manually from: https://www.sqlite.org/download.html" -ForegroundColor Yellow
}

# Cleanup
Remove-Item -Path $tempDir -Recurse -Force

