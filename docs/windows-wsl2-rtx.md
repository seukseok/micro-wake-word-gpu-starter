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
