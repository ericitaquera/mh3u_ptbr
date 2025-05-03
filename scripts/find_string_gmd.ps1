# === find_string_gmd.ps1 ===
# Search for a string inside all *.gmd files

# Ensure environment is loaded
param (
    [string]$searchTerm
)

if (-not $env:ARC_EXTRACTED_DIR) {
    Write-Error "Missing environment setup. Please run env.ps1 first."
    exit 1
}

if (-not $searchTerm) {
    Write-Host "Usage: .\find_string_gmd.ps1 <search string>" -ForegroundColor DarkGray
    $searchTerm = Read-Host "Enter the string to search for"
}

if (-not $searchTerm) {
    Write-Host "Usage: .ind_string_gmd.ps1 <search string>" -ForegroundColor DarkGray
    $searchTerm = Read-Host "Enter the string to search for"
}

# Get all .gmd files under the ROMFS directory
$gmdFiles = Get-ChildItem -Path $env:ARC_EXTRACTED_DIR -Recurse -Filter '*.gmd' -File

if ($gmdFiles.Count -eq 0) {
    Write-Host "No .gmd files found in $env:ARC_EXTRACTED_DIR"
    exit 0
}

Write-Host "Searching for '$searchTerm' in $($gmdFiles.Count) .gmd files..."

for ($i = 0; $i -lt $gmdFiles.Count; $i++) {
    $file = $gmdFiles[$i]
    $percent = [math]::Round(($i / $gmdFiles.Count) * 100)
    Write-Progress -Activity "Searching .gmd files..." -Status "$($i+1)/$($gmdFiles.Count)" -PercentComplete $percent
    $matches = Select-String -Path $file.FullName -Pattern $searchTerm -SimpleMatch
    if ($matches) {
        Write-Host "Match found in: $($file.FullName)" -ForegroundColor Yellow

        # Find corresponding .txt translation file
        $relativePath = $file.FullName.Substring($env:ARC_EXTRACTED_DIR.Length).TrimStart('\')
        $txtPath = Join-Path $env:GMD_TXT_PTBR_DIR ([System.IO.Path]::ChangeExtension($relativePath, ".txt"))

        if (Test-Path $txtPath) {
            Write-Host " ! Translation file already exists: $txtPath" -ForegroundColor DarkGreen
        } #else {
            #Write-Host " ! Translation file not found for: $txtPath" -ForegroundColor DarkRed
        #}
    }
}

Write-Host "Search complete." -ForegroundColor Green
