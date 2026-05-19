param(
    [int]$Port = 8789,
    [switch]$SkipComposeUp
)

$ErrorActionPreference = "Stop"

function Show-Step {
    param([string]$Name)
    Write-Host ""
    Write-Host "==> $Name"
}

Show-Step "Host GPU"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader

Show-Step "Docker"
docker --version
docker compose version

Show-Step "Docker GPU passthrough"
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader

Show-Step "Compose config"
docker compose config --quiet

if (-not $SkipComposeUp) {
    Show-Step "Start trainer"
    $env:REC_PORT = "$Port"
    docker compose up -d
}

Show-Step "Wait for trainer UI"
$deadline = (Get-Date).AddMinutes(20)
do {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "HTTP 200 from http://localhost:$Port"
            break
        }
    } catch {
        Start-Sleep -Seconds 5
    }
} while ((Get-Date) -lt $deadline)

if (-not $response -or $response.StatusCode -ne 200) {
    throw "Trainer UI did not return HTTP 200 before the timeout."
}

Show-Step "Trainer CUDA"
docker exec micro-wake-word-gpu-starter bash -lc "source /data/.recorder-venv/bin/activate && python - <<'PY'
import json
import torch
print(json.dumps({
    'torch': torch.__version__,
    'cuda_available': torch.cuda.is_available(),
    'cuda_device_count': torch.cuda.device_count(),
    'cuda_device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
}, indent=2))
PY"

Show-Step "Local checks"
python scripts/validate_manifest.py models/example_wake_word.json --allow-missing-model
python scripts/export_esphome.py models/example_wake_word.json --output examples/hey-komi/esphome-snippet.yaml
python scripts/prepare_dataset.py data/positive data/negative --manifest examples/hey-komi/dataset_manifest.empty.example.json --allow-empty
python -m unittest discover -s tests

Write-Host ""
Write-Host "Smoke test completed."
