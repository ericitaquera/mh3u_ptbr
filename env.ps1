# === Set base working directory ===
$env:BASE_DIR = "C:\temp\mh3u_ptbr"
Write-Host "BASE_DIR set to $env:BASE_DIR`n"

# === Define and create project folders ===
$folders = @{
    ROMFS_DIR        = "$env:BASE_DIR\romfs_extracted"
    ARC_DIR          = "$env:BASE_DIR\arc_extracted"
    GMD_TXT_DIR      = "$env:BASE_DIR\gmd_texts"
    GMD_TXT_PTBR_DIR = "$env:BASE_DIR\gmd_texts_ptbr"
    GMD_REPACKED_DIR = "$env:BASE_DIR\gmd_repacked"
    ARC_REPACKED_DIR = "$env:BASE_DIR\arc_repacked"
    ROMFS_FINAL_DIR  = "$env:BASE_DIR\romfs_final"
    TMP_DIR          = "$env:BASE_DIR\tmp"
    LOG_DIR          = "$env:BASE_DIR\logs"
}

foreach ($key in $folders.Keys) {
    $path = $folders[$key]

    # Assign the environment variable
    Set-Item -Path "Env:$key" -Value $path

    # Create folder if it doesn't exist
    if (-not (Test-Path -Path $path)) {
        New-Item -ItemType Directory -Path $path | Out-Null
        Write-Host "Creating folder: $path"
    }
    else {
        Write-Host "Already Exists: $path"
    }

    Write-Host "$key set to $path`n"
}

Write-Host "All environment variables set and folders verified."




