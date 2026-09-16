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
- **Verify before encoding** — confirm the recording *shows what you intended* (crop good, the intended overlay present, no stale or unwanted artifacts) **and is *watchable*** (packet/message labels readable at playback rate, no dead air). See **Verifying the recording** → **Pacing & legibility** below. Don't declare done without it.

## Driving the simulation — traps that silently corrupt a capture

These three cost a session's worth of mislabelled artifacts. All of them fail *quietly*:
nothing errors, and you only notice by cross-checking the content.

- **Two Qtenv instances will bind the same MCP port without complaint.** The second one
  does not fail to start; both listen, and the kernel then spreads your JSON-RPC calls
  between them. A capture you labelled `NoTunnel` is then quite possibly showing
  `RoutingLoop`, and an option you passed on the command line appears to have been
  ignored (because the request went to the older process). **Before every capture, call
  `get_config` and confirm the active configuration is the one you asked for**, and
  after every capture free the port and wait for it to clear.
- **`bin/inet` is a shell wrapper, so `$!` is not the simulation's pid.** The real
  process is an `opp_run_release` child. Killing the pid you captured at launch leaves
  the child holding the port, which sets up the trap above. Kill by *port holder*
  instead: `ss -ltnp | grep <port> | sed 's/.*pid=\([0-9]*\).*/\1/'` — and take care
  not to kill a Qtenv the user started themselves on a different port.
- **`pgrep -f <pattern>` / `pkill -f <pattern>` match your own command line.** If the
  pattern appears in the shell command you are running, you kill your own shell. Use a
  pid file, or derive pids from `ss` output.

**String parameters need embedded quotes on the command line.** `--*.x.y.labelFormat=""`
passes an empty string; `--*.x.y.labelFormat=` is an error, and
`--*.x.y.interfaceFilter=not(tun*)` is parsed as an *expression* and stops Qtenv on a
modal dialog **before it binds the MCP port** — which looks exactly like a slow start.
If the port never appears, read the launch log for a parse error.

**A filter parameter replaces its default rather than adding to it.**
`interfaceTableVisualizer.interfaceFilter` defaults to `not(lo*)`; setting it to
`not(tun*)` brings the loopback labels back. Prefer a positive match (`"eth*"`) when you
want a specific set.

**Qtenv's canvas toolbar floats over the top-right of the canvas** and is *inside* the
`crop_rect` that `start_video_recording` reports, so `crop_area: 'with_padding'` does not
exclude it. No showcase video on master shows it. Drop the top strip in the ffmpeg crop
(≈85 px was right for a 418 px-tall canvas — it also removes the `configurator` /
`visualizer` icons, which sit in the same band). Stills taken with `get_canvas_image` are
unaffected: that renders the canvas directly, like Qtenv's "Export to Image".

## Verifying the recording

Before encoding, verify the recording **shows what you intended** — *not* by pixel-matching overlay
colors. Visualizer overlays have no fixed color to match: a data-link arrow's color is palette-cycled
by index (default `lineColor="dark"`, a color *group*), width-3, anti-aliased, and opacity-faded
during fade-out (`PathCanvasVisualizerBase.cc:142,169`), so exact-RGB scanning is unreliable. Two
methods that compose — **A** is the default, **B** the oracle:

**A. Look at the frames (general, no setup).** The Read tool renders a PNG as an image, so just
*look* — for any overlay (arrows, comm ranges, routing tables, packet-drop markers, labels) and for
crop quality, with no per-visualizer knowledge. Read:
- the **first** frame — crop encloses the whole canvas with padding, nothing clipped; no stale
  overlay from a prior run (the first frame is deterministically before any new overlay fires); and
  no unwanted built-in message animation (see below) if the clip should show only the visualizer
  overlay.
- **1–2 frames at the event's sim time** (pick from the message log / anchors; a data-link arrow
  persists ~1 s sim-time, so any frame in that window catches it) — the intended overlay is present
  and labelled. *Seeing* the arrow is the real check; clean layout / updated labels are only
  *adjacent* indicators that silently pass the wrong-filter / visualizer-off-by-default bugs.

**B. Count the overlay figures (oracle — for certainty or recipe redo).** INET canvas visualizers
draw their overlays as children of a named `cGroupFigure` on the network canvas, so the child count
*is* the live-overlay count — deterministic and immune to color/AA/fade. `count 0` at the event time
pins the failure to "visualizer off / wrong filter". Query via `execute_cpp`:

```cpp
void check_overlays() {
    const char* groups[] = {"paths","packet drops","link breaks","communication",
                            "routing tables","links","trees"};
    auto canvas = getSimulation()->getSystemModule()->getCanvas();
    struct R { static cFigure* find(cFigure* f, const char* n) {
        if (!strcmp(f->getName(), n)) return f;
        for (int i = 0; i < f->getNumFigures(); i++)
            if (auto* r = find(f->getFigure(i), n)) return r;
        return nullptr;
    }};
    for (auto* g : groups) if (auto* f = R::find(canvas->getRootFigure(), g))
        std::cout << g << "=" << f->getNumFigures() << "  ";
    std::cout << std::endl;
}
check_overlays();
```

