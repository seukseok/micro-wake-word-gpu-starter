param(
    [string]$ContainerName = "micro-wake-word-gpu-starter",
    [string]$UiUrl = "http://localhost:8789",
    [string]$DataDir = "/data",
    [string]$TrainingDatasetRoot = "workspace/training_datasets"
)

$ErrorActionPreference = "Stop"

$results = @()

function Add-Check {
    param(
        [string]$Name,
        [string]$Status,
        [string]$Details,
        [string]$Fix = ""
    )

    $script:results += [pscustomobject]@{
        Check = $Name
        Status = $Status
        Details = $Details
        Fix = $Fix
    }
}

function Invoke-Native {
    param(
        [string]$File,
        [string[]]$Arguments
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & $File @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    } catch {
        $output = @($_)
        $exitCode = 1
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    [pscustomobject]@{
        ExitCode = $exitCode
        Output = (($output | ForEach-Object { "$_" }) -join "`n")
    }
}

function Get-NvidiaLibraryPath {
    param([string]$Root)

    $paths = @(
        "$Root/.venv/lib/python3.12/site-packages/nvidia/cublas/lib",
        "$Root/.venv/lib/python3.12/site-packages/nvidia/cuda_runtime/lib",
        "$Root/.venv/lib/python3.12/site-packages/nvidia/cudnn/lib",
        "$Root/.venv/lib/python3.12/site-packages/nvidia/cufft/lib",
        "$Root/.venv/lib/python3.12/site-packages/nvidia/curand/lib",
        "$Root/.venv/lib/python3.12/site-packages/nvidia/cusolver/lib",
        "$Root/.venv/lib/python3.12/site-packages/nvidia/cusparse/lib",
        "$Root/.venv/lib/python3.12/site-packages/nvidia/cuda_cupti/lib",
        "$Root/.venv/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib",
        "$Root/.venv/lib/python3.12/site-packages/nvidia/nccl/lib",
        "$Root/.venv/lib/python3.12/site-packages/nvidia/nvjitlink/lib",
        "/usr/local/nvidia/lib64"
    )
    return ($paths -join ":")
}

$dockerAvailable = $false
$containerRunning = $false

if (Get-Command docker -ErrorAction SilentlyContinue) {
    Add-Check "docker cli" "PASS" "docker command found"
    $dockerInfo = Invoke-Native "docker" @("info")
    if ($dockerInfo.ExitCode -eq 0) {
        Add-Check "docker daemon" "PASS" "daemon is reachable"
        $dockerAvailable = $true
    } else {
        Add-Check "docker daemon" "FAIL" "daemon is not reachable" "Start Docker Desktop or Docker Engine, then rerun this script."
    }
} else {
    Add-Check "docker cli" "FAIL" "docker command not found" "Install Docker Desktop with WSL2 integration or Docker Engine."
}

if (Test-Path -LiteralPath "compose.yaml") {
    $compose = Get-Content -LiteralPath "compose.yaml" -Raw
    $missing = @()
    if ($compose -notmatch "gpus:\s*all") { $missing += "gpus: all" }
    if ($compose -notmatch "\./workspace:/data") { $missing += "./workspace:/data volume" }
    if ($compose -notmatch "REC_PORT") { $missing += "REC_PORT" }

    if ($missing.Count -eq 0) {
        Add-Check "compose.yaml" "PASS" "GPU, workspace volume, and port settings found"
    } else {
        Add-Check "compose.yaml" "FAIL" ("missing: " + ($missing -join ", ")) "Restore the starter compose.yaml settings."
    }
} else {
    Add-Check "compose.yaml" "FAIL" "compose.yaml not found" "Run this script from the repository root."
}

if ($dockerAvailable) {
    $inspect = Invoke-Native "docker" @("inspect", "-f", "{{.State.Running}}", $ContainerName)
    if ($inspect.ExitCode -eq 0 -and $inspect.Output.Trim() -eq "true") {
        Add-Check "trainer container" "PASS" "$ContainerName is running"
        $containerRunning = $true
    } else {
        Add-Check "trainer container" "FAIL" "$ContainerName is not running" "Run docker compose up -d from the repository root."
    }
} else {
    Add-Check "trainer container" "SKIP" "docker daemon unavailable"
}

if ($containerRunning) {
    $gpu = Invoke-Native "docker" @("exec", $ContainerName, "nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader")
    if ($gpu.ExitCode -eq 0) {
        Add-Check "nvidia passthrough" "PASS" ($gpu.Output.Split("`n")[0])
    } else {
        Add-Check "nvidia passthrough" "FAIL" "nvidia-smi failed in container" "Update NVIDIA drivers, Docker GPU support, and compose gpus settings."
    }

    $venv = Invoke-Native "docker" @("exec", $ContainerName, "bash", "-lc", "test -d '$DataDir/.venv'")
    if ($venv.ExitCode -eq 0) {
        Add-Check "trainer venv" "PASS" "$DataDir/.venv exists"
    } else {
        Add-Check "trainer venv" "FAIL" "$DataDir/.venv is missing" "Open the trainer UI once and let the upstream app finish dependency setup."
    }

    $ldLibraryPath = Get-NvidiaLibraryPath $DataDir
    $python = "$DataDir/.venv/bin/python"
    $torchCode = "import torch; print('cuda_available=true' if torch.cuda.is_available() else 'cuda_available=false'); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none')"
    $torch = Invoke-Native "docker" @("exec", "-e", "LD_LIBRARY_PATH=$ldLibraryPath", $ContainerName, $python, "-c", $torchCode)
    if ($torch.ExitCode -eq 0 -and $torch.Output -match "cuda_available=true") {
        $device = ($torch.Output.Split("`n") | Where-Object { $_ -and $_ -notmatch "cuda_available=" } | Select-Object -Last 1).Trim()
        Add-Check "torch cuda" "PASS" $device
    } else {
        Add-Check "torch cuda" "FAIL" "torch does not report CUDA available" "Run scripts/check_trainer_gpu.ps1 and confirm NVIDIA libraries are visible in the trainer venv."
    }

    $tfCode = "import tensorflow as tf; gpus=tf.config.list_physical_devices('GPU'); print(f'gpu_count={len(gpus)}'); print(gpus[0].name if gpus else 'none')"
    $tf = Invoke-Native "docker" @("exec", "-e", "LD_LIBRARY_PATH=$ldLibraryPath", $ContainerName, $python, "-c", $tfCode)
    if ($tf.ExitCode -eq 0 -and $tf.Output -match "gpu_count=1") {
        $device = ($tf.Output.Split("`n") | Where-Object { $_ -match "/physical_device:GPU" } | Select-Object -Last 1).Trim()
        if (-not $device) {
            $device = "GPU detected"
        }
        Add-Check "tensorflow gpu" "PASS" $device
    } else {
        Add-Check "tensorflow gpu" "FAIL" "TensorFlow does not report a GPU" "Run scripts/check_trainer_gpu.ps1; keep CPU fallback disabled for release training."
    }
} else {
    Add-Check "nvidia passthrough" "SKIP" "trainer container is not running"
    Add-Check "trainer venv" "SKIP" "trainer container is not running"
    Add-Check "torch cuda" "SKIP" "trainer container is not running"
    Add-Check "tensorflow gpu" "SKIP" "trainer container is not running"
}

try {
    $response = Invoke-WebRequest -Uri $UiUrl -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Add-Check "trainer ui" "PASS" "HTTP 200 at $UiUrl"
    } else {
        Add-Check "trainer ui" "FAIL" "HTTP $($response.StatusCode) at $UiUrl" "Check docker compose logs trainer."
    }
} catch {
    Add-Check "trainer ui" "FAIL" "cannot reach $UiUrl" "Run docker compose up -d and wait for the trainer to finish startup."
}

