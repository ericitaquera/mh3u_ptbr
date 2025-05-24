# === Set base working directory ===
$env:BASE_DIR = "C:\tmp\mh3u_ptbr"
Write-Host "BASE_DIR set to $env:BASE_DIR"

# === Set tools directory ===
$env:TOOLS_DIR = "$env:BASE_DIR\tools"
Write-Host "TOOLS_DIR set to $env:TOOLS_DIR`n"

# === Define and create project folders ===
$folders = @{
    ROMFS_DIR        = "$env:BASE_DIR\romfs_extracted"
    ARC_EXTRACTED_DIR    = "$env:BASE_DIR\arc_extracted"
    GMD_TXT_DIR      = "$env:BASE_DIR\gmd_texts"
    GMD_TXT_PTBR_DIR = "$env:BASE_DIR\gmd_texts_ptbr"
    GMD_REPACKED_DIR     = "$env:BASE_DIR\gmd_repacked"
    QTDS_TEXT_DIR    = "$env:BASE_DIR\qtds_texts"
    QTDS_TEXT_PTBR_DIR    = "$env:BASE_DIR\qtds_texts_ptbr"
    QTDS_REPACKED       = "$env:BASE_DIR\qtds_repacked"
    ARC_REPACKED_DIR = "$env:BASE_DIR\arc_repacked"
    ROMFS_FINAL_DIR  = "$env:BASE_DIR\romfs_final"
    SCRIPTS          = "$env:BASE_DIR\scripts"
    TMP_DIR          = "$env:BASE_DIR\tmp"
    LOG_DIR          = "$env:BASE_DIR\logs"
    TOOLS_DIR        = "$env:BASE_DIR\tools"
    QUICKBMS_SCRIPTS_DIR            = "$env:BASE_DIR\quickbms_scripts"
    PROMPTS_GPT         = "$env:BASE_DIR\prompts_gpt"
    MOD_PATH_DIR        = "$env:BASE_DIR\luma\titles\00040000000AE400\romfs\"

}

foreach ($key in $folders.Keys) {
    $path = $folders[$key]

    # Assign the environment variable
    Set-Item -Path "Env:$key" -Value $path

    # Create folder if it doesn't exist
    if (-not (Test-Path -Path $path)) {
        New-Item -ItemType Directory -Path $path | Out-Null
        Write-Host "Created folder: $path"
    }
    else {
        Write-Host "Exists: $path"
    }

    Write-Host "$key set to $path`n"
}

Write-Host "All environment variables set and folders verified."
