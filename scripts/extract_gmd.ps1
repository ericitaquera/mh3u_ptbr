# === extract_gmd.ps1 ===
# Extract gmd binary files into .txt editable
# Defaults to dry-run unless -Execute is used

param(
    [Parameter(Mandatory = $true)]
    [string]$SourceFile,
    [switch]$Help,
    [switch]$Execute,
    [Alias("dry-run")]
    [switch]$DryRun = $true
)

if ($Help) {
    Write-Host "USAGE:"
    Write-Host "  .\\extract_gmd.ps1 -SourceFile <file.gmd> [-Execute] [-Force] [-Help]"
    Write-Host "  Dry-run by default. Use -Execute to write output."
    Write-Host "  Outputs .txt and .header files to `$env:GMD_TXT_DIR"
    exit 0
}

# Define output filenames
$relativePath = $SourceFile.Substring($env:ARC_EXTRACTED_DIR.Length).TrimStart('\')
$baseName = [System.IO.Path]::GetFileNameWithoutExtension($SourceFile)

$targetDir = Join-Path $env:GMD_TXT_DIR ([System.IO.Path]::GetDirectoryName($relativePath))
if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

$OutputText = Join-Path $targetDir ($baseName + ".txt")
$OutputHeader = Join-Path $targetDir ($baseName + ".header")

# Check if output files exist
if ((Test-Path $OutputText) -or (Test-Path $OutputHeader)) {
    if (-not $Execute) {
        Write-Host "[Dry Run] Would overwrite:"
        if (Test-Path $OutputText) { Write-Host " - $OutputText" }
        if (Test-Path $OutputHeader) { Write-Host " - $OutputHeader" }
        exit 0
    } else {
        Write-Host "Warning: Output files already exist:"
        if (Test-Path $OutputText) { Write-Host " - $OutputText" }
        if (Test-Path $OutputHeader) { Write-Host " - $OutputHeader" }
        $response = Read-Host "Do you want to overwrite them? (Y/N)"
        if ($response.ToUpper() -ne 'Y') {
            Write-Host "Aborting extraction."
            exit 1
        }
    }
}

# Read all bytes
$bytes = [System.IO.File]::ReadAllBytes($SourceFile)

# Find last 0x12
$last12Index = -1
for ($i = 0; $i -lt $bytes.Length; $i++) {
    if ($bytes[$i] -eq 0x12) {
        $last12Index = $i
    }
}

if ($last12Index -eq -1) {
    Write-Host "Warning: No 0x12 byte found. Assuming no header."
    $headerBytes = @()
    $textBytes = $bytes
}
else {
    $headerBytes = $bytes[0..$last12Index]
    $textBytes = $bytes[($last12Index + 1)..($bytes.Length - 1)]
}

if (-not $Execute) {
    Write-Host "[Dry Run] Would extract: $SourceFile to $OutputText and $OutputHeader"
    exit 0
}

# Save header
[System.IO.File]::WriteAllBytes($OutputHeader, $headerBytes)

# Decode text
$outputLines = @()
$currentBlock = New-Object System.Collections.Generic.List[Byte]

for ($i = 0; $i -lt $textBytes.Length; $i++) {
    $byte = $textBytes[$i]

    if ($byte -eq 0x00) {
        if ($currentBlock.Count -gt 0) {
            $decoded = [System.Text.Encoding]::UTF8.GetString($currentBlock.ToArray())
            $outputLines += $decoded
            $currentBlock.Clear()
        }
        $outputLines += "--- BLOCK ---"
    }
    elseif ($byte -eq 0x0D) {
        if (($i + 1) -lt $textBytes.Length -and $textBytes[$i + 1] -eq 0x0A) {
            if ($currentBlock.Count -gt 0) {
                $decoded = [System.Text.Encoding]::UTF8.GetString($currentBlock.ToArray())
                $outputLines += $decoded
                $currentBlock.Clear()
            }
            $i++
        }
    }
    else {
        $currentBlock.Add($byte)
    }
}

# Save any remaining text
if ($currentBlock.Count -gt 0) {
    $decoded = [System.Text.Encoding]::UTF8.GetString($currentBlock.ToArray())
    $outputLines += $decoded
}

# Save text output
$outputLines | Set-Content -Path $OutputText -Encoding UTF8

Write-Host "`n Extraction completed:"
Write-Host " - Text: $OutputText"
Write-Host " - Header: $OutputHeader"

