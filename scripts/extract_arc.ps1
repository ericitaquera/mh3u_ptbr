# === extract_arc.ps1 ===
# Extract all files from a source .arc file or dir (or ROMFS_DIR by default) into ARC_EXTRACTED using QuickBMS
# Defaults to dry-run unless -Execute is used

param(
    [switch]$Execute,
    [Alias("dry-run")]
    [switch]$DryRun = $true,
    [switch]$Force,
    [string]$SourceDir,
    [string]$SourceFile,
    [switch]$Help
)

if ($Help) {
    Write-Host """HELP:
  .\extract_arc.ps1 [-Execute] [-Force] [-SourceDir <path>] [-SourceFile <file.arc>] [-Help]

  By default, the script runs in dry-run mode. Use -Execute to perform extraction.

  PARAMETERS:
    -Execute      Actually extract .arc files (default is dry-run)
    -Force        Re-extract even if target folder already exists
    -SourceDir    Optional. Path to folder containing .arc files (defaults to ROMFS_DIR)
    -SourceFile   Optional. Specific ARC file to extract instead of scanning a folder
    -Help         Show this help message

  LOGGING:
    Extracted files are logged to: $env:LOG_DIR\arc_extracted.log

  TOOL:
    Uses quickbms.exe + mh3u.bms from: $env:TOOLS_DIR\quickbms
    https://aluigi.altervista.org/quickbms.htm
"""
    exit 0
}

Write-Host "USAGE:"
Write-Host "  .\extract_arc.ps1 [-Execute] [-Force] [-SourceDir <path>] [-SourceFile <file.arc>] [-Help]"
Write-Host "  By default, runs in dry-run mode. Use -Execute to actually extract."
Write-Host "  ARC files will be extracted into ARC_EXTRACTED."
Write-Host ""

# Ensure environment is loaded
if (-not $env:ROMFS_DIR -or -not $env:ARC_EXTRACTED -or -not $env:TOOLS_DIR -or -not $env:LOG_DIR -or -not $env:QUICKBMS_SCRIPTS_DIR) {
    Write-Error "Missing environment setup. Please run env.ps1 first."
    exit 1
}

$QUICKBMS = "$env:TOOLS_DIR\quickbms\quickbms.exe"
$SCRIPT = "$env:QUICKBMS_SCRIPTS_DIR\extract_all.bms"
$LOG_FILE = "$env:LOG_DIR\arc_extracted.log"

if (-not (Test-Path $QUICKBMS)) {
    Write-Error "quickbms.exe not found at: $QUICKBMS"
    exit 1
}

if (-not (Test-Path $SCRIPT)) {
    Write-Error "BMS script not found at: $SCRIPT"
    exit 1
}

if ($SourceFile -and (Test-Path $SourceFile -PathType Leaf)) {
    $arcFiles = @(Get-Item -LiteralPath (Resolve-Path $SourceFile).Path)
    $SOURCE = Split-Path -Parent $arcFiles[0].FullName
    $BASE_TARGET = $env:ARC_EXTRACTED
} elseif ($SourceDir -and (Test-Path $SourceDir -PathType Container)) {
    $SOURCE = (Resolve-Path $SourceDir).Path
    $BASE_TARGET = $env:ARC_EXTRACTED
    $allArcs = Get-ChildItem -Path $SOURCE -Recurse -Filter '*.arc' -File
    $arcFiles = @()
    foreach ($file in $allArcs) {
        $arcFiles += $file
    }
}

if (-not $arcFiles -or $arcFiles.Count -eq 0) {
    Write-Host "No .arc files found in $SOURCE"
    Write-Host "Use -Help for more details."
    exit 0
}

"# Extracted ARC files - $(Get-Date)" | Out-File -FilePath $LOG_FILE -Encoding UTF8

foreach ($arc in $arcFiles) {
    if ($SourceFile) {
        $relativePath = $arc.FullName.Substring($env:ROMFS_DIR.Length).TrimStart('\')
    } else {
        $relativePath = $arc.FullName.Substring($env:ROMFS_DIR.Length).TrimStart('\')
    }
    $targetDir = Join-Path $BASE_TARGET $relativePath

    $shouldExtract = $Force -or -not (Test-Path $targetDir)

    if ($shouldExtract) {
        if ($DryRun -and -not $Execute) {
            Write-Host "[Dry Run] Would extract: $($arc.FullName) to $targetDir"
        } else {
            if (-not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
            Write-Host "Extracting: $($arc.FullName)"
            $cmdLine = "CMD: {0} `"{1}`" `"{2}`" `"{3}`"" -f $QUICKBMS, $SCRIPT, $arc.FullName, $targetDir
            Write-Host $cmdLine
            & $QUICKBMS $SCRIPT "$($arc.FullName)" "$targetDir"

            if ($LASTEXITCODE -eq 0) {
                "$($arc.FullName) => $targetDir" | Out-File -FilePath $LOG_FILE -Append -Encoding UTF8
            } else {
                Write-Host "Failed to extract: $($arc.FullName)"
                exit 1
            }
        }
    } else {
        Write-Host "Skipping (already exists): $($targetDir) remove/backup it or use -Force to overwrite"
    }
}

Write-Host "All ARC files processed. Log written to $LOG_FILE"
