---
name: inet-showcase-charts
description: Author and render OMNeT++ Analysis (.anf) result charts for INET showcases — create or edit charts by copying a template-derived sibling, write/adjust the Python chart script, render to PNG headlessly with opp_charttool, choose native vs matplotlib, use the inet.scave.plot helpers, and add a FIGURE RECIPE comment. Use when asked to create, add, edit, or regenerate a result chart/graph/plot (line, bar, histogram, scatter) for an INET showcase from .sca/.vec results, to work with a .anf analysis file, or to produce a chart image for showcase documentation. NOT for sequence charts from .elog files — use the omnetpp-ide-mcp skill for those.
---

# INET showcase charts

Hand-author and render the result charts in INET showcase documentation: the `.anf` analysis file,
its embedded Python chart script, and the committed PNG.

## Mental model

An `.anf` is XML: `<input>` result-file patterns plus one or more `<chart>`s. **Each chart is
self-contained** — an embedded Python `<script>` plus `<property>` values plus the IDE config form
(`<dialogPage>` blocks). The script targets the `omnetpp.scave` API (`results`, `chart`, `utils`,
`ideplot`, `vectorops`), never files directly. That one API lets the *same* chart render two ways:

- **In the IDE** — live ResultFileManager and (native charts) an interactive SWT widget.
- **Headless** — `opp_charttool` swaps in file-reading impls and renders with Matplotlib.

The committed showcase PNG is produced **headlessly with `opp_charttool`** (the doc build just
consumes the PNG, committed under the showcase's `doc/media/`).

## Author by copying a sibling — don't build from blank

INET showcase charts carry the full template machinery (`<dialogPage>` config forms, the house
`<property>` set, rc-params). **The reliable way to match house style is to copy the nearest existing
showcase chart of the same template, then edit it** — that inherits the dialogPages, property names,
rc-params, and defaults for free, so you only touch the data query, the script body, the chart
`name`, and the `image_export_filename`.

```
1. Pick the chart type/template you need (see the decision below)
2. Find the closest existing chart:  grep -rl 'template="<id>"' showcases/*/*/*.anf
   copy that whole <chart>…</chart> (with its <script>, <property> tags, AND <dialogPage> blocks)
3. Edit: the result filter / query, custom script logic, the name=, and image_export_filename
4. Render:  . /home/user/omnetpp-dev/setenv
            opp_charttool imageexport Foo.anf -n "<chart name>" -d <showcase>/doc/media/
5. Verify:  open the PNG; for a NATIVE chart this is the Matplotlib-emulated render — confirm it
            looks right (it is what gets committed)
6. (optional) preview in the IDE for parity / native interactivity (omnetpp-ide-mcp skill)
7. Commit:  the .anf + the exported PNG (PNG → doc/media/)
8. Recipe:  add a FIGURE RECIPE comment next to the .. figure:: in the .rst (below)
```

A from-scratch `.anf` skeleton and the full `.anf` element reference are in
**references/anf-format.md** — but for production charts, prefer copying a sibling.

## Choose the chart backend

In existing showcases native and matplotlib are used about equally (~50/50) — there is **no default
to fall back on**; choose by purpose. Set the chart's `type` attribute accordingly.

- **Native** (`type="LINE" | "BAR" | "HISTOGRAM"`, plots via `ideplot`/`utils.plot_*`) — when **the
  reader may want to explore the chart** in the IDE: zoom, pan, toggle individual curves. Interactive
  widget in the IDE *and* headless export. **You must then check the headless Matplotlib export** —
  that emulated render is the committed PNG and can differ subtly from the on-screen native widget.
- **Matplotlib** (`type="MATPLOTLIB"`, uses `matplotlib.pyplot`) — when the chart is **for display
  only**, or needs **complex/custom work** native can't express (twin axes, annotations, insets,
  custom layouts). No native interactivity; identical in IDE and headless.

`inet.scave.plot` (INET helpers): **default to the stock `omnetpp.scave` tools** — custom Matplotlib
can do anything, and this module may later fold into the OMNeT++ tools, so don't build hard
dependencies on it. In practice the only widely-used helpers are **`default_colors`** (the house
palette) and **`add_to_dataframe`** (per-row color/marker styling); `create_custom_legend` shows up
for richer legends. Full how-to (and when each beats the stock equivalent) is in
**references/inet-scave-plot.md** — read it before using or recommending it.

## The chart-script contract

Every chart script follows this shape (full API in **references/chart-script-api.md**):

```python
from omnetpp.scave import results, chart, utils      # + ideplot (native) OR matplotlib.pyplot as plt
props = chart.get_properties()                        # 1. the chart's <property> values
utils.preconfigure_plot(props)                        # 2. styling/rc — before plotting
df = results.get_vectors(props["filter"], ...)        # 3. query .sca/.vec → pandas DataFrame
if df.empty:
    raise chart.ChartScriptError("The result filter returned no data.")  # 4. guard (≈universal)
# ... transform (utils.perform_vector_ops, pivots) and plot ...
utils.postconfigure_plot(props)
utils.export_image_if_needed(props)                   # 5. MANDATORY — or imageexport produces nothing
utils.export_data_if_needed(df, props)                # if you have a df
```

