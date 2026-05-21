# micro-wake-word-gpu-starter

한국어 | [English](README.en.md)

NVIDIA GPU로 ESPHome용 커스텀 micro wake word 모델을 학습하고 패키징하는 스타터 킷입니다.

![실제 트레이너 UI 데모](docs/assets/trainer-ui-demo.gif)

실제 실행 중인 트레이너 UI를 녹화한 화면입니다. 동영상으로 보려면 [raw MP4 데모](https://raw.githubusercontent.com/seukseok/micro-wake-word-gpu-starter/main/docs/assets/trainer-ui-demo.mp4)를 열면 됩니다.

## 먼저 고르세요

| 목적 | 바로 할 일 |
| --- | --- |
| 후보 모델만 써보기 | [v0.2.0 MVP release](https://github.com/seukseok/micro-wake-word-gpu-starter/releases/tag/v0.2.0-mvp)에서 `hey_komi.tflite`와 `hey_komi.json`을 받아 ESPHome 모델 폴더에 넣습니다. |
| GPU 트레이너 실행하기 | Docker Desktop을 켜고 `docker compose up -d` 실행 후 `http://localhost:8789`를 엽니다. |
| 직접 학습하기 | `doctor.ps1`로 환경을 확인하고, 데이터셋 상태 점검, smoke training, manifest 검증, ESPHome export 순서로 진행합니다. |

자세한 단계별 설명은 [셋업/사용 가이드](docs/setup-and-usage.ko.md)를 보세요.

## 빠른 시작

Windows PowerShell 기준:

```powershell
git clone https://github.com/seukseok/micro-wake-word-gpu-starter.git
cd micro-wake-word-gpu-starter
docker compose up -d
.\scripts\doctor.ps1
```

브라우저에서 트레이너 UI를 엽니다.

```text
http://localhost:8789
```

트레이너용 대용량 데이터셋 상태를 확인합니다.

```powershell
.\scripts\prepare_training_datasets.ps1
```

생성된 모델을 검증하고 ESPHome snippet을 출력합니다.

```powershell
python scripts\validate_manifest.py workspace\trained_wake_words\hey_komi.json
python scripts\export_esphome.py workspace\trained_wake_words\hey_komi.json
```

학습 결과물은 기본적으로 아래 위치에 생성됩니다.

```text
workspace/trained_wake_words/<wake_word>.tflite
workspace/trained_wake_words/<wake_word>.json
```

## 후보 모델 사용

지금 바로 써볼 파일:

```text
models/hey-komi-candidate/hey_komi.tflite
models/hey-komi-candidate/hey_komi.json
models/hey-komi-candidate/model-card.md
```

릴리스에서 다운로드:

- [micro-wake-word-gpu-starter v0.2.0 MVP](https://github.com/seukseok/micro-wake-word-gpu-starter/releases/tag/v0.2.0-mvp)
- [Hey Komi v0.1.0 candidate](https://github.com/seukseok/micro-wake-word-gpu-starter/releases/tag/v0.1.0-candidate)

ESPHome에는 `.tflite`와 `.json`을 같은 모델 폴더에 넣고, export script가 출력한 경로를 사용합니다.

```yaml
micro_wake_word:
  models:
    - model: /config/esphome/models/hey_komi.json
      id: hey_komi_wake_word
```

아직 `hardware-validated` 모델은 아닙니다. 실제 ESP32-S3 마이크에서 false wake와 missed wake 테스트가 끝나기 전까지는 candidate로 취급해야 합니다.

## 직접 학습 흐름

1. `docker compose up -d`로 트레이너를 실행합니다.
2. `.\scripts\doctor.ps1`로 Docker, GPU, Torch, TensorFlow, UI, 데이터셋 상태를 확인합니다.
3. `http://localhost:8789`에서 wake phrase와 학습 설정을 입력합니다.
4. 결과로 나온 `.tflite`와 `.json`을 검증합니다.
5. `python scripts\export_esphome.py ...` 출력값을 ESPHome 설정에 붙입니다.

짧은 end-to-end 학습 확인:

```powershell
.\scripts\train_smoke.ps1 -WakeWord "hey komi" -WakeWordTitle "Hey Komi" -Samples 50 -BatchSize 10 -TrainingSteps 20
```

## 검증된 환경

- NVIDIA GeForce RTX 5070 Ti
- Windows 11 + Docker Desktop
- Docker GPU passthrough 확인
- Torch `cuda_available: true` 확인
- TensorFlow `/physical_device:GPU:0` 인식 확인
- GitHub Actions CI 통과

## 데이터셋

데이터셋 카탈로그는 [datasets/catalog.json](datasets/catalog.json)에 있습니다.

```powershell
python scripts\show_datasets.py --recommended first
.\scripts\prepare_training_datasets.ps1
```

대표 소스:

- `kahrendt/microwakeword`: background/negative feature archive
- Google Speech Commands v0.02: 단어 음성 클립
- MLCommons Multilingual Spoken Words microset: 다국어 단어 음성 클립
- FSD50K: 환경음 hard negative

## 앞으로 할 계획

- ESP32-S3 테스트 리포트 수집
- Hardware-validated 모델 릴리스
- 대용량 데이터셋 다운로드/압축해제/변환 자동 재개 개선
- 실제 하드웨어 테스트 영상 또는 짧은 시연 MP4 추가

## 관련 문서

- [셋업/사용 가이드](docs/setup-and-usage.ko.md)
- [Windows/WSL2/RTX guide](docs/windows-wsl2-rtx.md)
- [Dataset guide](docs/dataset-guide.md)
- [Model quality gates](docs/model-quality-gates.md)
- [Release demo assets](docs/release-demo-assets.md)
- [Release playbook](docs/release-playbook.md)
- [Hey Komi model card](models/hey-komi-candidate/model-card.md)

## 라이선스

MIT. Upstream 프로젝트는 각자의 라이선스를 따릅니다.
