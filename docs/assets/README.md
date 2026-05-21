# Real UI Demo Assets

These assets are captured from the running trainer web UI at `http://localhost:8789`.

Regenerate after starting the trainer:

```powershell
docker compose up -d
npm install --prefix .tools/playwright playwright-core
node scripts/capture_trainer_ui_demo.mjs
python -m pip install --target .tools/video-deps pillow imageio-ffmpeg
$env:PYTHONPATH = ".tools\video-deps"; python scripts/build_ui_demo_media.py
```

The README embeds `trainer-ui-demo.gif` because GitHub reliably renders GIFs inline. The MP4 is linked through the raw GitHub URL so it opens as a video/download instead of the repository file viewer.

Release-result command snippets are tracked in [../release-demo-assets.md](../release-demo-assets.md). Add real hardware demo media there once ESP32-S3 testers provide video or reproducible reports.
