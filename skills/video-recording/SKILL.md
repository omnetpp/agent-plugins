---
name: video-recording
description: Record videos of OMNeT++/INET simulations for showcase documentation using the MCP server's video recording tools. Use when asked to create a video, animation, or recording of a running simulation, or when a showcase needs visual evidence of time-dependent behavior (protocol state changes, tree building, failover, traffic flow).
---

# Video Recording for Simulation Showcases

Record simulation videos via the MCP server's `record_video` / `start_video_recording` + `stop_video_recording` tools, then encode with ffmpeg.

## Workflow

1. **Express-run** to just before the interesting segment
2. **Step once** — `run_simulation(event_limit=1, mode='normal')` to flush accumulated UI events
3. **Wait for visualizer fade-out** — `time.sleep(2)` if channel visualizer uses `fadeOutMode = "realTime"` (the default; `fadeOutTime` is typically 1s). Skip if `fadeOutMode = "simTime"`.
4. **Record** — use `record_video` with `crop_area: 'with_padding'`:
   ```
   record_video(time_limit='<end_time>', fps=2, crop_area='with_padding',
                output_dir='<media>/frames_<name>', filename_prefix='<name>_',
                output_file='raw.mp4')
   ```
5. **Encode** with ffmpeg at desired playback rate (start with 10fps, adjust if too fast/slow):
   ```
   ffmpeg -r 10 -f image2 -i "frames/<prefix>_%04d.png" \
     -filter:v "crop=W:H:X:Y,pad=ceil(iw/2)*2:ceil(ih/2)*2" \
     -vcodec libx264 -pix_fmt yuv420p output.mp4 -y
   ```
   Crop values (`W:H:X:Y`) come from the `crop_rect` in `start_video_recording` response.
6. **Clean up** frame directories after encoding.

## Parameters

| Parameter | Notes |
|-----------|-------|
| `crop_area` | Always use `'with_padding'` (network canvas + border + 10px) |
| `fps` | Capture density parameter. Default 2. Actual frame count depends on animation steps in normal mode. |
| ffmpeg `-r` | Playback rate. 10fps is a good starting point. Adjust based on video duration vs content density. |

## Guidelines

- **Keep videos short** — record only the interesting events + 2 packets (or equivalent) after the state change to confirm the new behavior.
- **Separate videos for separate events** — never put a time jump in a single video. If interesting events are far apart in sim time, make separate videos.
- **Frame numbering** — if using `start/stop_video_recording` across multiple segments with the same output_dir, frame numbers continue. Use `-start_number N` in ffmpeg.
- **Preserve iterations** — move superseded videos to `media/unused/` rather than deleting, in case you need to go back.
- **Verify first frame** — read the first frame PNG to confirm no stale visualizer overlays before encoding.

## Playback Rate Selection

| Frame count | At 10fps | At 15fps | At 5fps |
|-------------|----------|----------|---------|
| 100 | 10s | 6.7s | 20s |
| 200 | 20s | 13s | 40s |
| 350 | 35s | 23s | 70s |
| 500 | 50s | 33s | 100s |

Target: 10–30s per video for showcase documentation.
