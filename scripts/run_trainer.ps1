param(
    [int]$Port = 8789
)

$ErrorActionPreference = "Stop"

Write-Host "Checking Docker..."
docker --version

Write-Host "Checking Docker Compose..."
docker compose version

Write-Host "Checking NVIDIA GPU visibility from Docker..."
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi

$env:REC_PORT = "$Port"
Write-Host "Starting trainer on http://localhost:$Port"
docker compose up
