# 셋업/사용 가이드

한국어 | [English](setup-and-usage.md)

이 문서는 처음 clone한 상태에서 ESPHome용 micro wake word 산출물을 검증하고 적용하는 흐름까지 안내합니다.

## 1. 사전 준비

권장 환경:

- Windows 11
- 최신 드라이버가 설치된 NVIDIA GPU
- WSL2 integration이 켜진 Docker Desktop
- helper script 실행용 Python 3.11 이상

호스트 GPU 확인:

```powershell
nvidia-smi
```

Docker에서 GPU가 보이는지 확인:

```powershell
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

Linux 사용자는 같은 Docker 명령을 shell에서 실행하면 됩니다. Python 명령의 경로 구분자는 `/`를 사용하세요.

## 2. 트레이너 UI 실행

저장소를 받고 트레이너를 시작합니다.

```powershell
git clone https://github.com/seukseok/micro-wake-word-gpu-starter.git
cd micro-wake-word-gpu-starter
docker compose up -d
```

브라우저에서 엽니다.

```text
http://localhost:8789
```

첫 실행은 upstream trainer가 `workspace/` 아래 Python 환경을 준비하므로 시간이 걸릴 수 있습니다.

## 3. 현재 환경 진단

doctor를 실행합니다.

```powershell
.\scripts\doctor.ps1
```

doctor가 확인하는 항목:

- Docker CLI와 daemon
- `compose.yaml`
- trainer container
- NVIDIA passthrough
- trainer virtual environment
- Torch CUDA
- TensorFlow GPU
- trainer UI
- 대용량 trainer dataset 폴더

실패한 항목이 있으면 표 아래의 fix hint를 따라 조치한 뒤 다시 실행합니다.

## 4. 후보 모델을 ESPHome에 적용

[v0.2.0 MVP release](https://github.com/seukseok/micro-wake-word-gpu-starter/releases/tag/v0.2.0-mvp)에서 아래 파일을 받습니다.

```text
hey_komi.tflite
hey_komi.json
```

두 파일을 ESPHome이 접근할 수 있는 같은 폴더에 넣습니다.

```text
/config/esphome/models/
```

ESPHome 설정은 아래 형태를 사용합니다.

```yaml
micro_wake_word:
  models:
    - model: /config/esphome/models/hey_komi.json
      id: hey_komi_wake_word
```

중요: `Hey Komi`는 후보 모델입니다. 실제 ESP32-S3 마이크 테스트 리포트가 모이기 전까지는 hardware-validated 모델이 아닙니다.

## 5. 직접 학습하기

데이터셋 준비 상태를 확인합니다.

```powershell
.\scripts\prepare_training_datasets.ps1
```

트레이너 UI에서 wake phrase와 학습 설정을 입력합니다. 학습 결과는 아래 폴더에 생성됩니다.

```text
workspace/trained_wake_words/
```

아주 작은 end-to-end 경로 테스트는 아래 명령으로 실행할 수 있습니다.

```powershell
.\scripts\train_smoke.ps1 -WakeWord "hey komi" -WakeWordTitle "Hey Komi" -Samples 50 -BatchSize 10 -TrainingSteps 20
```

Smoke training은 파이프라인 동작 확인용입니다. 실사용 모델 품질을 보장하지 않습니다.

## 6. 결과물 검증

manifest 검증:

```powershell
python scripts\validate_manifest.py workspace\trained_wake_words\hey_komi.json
```

ESPHome snippet 출력:

```powershell
python scripts\export_esphome.py workspace\trained_wake_words\hey_komi.json
```

출력 예시:

```yaml
micro_wake_word:
  models:
    - model: /config/esphome/models/hey_komi.json
      id: hey_komi_wake_word
```

생성된 `.json`과 `.tflite` 파일을 ESPHome 모델 폴더에 함께 넣습니다.

## 7. 문제 해결

Docker가 연결되지 않을 때:

```powershell
docker info
```

Docker Desktop을 시작하고 `.\scripts\doctor.ps1`를 다시 실행합니다.

트레이너 UI가 열리지 않을 때:

```powershell
docker compose logs trainer
```

TensorFlow나 Torch가 GPU를 보지 못할 때:

```powershell
.\scripts\check_trainer_gpu.ps1
```

데이터셋이 부족해 보일 때:

```powershell
.\scripts\prepare_training_datasets.ps1
```

모델 검증이 실패하면 `.json`과 `.tflite`가 같은 폴더에 있는지, JSON의 `model` 필드가 실제 `.tflite` 파일 이름과 같은지 확인하세요.

## 테스트 리포트에 포함할 내용

실제 하드웨어 테스트 이슈에는 아래 정보를 포함하면 좋습니다.

- board
- microphone
- room type
- model version
- `probability_cutoff`와 `sliding_window_size`
- false wakes per hour
- missed wakes out of at least 20 attempts
