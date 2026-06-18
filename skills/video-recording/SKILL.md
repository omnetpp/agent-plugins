---
name: video-recording
description: Record videos of OMNeT++/INET simulations for showcase documentation using the MCP server's video recording tools. Use when asked to create a video, animation, or recording of a running simulation, or when a showcase needs visual evidence of time-dependent behavior (protocol state changes, tree building, failover, traffic flow).
---

# Video Recording for Simulation Showcases

Record simulation videos via the MCP server's `record_video` / `start_video_recording` + `stop_video_recording` tools, then encode with ffmpeg. Optionally adjust capture pacing with `set_animation_parameters` (see below).

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
| `playback_speed` | The pacing/length knob (set via `set_animation_parameters` before recording). Higher = shorter video, packets stay visible; lower = slow-motion. Default 1. See below. |
| ffmpeg `-r` | Playback rate. 10fps is a good starting point. Adjust based on video duration vs content density. |

## Capture Speed (`set_animation_parameters`)

During recording, one frame is captured every `(1/fps) × animation_speed × playback_speed` of
simulated time (`animation_speed` is the model-driven speed — from NED display strings / message
animations). If a model defines *no* animation speed, recording falls back to one frame per event
and `playback_speed` has no effect — but most INET showcases animate, so it applies. Three levers:

- **`fps`** (capture) — higher = more frames per unit of animated sim time (smoother, more frames).
- **`playback_speed`** (capture, via `set_animation_parameters`) — **the knob for pacing/length.**
  Lower = more frames (slow-motion, finer detail); higher = fewer frames (shorter video). Packets
  stay fully visible across the useful range (tested on BasicDHCP: pb=1 → 69s, pb=2 → 41s, pb=4 →
  25s, packets present in every frame). Clipped to 0.01–100 in normal mode.
- **ffmpeg `-r`** (encode) — real-time playback rate of the final video.

**To shorten a recording, raise `playback_speed`** (or lower `fps` / raise ffmpeg `-r`). Set it once
before `record_video` against the `normal` profile; verify via the `animation` object in
`get_simulation_state`. It persists across runs (same toolbar slider / "Animation Parameters" dialog).

⚠️ **Do NOT use the `min_animation_speed` clamp to shorten.** It bounds the model's animation speed,
but for events with tiny sim-time (fast LAN exchanges — a 100 Mbps DHCP DORA spans *microseconds*)
clamping even slightly above the model's natural speed collapses the message-animation holds and the
packets stop animating — they teleport. Tested: `min_animation_speed=0.16` on BasicDHCP → packets
vanished, while `playback_speed=4` kept them. The min/max clamps only bound a model that animates
pathologically fast/slow; they are not a length knob.

### Bubbles are wall-clock-timed — no speed setting affects them

`cComponent::bubble()` notifications (e.g. "Got IP …") use a hardcoded **1-second real-wall-clock
timer** in Qtenv (`BubbleItem::startTimer(1000)`), decoupled from sim/animation/playback speed.
During recording they render to only **~10–11 frames** (~0.37 s at 30 fps) regardless of any setting,
and the **last** event's bubble is clipped to ~3 frames (after the final event the sim races to the
time limit, so the wall-clock bubble catches almost nothing). Consequences:

- No `set_animation_parameters` value can lengthen a bubble.
- **ffmpeg re-timing decimates bubbles further** — `setpts`/`fps` speed-ups drop frames uniformly,
  crushing an already-brief bubble below readability. If you must shorten, record natively at a
  higher `playback_speed` (the wall-clock bubble keeps its ~10 frames) rather than re-timing a
  natural-speed video.
- To make a bubble readable (~1 s) in a *shortened* video, **freeze/hold its frames in post** —
  rebuild the frame sequence: fast-forward the action, repeat the bubble's representative frame ~33×
  at 30 fps. That's the only way to get readable bubbles *and* a short video; it's a Qtenv
  limitation, not optional polish. Detect bubble frames by their fill color `RGB(248,248,216)`.

## Guidelines

- **Keep videos short** — record only the interesting events + 2 packets (or equivalent) after the state change to confirm the new behavior.
- **Separate videos for separate events** — never put a time jump in a single video. If interesting events are far apart in sim time, make separate videos.
- **Frame numbering** — if using `start/stop_video_recording` across multiple segments with the same output_dir, frame numbers continue. Use `-start_number N` in ffmpeg.
- **Stale frames may linger** — if a prior recording was killed mid-way and its `output_dir` is the same as the current one, the new recording overwrites frames 0..N but anything numbered past N from the prior run is still on disk. ffmpeg's `%04d` glob will silently encode the stragglers too. Check what's already in the dir before recording (or use a fresh per-recording subdir).
- **Preserve iterations** — move superseded videos to `media/unused/` rather than deleting, in case you need to go back.
- **Verify the frames** — read sample frames before encoding, and check two distinct things:
  - **No stale overlays from a prior run** — read the *first* frame; nothing should be left over from earlier capture activity. The first frame is the right anchor for this check because it's deterministically before any new overlay has fired.
  - **The overlays you *added* are actually present** — when the recording exists *because* of a specific visualizer (a `DataLinkVisualizer` arrow, a `RoutingTableVisualizer` overlay, a packet-drop marker), the overlay won't be in the first frame — it appears only at the moment the underlying event fires. Sample frames at that event time: use the message log / FES / known protocol timing to pick frames where the packet is in flight (data-link arrows usually persist for 1 s of sim time after the send, so any frame within that window should show them). Layout being correct, labels updating, and the playground being clean are *adjacent* indicators, not the feature itself. "Looks right" ≠ "is right" — an explicit check catches the wrong-selector / visualizer-off-by-default bugs that adjacent indicators silently pass. Don't declare done without it.

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
