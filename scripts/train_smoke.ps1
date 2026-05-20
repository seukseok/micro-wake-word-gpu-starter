param(
    [string]$ContainerName = "micro-wake-word-gpu-starter",
    [string]$WakeWord = "hey komi",
    [string]$WakeWordTitle = "Hey Komi",
    [int]$Samples = 50,
    [int]$BatchSize = 10,
    [int]$TrainingSteps = 20
)

$ErrorActionPreference = "Stop"

$dataDir = "/data"
$nvidiaLibs = @(
    "$dataDir/.venv/lib/python3.12/site-packages/nvidia/cublas/lib",
    "$dataDir/.venv/lib/python3.12/site-packages/nvidia/cuda_runtime/lib",
    "$dataDir/.venv/lib/python3.12/site-packages/nvidia/cudnn/lib",
    "$dataDir/.venv/lib/python3.12/site-packages/nvidia/cufft/lib",
    "$dataDir/.venv/lib/python3.12/site-packages/nvidia/curand/lib",
    "$dataDir/.venv/lib/python3.12/site-packages/nvidia/cusolver/lib",
    "$dataDir/.venv/lib/python3.12/site-packages/nvidia/cusparse/lib",
    "$dataDir/.venv/lib/python3.12/site-packages/nvidia/cuda_cupti/lib",
    "$dataDir/.venv/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib",
    "$dataDir/.venv/lib/python3.12/site-packages/nvidia/nccl/lib",
    "$dataDir/.venv/lib/python3.12/site-packages/nvidia/nvjitlink/lib",
    "/usr/local/nvidia/lib64"
)

$ldLibraryPath = $nvidiaLibs -join ":"

$bash = @'
set -euo pipefail

source /data/.venv/bin/activate
python -c "import tensorboard" 2>/dev/null || python -m pip install tensorboard
train_wake_word --data-dir=/data --samples="${SMOKE_SAMPLES}" --batch-size="${SMOKE_BATCH_SIZE}" --training-steps="${SMOKE_TRAINING_STEPS}" "${SMOKE_WAKE_WORD}" "${SMOKE_WAKE_WORD_TITLE}"
'@

$bash = $bash.Replace("`r", "")
$bash | docker exec -i `
    -e "LD_LIBRARY_PATH=$ldLibraryPath" `
    -e "SMOKE_WAKE_WORD=$WakeWord" `
    -e "SMOKE_WAKE_WORD_TITLE=$WakeWordTitle" `
    -e "SMOKE_SAMPLES=$Samples" `
    -e "SMOKE_BATCH_SIZE=$BatchSize" `
    -e "SMOKE_TRAINING_STEPS=$TrainingSteps" `
    $ContainerName bash
