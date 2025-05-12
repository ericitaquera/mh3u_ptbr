param (
    [Parameter(Mandatory)]
    [string]$BlockName
)

$lines = Get-Content ".\build_blocks.txt"
$insideBlock = $false
$found = $false

foreach ($line in $lines) {
    if ($line -match "^---\s*$") {
        $insideBlock = $false
    }

    if ($insideBlock) {
        if ($line.Trim()) {
            Write-Host ">> $line"
            Invoke-Expression $line
        }
    }

    if ($line.Trim() -eq $BlockName) {
        $insideBlock = $true
        $found = $true
    }
}

if (-not $found) {
    Write-Host "Bloco '$BlockName' não encontrado." -ForegroundColor Red
}
