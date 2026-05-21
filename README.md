# micro-wake-word-gpu-starter

한국어 | [English](README.en.md)

NVIDIA GPU로 ESPHome용 커스텀 micro wake word 모델을 학습하고 패키징하는 스타터 킷입니다.

![실제 트레이너 UI 데모](docs/assets/trainer-ui-demo.gif)

실제 실행 중인 트레이너 UI를 녹화한 화면입니다. 동영상으로 보려면 [raw MP4 데모](https://raw.githubusercontent.com/seukseok/micro-wake-word-gpu-starter/main/docs/assets/trainer-ui-demo.mp4)를 열면 됩니다.

## 무엇을 할 수 있나요?

- Docker Compose로 NVIDIA GPU 기반 microWakeWord 트레이너 UI를 실행합니다.
- 학습 결과물인 `.tflite` 모델과 ESPHome용 `.json` manifest를 검증합니다.
- 공개 데이터셋 준비, GPU 점검, ESPHome YAML 생성을 스크립트로 도와줍니다.
- RTX 5070 Ti에서 실제 학습한 `Hey Komi` 후보 모델과 model card를 제공합니다.

## 빠른 시작

필요한 것:

- Windows 11 또는 Linux
- 최신 드라이버가 설치된 NVIDIA GPU
- Docker Desktop + WSL2 integration, 또는 Linux Docker Engine

트레이너 실행:

```bash
docker compose up
```

브라우저에서 열기:

```text
http://localhost:8789
```

학습 결과물은 기본적으로 아래 위치에 생성됩니다.

```text
workspace/trained_wake_words/<wake_word>.tflite
workspace/trained_wake_words/<wake_word>.json
```

manifest 검증과 ESPHome snippet 생성:

```bash
python scripts/validate_manifest.py workspace/trained_wake_words/hey_komi.json
python scripts/export_esphome.py workspace/trained_wake_words/hey_komi.json
```

GPU 학습 환경 점검:

```powershell
.\scripts\check_trainer_gpu.ps1
.\scripts\doctor.ps1
```

## 후보 모델

`Hey Komi` 후보 모델은 실제 RTX 5070 Ti GPU 학습으로 생성했습니다.

```text
models/hey-komi-candidate/hey_komi.tflite
models/hey-komi-candidate/hey_komi.json
models/hey-komi-candidate/model-card.md
```

다운로드: [Hey Komi v0.1.0 candidate](https://github.com/seukseok/micro-wake-word-gpu-starter/releases/tag/v0.1.0-candidate)

```text
Samples: 5,000 generated wake-word clips
Training steps: 5,000
Trainer result: Training complete (GPU path)
CPU fallback: false
Elapsed time: 0:21:31
Calibration: cutoff=0.34, window=3, recall=97.70%, ambient_faph=0.724
TFLite streaming test: cutoff=0.89 -> frr=0.0520, faph=0.000
```

아직 `hardware-validated` 모델은 아닙니다. 안정 배포 전에는 ESP32-S3 마이크에서 false wake와 missed wake 테스트가 필요합니다.

## 검증된 환경

- NVIDIA GeForce RTX 5070 Ti
- Windows 11 + Docker Desktop
- Docker GPU passthrough 확인
- Torch `cuda_available: true` 확인
- TensorFlow `/physical_device:GPU:0` 인식 확인
- GitHub Actions CI 통과

작은 end-to-end GPU smoke run 결과는 [examples/hey-komi-gpu-smoke-training.md](examples/hey-komi-gpu-smoke-training.md)에 정리되어 있습니다.

## 데이터셋

데이터셋 카탈로그는 [datasets/catalog.json](datasets/catalog.json)에 있습니다. 자세한 설명은 [datasets/README.md](datasets/README.md)와 [docs/dataset-guide.md](docs/dataset-guide.md)를 참고하세요.

대표 소스:

- `kahrendt/microwakeword`: background/negative feature archive
- Google Speech Commands v0.02: 단어 음성 클립
- MLCommons Multilingual Spoken Words microset: 다국어 단어 음성 클립
- FSD50K: 환경음 hard negative

카탈로그 확인:

```bash
python scripts/show_datasets.py --recommended first
```

트레이너용 대용량 데이터셋 준비 상태 확인:

```powershell
.\scripts\prepare_training_datasets.ps1
```

## 앞으로 할 계획

- ESP32-S3 테스트 리포트: board, microphone, room, threshold, false wake, missed wake 수집
- Hardware-validated 모델 릴리스: 최소 1개 이상의 실제 마이크 테스트 보고서 확보
- Resumable dataset prep 고도화: 대용량 다운로드/압축해제/변환 자동 재개
- 추가 release demo assets: 실제 하드웨어 테스트 영상 또는 짧은 시연 MP4 추가

전체 로드맵은 [docs/product-roadmap.md](docs/product-roadmap.md)에 있습니다.

## 관련 문서

- [Windows/WSL2/RTX guide](docs/windows-wsl2-rtx.md)
- [Dataset guide](docs/dataset-guide.md)
- [Model quality gates](docs/model-quality-gates.md)
- [Release demo assets](docs/release-demo-assets.md)
- [Release playbook](docs/release-playbook.md)
- [Hey Komi model card](models/hey-komi-candidate/model-card.md)
- [RTX 5070 Ti smoke test](examples/rtx-5070-ti-smoke-test.md)

## 라이선스

MIT. Upstream 프로젝트는 각자의 라이선스를 따릅니다.
