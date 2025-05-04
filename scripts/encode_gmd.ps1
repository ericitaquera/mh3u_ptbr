# gmd_encode.ps1 (with line length validation)
param(
    [Alias("SourceFile")]
    [Parameter(Mandatory = $true)]
    [string]$InputFile
)

# Define output filenames
if (-not $env:GMD_REPACKED_DIR) {
    Write-Host "Error: Environment variable GMD_REPACKED_DIR not defined."
    exit 1
}

# Check input file
if (!(Test-Path $InputFile)) {
    Write-Host "Error: Cannot find path '$InputFile'"
    exit 1
}

$relativePath = $InputFile.Substring($env:GMD_TXT_PTBR_DIR.Length).TrimStart('\')
Write-Host "relativePath: $RelativePath"
$baseName = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
$targetDir = Join-Path $env:GMD_REPACKED_DIR ([System.IO.Path]::GetDirectoryName($relativePath))
if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

$headerRelativePath = $InputFile.Substring($env:GMD_TXT_PTBR.Length).TrimStart('\')
$HeaderFile = Join-Path $env:GMD_TXT_DIR ($RelativePath -replace '\.txt$', '.header')


$OutputGmd = Join-Path $targetDir ($baseName + ".gmd")

# Read header
if (!(Test-Path $HeaderFile)) {
    Write-Host "Error: Missing header file '$HeaderFile'"
    exit 1
}
$headerBytes = [System.IO.File]::ReadAllBytes($HeaderFile)

# Read all lines
$lines = Get-Content -Path $InputFile -Encoding UTF8 | Where-Object { $_.Trim() -ne "" }

# 🛡️ Validation step: check for long lines
$offendingLines = @()
for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    if ($line.Trim() -ne "--- BLOCK ---" -and $line.Length -gt 100) {
        $offendingLines += ($i + 1)  # 1-based line number
    }
}

if ($offendingLines.Count -gt 0) {
    Write-Host "`n Error: The following lines exceed 43 characters:`n"
    foreach ($lineNumber in $offendingLines) {
        Write-Host " - Line $lineNumber"
    }
    exit 1
}

# Build text bytes
$textBytes = New-Object System.Collections.Generic.List[Byte]

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]

    if ($line.Trim() -eq "--- BLOCK ---") {
        $textBytes.Add(0x00)
    }
    else {
        $utf8Bytes = [System.Text.Encoding]::UTF8.GetBytes($line)
        $textBytes.AddRange($utf8Bytes)

        # Only add 0D 0A if the next line is NOT a block separator
        if (($i + 1) -lt $lines.Count -and $lines[$i + 1].Trim() -ne "--- BLOCK ---") {
            $textBytes.Add(0x0D)
            $textBytes.Add(0x0A)
        }
    }
}

# Final file = header + rebuilt text
$finalBytes = $headerBytes + $textBytes.ToArray()

# Save final GMD
[System.IO.File]::WriteAllBytes($OutputGmd, $finalBytes)

Write-Host "`n✅ Successfully rebuilt:"
Write-Host " - $OutputGmd"


