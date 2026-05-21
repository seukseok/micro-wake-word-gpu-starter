param(
    [string]$TrainingDatasetRoot = "workspace/training_datasets",
    [switch]$FailOnMissing
)

$ErrorActionPreference = "Stop"

$datasets = @(
    [pscustomobject]@{ Name = "negative_datasets"; Role = "required negatives"; MinimumFiles = 1; NextAction = "Run the upstream negative dataset preparation." },
    [pscustomobject]@{ Name = "mit_rirs_16k"; Role = "required room impulse responses"; MinimumFiles = 1; NextAction = "Prepare MIT RIR and convert to 16 kHz WAV." },
    [pscustomobject]@{ Name = "audioset_16k"; Role = "recommended ambient audio"; MinimumFiles = 1000; NextAction = "Convert AudioSet clips to 16 kHz WAV." },
    [pscustomobject]@{ Name = "fma_16k"; Role = "recommended music negatives"; MinimumFiles = 1000; NextAction = "Convert FMA small MP3 clips to 16 kHz WAV." },
    [pscustomobject]@{ Name = "wham_16k"; Role = "optional noise negatives"; MinimumFiles = 1; NextAction = "Prepare WHAM noise if you need stronger noise augmentation." },
    [pscustomobject]@{ Name = "chime_16k"; Role = "optional home noise negatives"; MinimumFiles = 1; NextAction = "Prepare CHiME if you need stronger room-noise augmentation." }
)

function Get-FolderStats {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return [pscustomobject]@{ Exists = $false; FileCount = 0; SizeGiB = 0.0 }
    }

    $measure = Get-ChildItem -LiteralPath $Path -File -Recurse -ErrorAction SilentlyContinue |
        Measure-Object -Property Length -Sum
    $size = 0.0
    if ($measure.Sum) {
        $size = [math]::Round(($measure.Sum / 1GB), 2)
    }

    return [pscustomobject]@{
        Exists = $true
        FileCount = [int]$measure.Count
        SizeGiB = $size
    }
}

$rows = @()
foreach ($dataset in $datasets) {
    $path = Join-Path $TrainingDatasetRoot $dataset.Name
    $stats = Get-FolderStats $path
    $status = "Missing"

    if ($stats.Exists -and $stats.FileCount -ge $dataset.MinimumFiles) {
        $status = "Ready"
    } elseif ($stats.Exists -and $stats.FileCount -gt 0) {
        $status = "Partial"
    }

    $next = ""
    if ($status -ne "Ready") {
        $next = $dataset.NextAction
    }

    $rows += [pscustomobject]@{
        Dataset = $dataset.Name
        Status = $status
        Files = $stats.FileCount
        SizeGiB = $stats.SizeGiB
        Role = $dataset.Role
        NextAction = $next
    }
}

Write-Host ""
Write-Host "Training dataset status"
Write-Host ""
$rows | Format-Table Dataset, Status, Files, SizeGiB, Role -AutoSize

$nextSteps = $rows | Where-Object { $_.NextAction }
if ($nextSteps) {
    Write-Host ""
    Write-Host "Next actions:"
    foreach ($row in $nextSteps) {
        Write-Host "- $($row.Dataset): $($row.NextAction)"
    }
}

if ($FailOnMissing -and ($rows | Where-Object { $_.Status -ne "Ready" })) {
    exit 1
}

exit 0
