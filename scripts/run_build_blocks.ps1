#[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

param(
    [string]$Name,
    [string]$StartFrom
)

$BUILD_FILE = "build_blocks.txt"

if (!(Test-Path $BUILD_FILE)) {
    Write-Error "❌ File '$BUILD_FILE' not found."
    exit 1
}

# ✅ Read and split into blocks
$content = Get-Content $BUILD_FILE -Raw -Encoding UTF8
$blocks = ($content -split '---') | Where-Object { $_.Trim() -ne '' }

# ✅ Prepare blocks with names
$named_blocks = @()
foreach ($block in $blocks) {
    $lines = $block -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
    if ($lines.Count -gt 0) {
        $named_blocks += [PSCustomObject]@{
            Name = $lines[0]
            Content = $block
        }
    }
}

# ✅ Handle -Name (execute only one block by name)
if ($Name) {
    $selected_blocks = $named_blocks | Where-Object { $_.Name -ieq $Name }
    if ($selected_blocks.Count -eq 0) {
        Write-Error "❌ No block found with name '$Name'. Available names:"
        $named_blocks | ForEach-Object { Write-Host " - $($_.Name)" -ForegroundColor Cyan }
        exit 1
    }
    Write-Host "➤ Executing block with name '$Name'" -ForegroundColor Cyan
}

# ✅ Handle -StartFrom (execute from this block onwards)
elseif ($StartFrom) {
    $nameList = $named_blocks | Select-Object -ExpandProperty Name
    $startIndex = ($nameList.IndexOf($StartFrom))

    if ($startIndex -eq -1) {
        Write-Error "❌ No block found with name '$StartFrom'. Available names:"
        $named_blocks | ForEach-Object { Write-Host " - $($_.Name)" -ForegroundColor Cyan }
        exit 1
    }

    $selected_blocks = $named_blocks[$startIndex..($named_blocks.Count - 1)]
    Write-Host "➤ Executing from block '$StartFrom' to the end" -ForegroundColor Cyan
}


# ✅ Default (run all)
else {
    $selected_blocks = $named_blocks
    Write-Host "➤ Executing ALL $($selected_blocks.Count) blocks" -ForegroundColor Cyan
}

# ✅ Execute blocks
$BLOCK_COUNT = 0
foreach ($block in $selected_blocks) {
    $BLOCK_COUNT++
    Write-Host "🚧 Processing Block #$BLOCK_COUNT - $($block.Name)" -ForegroundColor Cyan

    $lines = $block.Content -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
    $commandLines = $lines | Select-Object -Skip 1

    foreach ($line in $commandLines) {
        Write-Host "    ➤ Executing: $line" -ForegroundColor Yellow

        try {
            Invoke-Expression $line
            if ($LASTEXITCODE -ne 0) {
                Write-Error "❌ Command failed: $line"
                exit 1
            }
        }
        catch {
            Write-Error "❌ Error executing: $line"
            exit 1
        }
    }
}

Write-Host "✅ Finished successfully." -ForegroundColor Green