Group → visualizer: `paths` = all path/arrow visualizers (DataLink, NetworkRoute, PhysicalLink —
they *share* this name, so the count is across them; read a child figure's label text to
disambiguate), `packet drops` = PacketDrop, `link breaks` = LinkBreak, `communication` = Medium
(ranges/signals), `routing tables` = RoutingTable, `links` = link/connection, `trees` = Tree. The
canvas belongs to `visualizationTargetModule` (usually the network — adjust if a submodule).
`execute_cpp` needs `opp_sandbox`; wrap the body in a uniquely-named function (top-level decls
persist), only `std::cout` is captured, and a bad snippet crashes the sim — recover by deterministic
replay (see the packet-dissection capture recipe).

*Disambiguating shared `paths` groups.* When more than one path visualizer is enabled they each get
their own `cGroupFigure("paths")`, all sharing the name (the count above sums across them). Each arrow
is a `LabeledPolylineFigure` (itself a group) whose label is a nested `cTextFigure` named `label`
(`labelFormat` default `"%n"` = packet name). Read that text to tell the groups apart — a plain
`dynamic_cast<cTextFigure*>` reaches it, no INET headers needed:

```cpp
void list_path_overlays() {
    auto canvas = getSimulation()->getSystemModule()->getCanvas();
    struct R {
        static const char* label(cFigure* f) {                 // first cTextFigure under f
            if (auto* t = dynamic_cast<cTextFigure*>(f)) return t->getText();
            for (int i = 0; i < f->getNumFigures(); i++)
                if (auto* s = label(f->getFigure(i))) return s;
            return nullptr;
        }
        static void walk(cFigure* f) {
            if (!strcmp(f->getName(), "paths")) {
                std::cout << "paths(" << f->getNumFigures() << "):";
                for (int i = 0; i < f->getNumFigures(); i++) {
                    auto* s = label(f->getFigure(i));
                    std::cout << " [" << (s ? s : "") << "]";
                }
                std::cout << std::endl;
                return;                                          // don't descend into the arrows
            }
            for (int i = 0; i < f->getNumFigures(); i++) walk(f->getFigure(i));
        }
    };
    R::walk(canvas->getRootFigure());
}
list_path_overlays();
```

One line per `paths` group, listing each arrow's packet label — so the labels identify what each
group visualizes (your DHCP frame names for the data-link arrows vs. an IP packet name for a route
overlay). With a single path visualizer enabled there's only one group and no ambiguity.

**Built-in message animation.** Qtenv's built-in animation (`Qtenv::opt->animationEnabled`, default
**on** — the message dot/line moving along connections) is separate from the INET visualizers. If a
clip should show only the clean visualizer overlay, the built-in animation is redundant clutter: spot
it in the first frame (packet dots traversing wires) and turn it off when unwanted —
`getQtenv()->opt->animationEnabled = false;` via `execute_cpp`, or Preferences → "Animate messages".
Disabling it does **not** remove visualizer arrows; their fade-out drives its own canvas animation.

The **bubble** color check (`RGB(248,248,216)`, above) is the one place pixel-matching is correct —
bubble fill genuinely *is* a fixed color.

### Pacing & legibility (playback, not content)

Methods A/B confirm the overlay is *present*; they don't confirm the clip is *watchable*. Pacing has
two opposite failure modes — check both before declaring done:

- **Too fast → labels unreadable.** A packet/arrow whose name flashes by can't be read. Estimate its
  on-screen *playback* time: `(frames the label is visible) ÷ ffmpeg -r`. A data-link arrow persists
  ~1 s sim-time, so at `playback_speed=1` it spans ~`fps` frames, i.e. `fps ÷ -r` seconds on screen.
  Aim for **≥ ~0.7–1 s of playback per readable label**. If it's less, the fix is *more frames over
  that packet* — lower `playback_speed` (or raise `fps`) so the animation is sampled more densely —
  **not** just a slower `-r`, which stretches everything including the dead parts. Verify by reading
  the actual frames over the event window and counting how many carry the label. (Microsecond LAN
  exchanges are the trap: clamping `min_animation_speed` to "fix" them collapses the holds and the
  packets teleport — see the warning above. Never use it for legibility.)
