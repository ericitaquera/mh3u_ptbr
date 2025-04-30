# === Extract ROMFS from romfs.bin using ctrtool ===

# Ensure environment is loaded
if (-not $env:BASE_DIR -or -not $env:ROMFS_DIR -or -not $env:TOOLS_DIR) {
    Write-Error "Missing environment setup. Please run env.ps1 first."
    exit 1
}

$ROMFS_BIN = "$env:BASE_DIR\romfs.bin"
$CTRTOOL = "$env:TOOLS_DIR\ctrtool\ctrtool.exe"

# Check for romfs.bin
if (-not (Test-Path $ROMFS_BIN)) {
    Write-Error "File not found: $ROMFS_BIN"
    exit 1
}

# Check for ctrtool
if (-not (Test-Path $CTRTOOL)) {
    Write-Error "ctrtool not found at $CTRTOOL"
    exit 1
}

# Create ROMFS_DIR if it doesn't exist
if (-not (Test-Path $env:ROMFS_DIR)) {
    New-Item -ItemType Directory -Path $env:ROMFS_DIR | Out-Null
    Write-Host "Created folder: $env:ROMFS_DIR"
}

# Run extraction
Write-Host "Extracting ROMFS to: $env:ROMFS_DIR"
& $CTRTOOL --romfsdir=$env:ROMFS_DIR $ROMFS_BIN

if ($LASTEXITCODE -eq 0) {
    Write-Host "ROMFS extracted successfully to $env:ROMFS_DIR"
} else {
    Write-Error "Failed to extract ROMFS."
}
