param(
    [string]$ContainerName = "micro-wake-word-gpu-starter",
    [string]$DataDir = "/data"
)

$ErrorActionPreference = "Stop"

$nvidiaLibs = @(
    "$DataDir/.venv/lib/python3.12/site-packages/nvidia/cublas/lib",
    "$DataDir/.venv/lib/python3.12/site-packages/nvidia/cuda_runtime/lib",
    "$DataDir/.venv/lib/python3.12/site-packages/nvidia/cudnn/lib",
    "$DataDir/.venv/lib/python3.12/site-packages/nvidia/cufft/lib",
    "$DataDir/.venv/lib/python3.12/site-packages/nvidia/curand/lib",
    "$DataDir/.venv/lib/python3.12/site-packages/nvidia/cusolver/lib",
    "$DataDir/.venv/lib/python3.12/site-packages/nvidia/cusparse/lib",
    "$DataDir/.venv/lib/python3.12/site-packages/nvidia/cuda_cupti/lib",
    "$DataDir/.venv/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib",
    "$DataDir/.venv/lib/python3.12/site-packages/nvidia/nccl/lib",
    "$DataDir/.venv/lib/python3.12/site-packages/nvidia/nvjitlink/lib",
    "/usr/local/nvidia/lib64"
)

$ldLibraryPath = $nvidiaLibs -join ":"

$bash = @"
set -euo pipefail

echo "== nvidia-smi =="
nvidia-smi --query-gpu=name,driver_version,memory.total,compute_cap --format=csv,noheader

source "$DataDir/.venv/bin/activate"

echo
echo "== torch =="
python -c 'import json, torch; print(json.dumps({"torch": torch.__version__, "cuda_available": torch.cuda.is_available(), "device_count": torch.cuda.device_count(), "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}, indent=2))'

echo
echo "== tensorflow =="
python -c 'import json, tensorflow as tf; print(json.dumps({"tensorflow": tf.__version__, "gpus": [device.name for device in tf.config.list_physical_devices("GPU")]}, indent=2))'
"@

$bash = $bash.Replace("`r", "")
$bash | docker exec -i -e "LD_LIBRARY_PATH=$ldLibraryPath" $ContainerName bash
