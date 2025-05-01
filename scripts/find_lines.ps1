# compare_blocks.ps1
param(
    [Parameter(Mandatory = $true)]
    [string]$File1,
    [Parameter(Mandatory = $true)]
    [string]$File2
)

# Read files
$lines1 = Get-Content -Path $File1 -Encoding UTF8
$lines2 = Get-Content -Path $File2 -Encoding UTF8

# Find all --- BLOCK --- line numbers
$blocks1 = @()
$blocks2 = @()

for ($i = 0; $i -lt $lines1.Count; $i++) {
    if ($lines1[$i].Trim() -eq "--- BLOCK ---") {
        $blocks1 += ($i + 1)
    }
}

for ($i = 0; $i -lt $lines2.Count; $i++) {
    if ($lines2[$i].Trim() -eq "--- BLOCK ---") {
        $blocks2 += ($i + 1)
    }
}

# Find minimum block count to compare safely
$minBlocks = [Math]::Min($blocks1.Count, $blocks2.Count)

# Compare block by block
for ($i = 0; $i -lt $minBlocks; $i++) {
    if ($blocks1[$i] -ne $blocks2[$i]) {
        Write-Host "`n❌ First mismatch detected at block $($i+1):"
        Write-Host " - $File1 block at line $($blocks1[$i])"
        Write-Host " - $File2 block at line $($blocks2[$i])"
        exit 1
    }
}

# If one file has more blocks after matching all the common ones
if ($blocks1.Count -ne $blocks2.Count) {
    Write-Host "`n❌ Block count differs after matched blocks:"
    Write-Host " - $File1 blocks: $($blocks1.Count)"
    Write-Host " - $File2 blocks: $($blocks2.Count)"
    exit 1
}

# If all blocks match
Write-Host "`n✅ Block structure matches perfectly!"