$datasetFolders = @(
    "negative_datasets",
    "mit_rirs_16k",
    "audioset_16k",
    "fma_16k",
    "wham_16k",
    "chime_16k"
)

foreach ($folder in $datasetFolders) {
    $path = Join-Path $TrainingDatasetRoot $folder
    if (Test-Path -LiteralPath $path) {
        $count = (Get-ChildItem -LiteralPath $path -File -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
        if ($count -gt 0) {
            Add-Check "dataset:$folder" "PASS" "$count files"
        } else {
            Add-Check "dataset:$folder" "WARN" "folder exists but has no files" "Prepare or convert this dataset before full training."
        }
    } else {
        Add-Check "dataset:$folder" "WARN" "folder missing" "Run scripts/prepare_training_datasets.ps1 for dataset status and next steps."
    }
}

Write-Host ""
Write-Host "micro-wake-word-gpu-starter doctor"
Write-Host ""
$results | Format-Table Check, Status, Details -AutoSize

$fixes = $results | Where-Object { $_.Fix }
if ($fixes) {
    Write-Host ""
    Write-Host "Fix hints:"
    foreach ($item in $fixes) {
        Write-Host "- $($item.Check): $($item.Fix)"
    }
}

$failures = $results | Where-Object { $_.Status -eq "FAIL" }
if ($failures) {
    exit 1
}

exit 0
