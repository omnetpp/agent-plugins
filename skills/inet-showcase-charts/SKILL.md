---
name: inet-showcase-charts
description: Author and render OMNeT++ Analysis (.anf) result charts for INET showcases — hand-write or edit the .anf and its Python chart script, render to PNG headlessly with opp_charttool, choose native vs matplotlib, start from chart templates, use the inet.scave.plot helpers, and add a FIGURE RECIPE comment. Use when asked to create, add, edit, or regenerate a result chart/graph/plot (line, bar, histogram, scatter) for an INET showcase from .sca/.vec results, to work with a .anf analysis file, or to produce a chart image for showcase documentation. NOT for sequence charts from .elog files — use the omnetpp-ide-mcp skill for those.
---

# INET showcase charts

Hand-author and render the result charts that appear in INET showcase documentation: the `.anf`
analysis file, its embedded Python chart script, and the committed PNG.

## Mental model

An `.anf` is XML: a set of `<input>` result-file patterns plus one or more `<chart>`s. **Each chart
is self-contained** — an embedded Python `<script>` plus `<property>` key-values. The script is
written against the `omnetpp.scave` API (`results`, `chart`, `utils`, `ideplot`, `vectorops`), never
against files directly. That one API is what lets the *same* chart render two ways:

- **In the IDE** — backed by the live ResultFileManager and (for native charts) a native SWT widget.
- **Headless** — `opp_charttool` swaps in file-reading implementations and renders with Matplotlib.

So a correctly written chart looks the same in the IDE and on the command line. The committed
showcase PNG is produced **headlessly with `opp_charttool`** (the doc build just consumes the PNG).

## Workflow

```
1. Confirm inputs exist   the sim already records the needed results/*.sca / *.vec
2. Author / edit  Foo.anf  in the showcase dir (XML + chart script)   → see references/anf-format.md
3. Render the PNG  opp_charttool imageexport Foo.anf -n "<chart>" -f png --dpi 150 -d <media-dir>
4. Verify          open the PNG; for a NATIVE chart this is the Matplotlib-emulated render —
                   confirm it looks right (it is what gets committed)
5. (optional)      preview in the IDE for parity / native interactivity (omnetpp-ide-mcp skill)
6. Commit          the .anf + the exported PNG (PNG → media repo)
7. Recipe          add a FIGURE RECIPE comment next to the .. figure:: in the .rst (below)
```

## Choose the chart backend

Set the chart's `type` attribute, which decides the backend.

- **Native** (`type="LINE" | "BAR" | "HISTOGRAM"`, plots via `ideplot`) — use when **the reader may
  want to explore the chart** in the IDE: zoom, pan, toggle individual curves. Native charts get an
  interactive widget in the IDE *and* export headlessly (emulated by Matplotlib). **When you pick
  native, you must check the headless Matplotlib export** — that emulated render is the committed
  PNG, and it can differ subtly from the on-screen native widget.
- **Matplotlib** (`type="MATPLOTLIB"`, uses `matplotlib.pyplot` directly) — use when the chart is
  **mainly for display** in the showcase, or when it needs **complex/custom work** native can't
  express (twin axes, annotations, insets, custom layouts). No native interactivity; identical in
  IDE and headless. This is the simplest to hand-author — prefer it unless interactivity is wanted.

`inet.scave.plot` (INET helpers): **default to the stock `omnetpp.scave` tools** — custom Matplotlib
can do anything, and this module may later migrate into the OMNeT++ tools, so don't build hard
dependencies on it. Reach for it only when one of its helpers (row ordering, per-row styling,
multi-dimensional legends, faded color cycles) genuinely removes real boilerplate. Its full how-to
is in **references/inet-scave-plot.md** — read it before using or recommending it.

## The chart-script contract

Every chart script follows this shape (full API in **references/chart-script-api.md**):

```python
from omnetpp.scave import results, chart, utils      # + ideplot (native) OR matplotlib.pyplot as plt
props = chart.get_properties()                        # 1. the chart's <property> values
utils.preconfigure_plot(props)                        # 2. styling/rc — before plotting
df = results.get_scalars(props["filter"], ...)        # 3. query .sca/.vec → pandas DataFrame
if df.empty:
    raise chart.ChartScriptError("The result filter returned no data.")  # 4. guard
# ... transform (utils.perform_vector_ops, pivots) and plot ...
utils.export_image_if_needed(props)                   # 5. MANDATORY — or imageexport produces nothing
utils.export_data_if_needed(df, props)                # if you have a df
```

