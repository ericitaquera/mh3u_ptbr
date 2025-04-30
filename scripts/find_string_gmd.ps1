# === find_string_gmd.ps1 ===
# Search for a string inside all *.gmd files

# Ensure environment is loaded
if (-not $env:ROMFS_DIR) {
    Write-Error "Missing environment setup. Please run env.ps1 first."
    exit 1
}

# Prompt for search string
$searchTerm = Read-Host "Enter the string to search for"

# Get all .gmd files under the ROMFS directory
$gmdFiles = Get-ChildItem -Path $env:ROMFS_DIR -Recurse -Filter '*.gmd' -File

if ($gmdFiles.Count -eq 0) {
    Write-Host "No .gmd files found in $env:ROMFS_DIR"
    exit 0
}

Write-Host "Searching for '$searchTerm' in $($gmdFiles.Count) .gmd files..."

foreach ($file in $gmdFiles) {
    $matches = Select-String -Path $file.FullName -Pattern $searchTerm -SimpleMatch
    if ($matches) {
        Write-Host "Match found in: $($file.FullName)"
    }
}

Write-Host "Search complete."
