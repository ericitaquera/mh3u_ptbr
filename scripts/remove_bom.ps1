param(
    [Parameter(Mandatory=$true)]
    [string]$Path
)

if (Test-Path $Path -PathType Leaf) {
    $files = @((Get-Item $Path))
} elseif (Test-Path $Path -PathType Container) {
    $files = Get-ChildItem -Path $Path -File -Recurse
} else {
    Write-Error "Path not found: $Path"
    exit 1
}

$BOM = [byte[]](0xEF,0xBB,0xBF)
$BOM_COUNT = 0

foreach ($file in $files) {
    $bytes = [System.IO.File]::ReadAllBytes($file.FullName)

    if ($bytes.Length -ge 3 -and ($bytes[0] -eq 0xEF) -and ($bytes[1] -eq 0xBB) -and ($bytes[2] -eq 0xBF)) {
        Write-Host "BOM detected and removing: $($file.FullName)"
        $BOM_COUNT++

        # Remove BOM (skip first 3 bytes)
        [System.IO.File]::WriteAllBytes($file.FullName, $bytes[3..($bytes.Length - 1)])
    } else {
        Write-Host "No BOM in: $($file.FullName)"
    }
}

if ($BOM_COUNT -eq 0) {
    Write-Host "`n No BOM found in files."
} else {
    Write-Host "`n Done. $BOM_COUNT file(s) had BOM and were fixed."
}