`utils.export_image_if_needed(props)` is the export hook and **must be the last plotting call** — it
is a no-op interactively and writes the file when `opp_charttool imageexport` (or the IDE export
dialog) sets `export_image=true`. Omitting it is the #1 reason an export silently produces no PNG.

To start from a built-in chart, copy a template's script as your base — see the template catalog and
both worked idioms (native `linechart.py`, matplotlib `generic_mpl.py`) in
**references/anf-format.md**.

## Render headlessly with opp_charttool

`opp_charttool` is a plain Python script; it needs the OMNeT++ Python package on `PYTHONPATH`, so
**source setenv first**:

```bash
. /home/user/omnetpp-dev/setenv          # puts .../python on PYTHONPATH
opp_charttool info Foo.anf               # list charts with their indices + types
opp_charttool imageexport Foo.anf -n "Per-station throughput" -f png --dpi 150 -d media/
opp_charttool imageexport Foo.anf -i 0 -f png --dpi 150 -d media/   # or select by index
```

- Default format is **svg** and default dpi is **300** — pass `-f png --dpi 150` explicitly.
- Select the chart with `-n <name-substring>` or `-i <index>` (not both). `info` shows indices.
- **Output filename** comes from the chart's `image_export_filename` property; if unset it falls back
  to a sanitized chart name. `-o <name>` overrides. The format adds the extension. So set
  `<property name="image_export_filename" value="per-station-throughput"/>` to control the PNG name.
- `--width` / `--height` are in **inches**; `--dpi` only scales raster resolution (aspect preserved).
- Export always goes through Matplotlib, **including native charts** — which is why native charts
  must be eyeballed after export.

## FIGURE RECIPE comment for charts

Every chart `.. figure::` in a showcase gets a FIGURE RECIPE comment immediately after, so it can be
regenerated. RST comment — `..` on its own line, body never parsed as RST. The anchor/self-check
philosophy is shared with the `video-recording` and `omnetpp-mcp-sim` skills.

```
.. figure:: media/per-station-throughput.png
..
   FIGURE RECIPE (redo via the "inet-showcase-charts" skill)
   type:     chart (native LINE)        # or: chart (matplotlib)
   anf:      PerStationThroughput.anf   chart "Per-station throughput" (id 1832)
   inputs:   results/*.sca, results/*.vec   from config General (already recorded)
   shows:    per-station application throughput vs offered load, one line per station
   anchor:   data is structural — the result filter + itervars. If the filter returns
             a different series set, the scenario/recording changed → re-derive.
   backend:  native → headless export is Matplotlib-emulated; verify it matches the IDE widget
   export:   opp_charttool imageexport PerStationThroughput.anf -n "Per-station throughput"
             -f png --dpi 150 -d media/   ; was 1650×825
   stamp:    captured 2026-06, INET 4.6
```

## Best practices

- **Drive appearance through `<property>` values** the script reads (`props[...]`), not hardcoded
  constants, where practical — it keeps the chart editable in the IDE dialog and matches templates.
- **Always guard empty data**: `if df.empty: raise chart.ChartScriptError(...)`. A bare empty
  DataFrame produces a confusing blank PNG.
- **Input patterns are relative to the `.anf`'s directory** (`results/*.sca`). Keep them as patterns,
  not specific run files, so the chart survives re-runs.
- **Set `image_export_filename`** so the committed PNG has a stable, meaningful name across re-exports.
- **Native ⇒ verify the export.** The on-screen native widget and the Matplotlib-emulated export are
  not pixel-identical; the export is what ships.
- **Reproducibility:** the `.anf` + the recording config must be enough to regenerate the PNG with no
  manual steps. The FIGURE RECIPE records the exact `opp_charttool` command.
- For hand-authored matplotlib charts, omit `<dialogPage>` elements — they're only the IDE config UI
  and the IDE falls back to the template's. Keep the `.anf` minimal.

## References

Read these as needed — they are the detailed contracts, kept out of this file to stay lean:

- **references/chart-script-api.md** — the `omnetpp.scave` API cheatsheet: `results` getters + filter
  grammar, `chart`, the `utils` plotting/pivot/export helpers, `ideplot`, and the `vectorops` list.
- **references/anf-format.md** — the `.anf` XML format, a minimal working skeleton, native vs
  matplotlib chart anatomy, the built-in template catalog, and both worked template scripts.
- **references/inet-scave-plot.md** — the `inet.scave.plot` helper reference (what each provides and
  when it beats the stock equivalent), plus the INET "enhanced histogram" custom template.
- **assets/starter.anf** — a minimal, ready-to-edit single-chart matplotlib `.anf` to copy as a base.