`utils.export_image_if_needed(props)` is the export hook and **must be the last plotting call** — a
no-op interactively, writes the file when `opp_charttool imageexport` sets `export_image=true`.
Omitting it is the #1 reason an export silently produces no PNG. All showcase charts end this way.

## Render headlessly with opp_charttool

`opp_charttool` is a plain Python script needing the OMNeT++ Python package on `PYTHONPATH`, so
**source setenv first**:

```bash
. /home/user/omnetpp-dev/setenv          # puts .../python on PYTHONPATH
opp_charttool info Foo.anf               # list charts with indices + types
opp_charttool imageexport Foo.anf -n "Per-station throughput" -d <showcase>/doc/media/
opp_charttool imageexport Foo.anf -i 0 -d <showcase>/doc/media/      # or select by index
```

- Select the chart with `-n <name-substring>` or `-i <index>` (not both). `info` shows indices.
- **Size is controlled in inches by the chart's `image_export_width`/`height` properties**, not by
  cranking dpi. House sizes: **12×8** (wide), **9×6**, or **6×4** (compact). Existing committed PNGs
  are ~80–96 dpi (≈963×578 for a wide chart) — the chart's properties carry these; copying a sibling
  inherits them. Match the dpi/size of the other figures in the same showcase.
- **Output filename** = the chart's `image_export_filename` property, else a sanitized chart name.
  `-o <name>` overrides; the format adds the extension. Set the property only when the chart name is
  ambiguous or shared (most showcase charts rely on the name fallback).
- `-f` format defaults to **svg** — pass `-f png` for the raster figure (most showcase media is PNG).
- Export always goes through Matplotlib, **including native charts** — hence the native eyeball check.

## FIGURE RECIPE comment for charts

Every chart `.. figure::` in a showcase gets a FIGURE RECIPE comment after it. RST comment — `..` on
its own line, body never parsed as RST. Anchor/self-check philosophy shared with the
`video-recording` and `omnetpp-mcp-sim` skills.

```
.. figure:: media/per-station-throughput.png
..
   FIGURE RECIPE (redo via the "inet-showcase-charts" skill)
   type:     chart (native LINE)        # or: chart (matplotlib)
   anf:      PerStationThroughput.anf   chart "Per-station throughput"
   inputs:   results/General-*.sca, results/General-*.vec   (already recorded by config General)
   shows:    per-station application throughput vs offered load, one line per station
   anchor:   data is structural — the result filter + itervars. If the filter returns a
             different series set, the scenario/recording changed → re-derive.
   backend:  native → headless export is Matplotlib-emulated; verify it matches the IDE widget
   export:   opp_charttool imageexport PerStationThroughput.anf -n "Per-station throughput"
             -f png -d doc/media/   ; size from image_export_width/height (was 963×578)
   stamp:    captured 2026-06, INET 4.6
```

## Best practices (from the surveyed showcases)

- **Copy a sibling of the same template** as the base — it brings the dialogPages, house property
  names, rc-params, and defaults; you then only edit the query, script, name, and export filename.
- **Keep the full `<dialogPage>` blocks** — showcase charts carry them (the IDE writes them), so the
  chart stays first-class/editable in the IDE. Don't strip them to "minimize" the `.anf`.
- **House rc-params**: `savefig.transparent: True` (and often `bbox: tight`) for clean doc embedding —
  near-universal; inherited when you copy a sibling.
- **Size via `image_export_width`/`height` in inches** (12×8 / 9×6 / 6×4); leave dpi to match the
  showcase's other figures. Don't reach for high dpi unless the showcase already does.
- **Axis labels carry the unit in brackets**: `Throughput [Mbps]`, `Delay [ms]`, `Loss [%]`.
- **Always guard empty data**: `if df.empty: raise chart.ChartScriptError(...)`.
- **Input patterns are relative to the `.anf` dir** — `results/General-*.sca` + `…-*.vec`, or
  config-specific `results/<Config>-#0.sca`. Keep them as patterns so the chart survives re-runs.
- **`image_export_filename`** only when the chart name is ambiguous/duplicated; else the name fallback
  is house-standard.
- **Native ⇒ verify the export.** The on-screen native widget and the Matplotlib-emulated export are
  not pixel-identical; the export is what ships.
- **Reproducibility:** the `.anf` + the recording config must regenerate the PNG with no manual steps;
  the FIGURE RECIPE records the exact `opp_charttool` command.

## References

Read as needed — detailed contracts kept out of this file to stay lean:

- **references/chart-script-api.md** — the `omnetpp.scave` API cheatsheet: `results` getters + filter
  grammar, `chart`, the `utils` plotting/pivot/export helpers, `ideplot`, and `vectorops`.
- **references/anf-format.md** — the `.anf` XML format, the element/attribute reference, a minimal
  from-scratch skeleton (for understanding the structure), the template catalog, and both worked
  template scripts (native + matplotlib).
- **references/inet-scave-plot.md** — the `inet.scave.plot` helper reference (what each provides, when
  it beats the stock equivalent — `default_colors` and `add_to_dataframe` are the common ones), plus
  the INET "enhanced histogram" custom template.
