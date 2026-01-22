# Boot Video Asset

## Video File Location

Place your boot/intro video file here with the name:

```
boot_video.mp4
```

**Full path**: `e:\Prog\AirsoftProject\bomb_app\assets\boot_video.mp4`

## Video Specifications

- **Format**: MP4 (H.264 codec recommended)
- **Resolution**: Any resolution (will be scaled to fit 240x320 portrait display)
- **Recommended Resolution**: 240x320 (portrait) for best quality
- **Frame Rate**: 30 FPS recommended
- **Duration**: Keep under 10 seconds for best user experience
- **Orientation**: Portrait (vertical) recommended

## Features

- Video plays automatically on application startup
- Press **#** to skip the video at any time
- Video plays once and freezes on the last frame
- Automatically transitions to CONFIG screen after video ends

## If Video is Missing

If the video file is not found, the application will:
- Print a warning message to the console
- Skip directly to the CONFIG screen
- Continue working normally without the boot video

## Example Command to Test

After placing your video file, run:
```bash
python main.py
```

The video should play immediately on startup.
