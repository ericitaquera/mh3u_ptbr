param (
    [Parameter(Mandatory)]
    [string]$InputFile
)

if (-not (Test-Path $InputFile)) {
    Write-Host "Arquivo não encontrado: $InputFile" -ForegroundColor Red
    exit 1
}

# Extrai nome base e extensão
$filename = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
$ext = [System.IO.Path]::GetExtension($InputFile)
$directory = [System.IO.Path]::GetDirectoryName($InputFile)
$outputFile = Join-Path $directory "$filename.ordered$ext"

# Ordena com base apenas no nome do arquivo
Get-Content $InputFile |
Sort-Object { [System.IO.Path]::GetFileName($_) } |
Set-Content $outputFile

Write-Host "✅ Arquivo ordenado salvo como: $outputFile"