- **Too slow → dead air.** "Boring" is *dead frames*, not raw length. Scan a handful of evenly-spaced
  frames (or diff consecutive frames); a span of visually-identical frames is the symptom.
  Continuously, visibly-evolving behavior is **not** dead air even when it runs long.

  Dead frames are only a *symptom* — the fix depends on the cause. Diagnose, then fix, in this order:

  1. **Idle lead-in / trail-out** (dead span at the very start or end) → **tighten the `window`**:
     record only the events + ~2 packets after the state change. No speed change. Check this first —
     it's the most common cause and the cheapest fix.
  2. **A real time-gap between two separated events** (active, then a long quiet stretch, then active
     again) → **split into two videos**. This is the *"separate videos for separate events — never put
     a time jump in a single video"* guideline. The trigger is the gap *itself*, not readability:
     compressing real idle time into a blur misrepresents the timeline, so you split even if speeding
     up wouldn't hurt labels.
  3. **Uniformly under-driven** (the whole clip, active parts included, crawls) → **raise
     `playback_speed`** globally.
  4. **Speed-up blocked by the too-fast check** — `playback_speed` is a *single global knob*. If one
     region is dense (labels must stay readable → wants slow) and another is sparse (dead air → wants
     fast), no single value satisfies both: speeding up the dead part blurs the dense part. Resolution
     is **two videos**, each speed-tuned to its own content. (A post-production per-segment re-time is
     possible but decimates bubbles — see above — so a native re-record per segment is cleaner.)

## Playback Rate Selection

| Frame count | At 10fps | At 15fps | At 5fps |
|-------------|----------|----------|---------|
| 100 | 10s | 6.7s | 20s |
| 200 | 20s | 13s | 40s |
| 350 | 35s | 23s | 70s |
| 500 | 50s | 33s | 100s |

Target: **10–30s** per video for showcase documentation — a guideline, **not a hard cap**. Some
behavior genuinely can't be shown in 30s (a slow-converging protocol, a multi-phase exchange,
a long-period failover); a ~1 min clip is fine **when the extra length is all informative** — i.e.
it passes the *dead-air* check (every span shows visible change), not merely the clock. Shorten only
by removing dead frames or tightening the `window`, **never** by speeding up past label-readability
(the *too-fast* check above). When length is warranted, keep it long.

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
5. **Verify** the recording shows what you intended (see *Verifying the recording* — frames for the
   intended overlay + crop, figure-count oracle for certainty), then clean up frames.

The anchors are the point: they let the AI decide *for itself* whether the recipe is
still valid or needs updating, instead of blindly replaying a stale procedure.

## Visualizer fade-outs are animations, not just opacity

`PacketDropCanvasVisualizer::setAlpha()` derives both the icon's opacity **and its
position** from the same alpha: `px = 4*dx*(1-alpha)`, `py = a*px^2 + b*px`, so the
marker flies out of the node along a parabola while it fades. **The fade IS the
animation; there is no separate motion clock.** Other fading visualizers work the same
way. Two consequences, and getting either wrong costs a whole recording cycle:

- A marker at alpha ≈ 1 for the whole clip does not move at all. It reads as a frozen
  decoration, and the reviewer will call it frozen.
- A fade that completes in a handful of rendered frames makes the icon teleport, so
  nothing appears in the file at all.

So the fade has to span **many rendered frames**. The knob for that is
`fadeOutAnimationSpeed`: while a marker is on screen the visualizer pins the canvas
animation speed to it (Qtenv takes the minimum over all requesters), and during
recording `sim_time_per_frame = (1/fps) * animation_speed * playback_speed`. The arc
therefore lasts `30 * fadeOutTime / (fadeOutAnimationSpeed * playback_speed)` frames — a
number you choose. It must be **lower** than the model's own animation speed, or the
minimum picks the model's instead and nothing changes.

`fadeOutMode` choice, for a window of simulated time recorded as seconds of video:
`realTime` fades in wall-clock seconds and loses to slow frame-grabbing every time;
`animationTime` survives that, but an express warm-up advances animation time by only a
few seconds however much simulated time it covers, so markers from an earlier burst are
still fresh at recording start and sit on screen from frame one; `simulationTime` works
if the value is smaller than the gap to the previous burst and comparable to the
recorded window.

## Stop the recording on an event limit, not a time limit

Qtenv's run loop (`src/qtenv/qtenv.cc`, the `runUntil.time` branch) breaks out at the
last event *before* the limit and never animates the remaining time — the source even
says `// TODO: animate until the target simtime`. If the last event of the burst is well
before the limit, the run stops there and whatever is on screen freezes for the rest of
the clip. The **event-limit** branch a few lines below calls `animateUntilNextEvent()`
before breaking, so frames keep being rendered and a fade can finish. Use
`record_video` with `event_limit` whenever anything on screen has to finish animating.

## Frame counts are not reproducible across builds

The number of frames a window yields depends on the animation speed the message animator
asks for, which changes with the model and has changed under an unmodified recipe here
(a RoutingLoop capture that shipped 422 frames now yields 5205). Never carry a frame
count forward from an earlier recording: read it off the run and let the input framerate
absorb it.
