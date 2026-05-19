# Windows, WSL2, and RTX Setup

This is the path most RTX 40/50 series users should try first.

## 1. Check the NVIDIA driver

Open PowerShell:

```powershell
nvidia-smi
```

If this fails, install or update the NVIDIA Game Ready or Studio driver before debugging Docker.

## 2. Install Docker Desktop

Use Docker Desktop with WSL2 integration enabled.

In Docker Desktop:

```text
Settings -> General -> Use the WSL 2 based engine
Settings -> Resources -> WSL Integration -> enable your distro
```

## 3. Verify GPU access from Docker

```powershell
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

If this works, the trainer container should be able to see your GPU.

## 4. Start the trainer

From the repository folder:

```powershell
docker compose up
```

Then open:

```text
http://localhost:8789
```

## 5. RTX 50 series notes

Use the latest NVIDIA driver and Docker Desktop release. If TensorFlow inside an upstream image does not recognize a very new GPU, try again after updating the image, or open an issue with:

- GPU model
- driver version
- `docker --version`
- `docker compose version`
- the output of the CUDA `nvidia-smi` test above

## Verified smoke test

This starter was smoke-tested on:

```text
NVIDIA GeForce RTX 5070 Ti, driver 591.86, 16303 MiB
Docker version 29.0.1
Docker Compose v2.40.3-desktop.1
```

The trainer UI returned `HTTP 200` on `http://localhost:8789`, and Torch inside the container reported:

```json
{
  "torch": "2.12.0+cu130",
  "cuda_available": true,
  "cuda_device_count": 1,
  "cuda_device_name": "NVIDIA GeForce RTX 5070 Ti"
}
```

The first boot may take 15-20 minutes while the trainer creates `/data/.recorder-venv` and installs dependencies. After that, a warm restart reached `HTTP 200` in 5.3 seconds on the test machine.
