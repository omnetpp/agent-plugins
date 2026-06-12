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

## Recipes — making a video reproducible

Every `.. video::` in a showcase should be immediately followed by a **recipe**: an
RST comment recording exactly how the clip was captured, so it can be regenerated
after a visualization or config change. The recipe is written for an AI to *replay*
via the MCP tools — no separate script is required (though one could consume the
same fields).

**Why redo is usually cheap:** the simulation is deterministic for a given
config+seed, and visualization settings (which visualizers, packet filters, colors,
the interface-table format) do **not** consume RNG. A visualization-only change is
therefore a pure replay — same trajectory, same event times, new overlay. Only a
change that consumes RNG differently (seed, module/host count, traffic or timing
params, scenario XML) shifts the timeline and forces re-tuning.

### Format

Place directly after the directive. A `..` on its own line makes the block a
comment; its content is never parsed as RST, so colons and directive-like text are
safe.

```
.. video:: media/basicdhcp.mp4
   :align: center

..
   VIDEO RECIPE (redo via the "video-recording" skill)
   config:   <[Config] name in ../omnetpp.ini>
   seed:     <"default", or the explicit seed-set/num-rngs the config sets>
   shows:    <one or two lines: what the clip must depict>
   anchors:  <the determinism self-check — see below>
   window:   <record sim-time start → end; express-run target; fade wait y/n>
   anim:     playback_speed=<n>        # set_animation_parameters, normal profile
   capture:  fps=<n>, crop_area=with_padding   # re-read crop_rect; canvas was <W×H>
   encode:   ffmpeg -r <n> -vcodec libx264 -pix_fmt yuv420p (pad to even dims)
   post:     <bubble-freeze steps, or "none">
   stamp:    recorded <YYYY-MM>, INET <ver>
```

Field notes:
- **anchors** — the structural facts the clip depends on, each stated as a
  *mechanism* (which must hold) plus the *last observed* sim time (which is
  seed-dependent). E.g. "all 3 clients BOUND within the first ~2–3s
  (startTime=uniform(0,2)); last observed bind ~t=2.1s." These double as the redo
  oracle, so phrase them as something you can re-check by reading the message log.
- **window** — express-run lands just before the segment; record `time_limit` is
  the segment end. Note whether a channel visualizer with `fadeOutMode=realTime` is
  present (→ wait ~2s after the step-flush) or not (→ skip).
- **seed** — record "default" unless the config sets `seed-set`/`num-rngs`
  explicitly; an explicit seed is RNG-affecting, so a change to it invalidates the
  anchors just like a traffic-param change.
- **capture** — never hardcode the crop rectangle; store only the last-known canvas
  size as a hint and re-read `crop_rect` from the `start_video_recording` response
  at capture time. If it differs, a layout-affecting visualization change happened —
  update the ffmpeg crop and the recorded size.
- **anim / encode** — `playback_speed` is the pacing knob and persists across runs,
  so re-assert it and verify via `get_simulation_state` → `animation`; ffmpeg `-r`
  is the playback rate.

### Redoing from a recipe (the AI workflow)

1. **Classify the change.** Diff the current `[Config]` against what the recipe
   assumes. Only visualization keys changed → expect a pure replay. Any
   RNG-affecting key changed → expect re-tuning.
2. **Replay setup → verify anchors.** Open the config, express-run to the window
   start, read the actual event times (message log / FES), and compare against the
   recipe's anchors:
   - **Anchors hold** → replay with the stored `anim`/`capture`/`encode` values.
   - **Anchors moved** → the timeline shifted. Re-derive the window/times, re-record,
     and **rewrite the recipe's anchors + window** (and canvas size if it changed),
     noting it in `stamp`.
3. **Capture** per the stored procedure, re-reading `crop_rect`.
4. **Encode** with the stored ffmpeg line (refresh crop `W:H:X:Y` from the fresh
   `crop_rect`).
5. **Verify** the first frame has no stale overlay, then clean up frames.

The anchors are the point: they let the AI decide *for itself* whether the recipe is
still valid or needs updating, instead of blindly replaying a stale procedure.
