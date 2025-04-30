# === extract_arc.ps1 ===
# Extract all .arc files from ROMFS_DIR into ARC_DIR

# Ensure environment is loaded
if (-not $env:ROMFS_DIR -or -not $env:ARC_DIR -or -not $env:TOOLS_DIR) {
    Write-Error "Missing environment setup. Please run env.ps1 first."
    exit 1
}

$ARC_TOOL = "$env:TOOLS_DIR\arc_extractor\arc_extract.exe"

if (-not (Test-Path $ARC_TOOL)) {
    Write-Error "arc_extract.exe not found at: $ARC_TOOL"
    Write-Host "You can download it from: https://github.com/marcussacana/ARC-Tool"
    exit 1
}

# Get all .arc files inside the ROMFS directory
$arcFiles = Get-ChildItem -Path $env:ROMFS_DIR -Recurse -Filter '*.arc' -File

if ($arcFiles.Count -eq 0) {
    Write-Host "No .arc files found in $env:ROMFS_DIR"
    exit 0
}

foreach ($arc in $arcFiles) {
    $relativePath = $arc.FullName.Substring($env:ROMFS_DIR.Length).TrimStart('\')
    $targetDir = Join-Path $env:ARC_DIR ($relativePath -replace '\.arc$', '')

    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }

    Write-Host "Extracting: $relativePath"
    & $ARC_TOOL "$($arc.FullName)" "$targetDir"
}

Write-Host "All ARC files extracted to $env:ARC_DIR"
