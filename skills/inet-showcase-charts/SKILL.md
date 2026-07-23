---
name: inet-showcase-charts
description: Author and render OMNeT++ Analysis (.anf) result charts for INET showcases — create charts data-first (pick the results, plot native or matplotlib from the matching template, configure presentation in the dialog), edit the Python chart script only when needed, render to PNG headlessly with opp_charttool, use the inet.scave.plot helpers, and add a FIGURE RECIPE comment. Use when asked to create, add, edit, or regenerate a result chart/graph/plot (line, bar, histogram, scatter) for an INET showcase from .sca/.vec results, to work with a .anf analysis file, or to produce a chart image for showcase documentation. NOT for sequence charts from .elog files — use the omnetpp-ide-mcp skill for those.
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

## How a chart is made — data first

A chart is data-first: you start from the *data* you want to plot, not from a template id. This
mirrors the IDE workflow, with a headless equivalent for each step.

1. **Pick the data.** Decide which results to plot. In the IDE you select them in the **Browse Data**
   page; what identifies them is a `filter` expression, e.g.
   `name =~ "throughput:last" AND module =~ "*.app[0]"`.
2. **Plot it — native or matplotlib.** In the IDE: right-click the selection → **Plot using
   "<template>"** and choose the native or matplotlib variant. It creates the chart from that
   template (latest version) and **auto-fills `filter` from your selection**. Pick the template by
   data type × backend:

   | data | native | matplotlib |
   |---|---|---|
   | vectors | `linechart_native` | `linechart_mpl` |
   | scalars → bars | `barchart_native` | `barchart_mpl` |
   | scalars vs iteration variable | `scatterchart_itervars_native` | `scatterchart_itervars_mpl` |
   | histograms | `histogramchart_native` | `histogramchart_mpl` |
   | statistics → box/whiskers | — | `boxwhiskers` |
   | arbitrary X/Y | `generic_xyplot_native` | `generic_mpl` |

   Headless equivalent (writes the same template-derived chart into the `.anf`, no IDE):
   ```bash
   . "$HOME/omnetpp-dev/setenv"
   scripts/new_chart_from_template.py --list                          # template ids
   scripts/new_chart_from_template.py Foo.anf --template linechart_native \
       --name "End-to-end delay [s]" --filter 'name =~ "endToEndDelay:vector"' --width 8 --height 6
   ```
   (`Foo.anf` is created if missing — `results/*.sca` + `*.vec` inputs — or appended to. Use
   `--template-dir inet/charttemplates` for INET's custom templates. See "Choose the chart backend".)
3. **Configure in the dialog.** Set title, axis titles/limits, legend, grid, size — these are chart
   **properties** (the *Configure Chart* dialog, or `--prop`/`--width`/`--height` headless).
   Presentation lives here, **not in the script** — see "Let the dialog drive presentation".
4. **Edit the script only if needed** — for custom *data aggregation* the dialog can't express. Keep
   presentation in properties and plot through `utils.plot_*` (see the contract).
5. **Render & commit.** `opp_charttool imageexport Foo.anf -n "<name>" -f png --dpi 150 -d
   doc/media` → check the PNG (native ⇒ it's the Matplotlib-emulated render) → commit the
   `.anf` + PNG → add the FIGURE RECIPE comment (below).

A chart is made from a template, which carries the **latest** script + `<dialogPage>` config forms +
defaults. Keep an existing chart current with the IDE's **Compare to Template** (diffs a chart's
script + dialog pages against its template) and **Reset to Template** (syncs them back). The full
`.anf` element reference is in **references/anf-format.md**.

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
dependencies on it. The genuinely useful helpers are **`default_colors`** (the house palette),
**`add_to_dataframe`** (per-row color/marker styling), **`annotate_barchart`** (bar value labels — no
stock equivalent), and **`create_custom_legend`** (richer legends). **Draw with the stock
`utils.plot_*`; do NOT call `inet.scave.plot.plot_bars` / `plot_vectors` unless you are actually using
their ordering/styling extras — otherwise the stock plotter is identical.** Import `inet.scave.plot`
only for a helper with no stock equivalent. Full how-to in **references/inet-scave-plot.md** — read it
before using or recommending it.

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

## Let the dialog drive presentation — don't hardcode it

The stock plotting helpers plus `postconfigure_plot` wire a chart's **title, legend, axis labels,
limits, scales, and grid to its properties** (the *Configure Chart* dialog). Use them and **do not
re-set those in the script** — hardcoding overrides the user's dialog choices and breaks
configurability. This is the most common mistake.

- `utils.plot_vectors` / `plot_bars` / `plot_lines` / `plot_histograms` — draw the data, set the
  **title** from the `title` property (auto-generated if empty), and draw the **legend** with labels
  from the `legend_*` properties. They work for both native and matplotlib charts (the mpl templates
  reuse the same scripts), branching internally on `chart.is_native_chart()`.
- `utils.postconfigure_plot(props)` (call it last, before the export hook) — applies
  `xaxis_title`/`yaxis_title`, `xaxis_min/max` & `yaxis_min/max` (limits), `xaxis_log`/`yaxis_log`,
  and `grid_show`/`grid_density`; for native charts it also places the legend from
  `legend_placement` / `legend_show` / `legend_border`.

So **do NOT put these in the script**: `set_title`, `set_xlabel`/`set_ylabel`, `set_xlim`/`set_ylim`,
`margins`, `set_xticks`, `legend(loc=…, framealpha=…)`, `grid(…)`, or cosmetics like hiding spines or
custom frame alpha. They belong in the chart's properties — set them in the dialog, or with
`new_chart_from_template.py --width/--height/--prop`. A value that must be data-derived should still
go through a property the user can override.

**Drop to raw `matplotlib` only for what the helpers can't express.** Even then: assemble a DataFrame
and run it through `utils.plot_lines(df, props)` if at all possible (you keep the dialog-driven title,
legend, and axes); use `utils.set_plot_title(props["title"])` not `ax.set_title`; read
limits/labels/legend from `props`, never literals; and end with `utils.postconfigure_plot(props)`.
A custom chart usually only needs custom *data aggregation* — do that, then plot through the helpers.

**Rename series via `legend_replacements`, not by rewriting the series column in the script.** To give
a series a readable name (e.g. `*.hostB.app[0]` → `hostA → hostB flow`), add the mapping to the chart's
**Legend dialog page** rather than mutating the `module`/`name` column the pivot groups on. The
replacements come in two forms: `find --> replace` (literal substring) and `/find/replace/` (regex).
They are applied by `make_legend_label` **before** `sort_rows_by_legend`, so the Ordering page's regexes
match the *renamed* labels — dialog pages stay in one vocabulary. Rewriting the series column instead
splits naming across two schemes (the visible legend vs. the ordering/pivot keys) and has to be kept in
sync by hand. Exception: **synthesized** rows the script itself creates (an aggregate/total series that
isn't in the data) must be named in the script — there is no source label for a replacement to match.

## Axis units and labels

Axis labels come from the framework, but *how* depends on whether the chart uses the unit machinery:

- **Unit-aware** (chart has `xaxis_unit`/`yaxis_unit` properties — the line/bar templates add them,
  empty by default): the plot helpers + `postconfigure_plot` build the label as **`axis_title` +
  ` [unit]`** and *convert* the data to the target unit. Use this when you plot a **raw result that
  carries a unit** and want it converted/shown — e.g. `endToEndDelay` in `s`: set `yaxis_unit=ms`,
  give the axis a base title, and the framework does the conversion and label.
- **Title-only** (no unit props): `postconfigure_plot` applies `xaxis_title`/`yaxis_title` verbatim.

**Gotcha — empty unit props on a derived-value chart.** Because the templates include the unit props
(even empty), a chart is unit-aware *by default*. For a chart plotting a **computed** quantity
(throughput from a `count`, an itervar axis) with the unit baked into the title, two behaviors matter:

1. `plot_lines` **never sets the x-label** (only y); `postconfigure_plot` applies the title→x-label
   fallback **only when neither `xaxis_unit` nor `yaxis_unit` is declared** (the backward-compat block
   in `utils.py` guards on `"xaxis_unit" not in props and "yaxis_unit" not in props`). So a line chart
   that keeps the (empty) unit props gets **no x-label** unless you hand-set one.
2. For bars, `_set_xlabel`/`_set_ylabel` take the title straight from `xaxis_title`/`yaxis_title`
   regardless, and append `[unit]` **only when the data's unit column is non-empty** (`len(unit) > 0`).
   So clearing `df["unit"] = ""` keeps the label to the title alone, with no stray `[]` — do **not**
   also force it by assigning `df["name"]`.

**Do NOT delete the empty `xaxis_unit`/`yaxis_unit` property declarations to "fix" this** (earlier
versions of this skill wrongly recommended that). `opp_charttool` won't object, but the **IDE rejects
the chart the moment it is opened for editing** — `Edited properties not declared: [yaxis_unit]` —
because the template's Plot dialog page still carries a widget for that property, and every dialog
widget requires a declared property. This bites *only* in the IDE; headless renders stay green, so
removing the props silently ships a chart the IDE then refuses to open.

**The IDE-safe recipe for a derived quantity:** keep the unit props **declared but empty**, put the
unit in the axis title (`yaxis_title = "… [Mbps]"`), and clear the data unit with `df["unit"] = ""`.
For **bars** that is the whole fix — the label reads `Throughput [Mbps]`, no workaround. For **lines**
the x-label still needs a hand-set (`p.set_xlabel(...)`) because the title→x-label fallback is
suppressed while the props are declared — the lesser evil versus a chart the IDE won't open.

**Rule of thumb:** raw result + want unit conversion → use the unit dialog; computed/derived quantity
→ keep the unit props declared-but-empty, bake the unit into the title, and clear `df["unit"]`.

## Render headlessly with opp_charttool

`opp_charttool` is a plain Python script needing the OMNeT++ Python package on `PYTHONPATH`, so
**source setenv first**:

```bash
. /home/user/omnetpp-dev/setenv          # puts .../python on PYTHONPATH
opp_charttool info Foo.anf               # list charts with indices + types
opp_charttool imageexport Foo.anf -n "Per-station throughput" -f png --dpi 150 -d doc/media
opp_charttool imageexport Foo.anf -i 0 -f png --dpi 150 -d doc/media   # or by index
```

- Select the chart with `-n <name-substring>` or `-i <index>` (not both). `info` shows indices.
- **`-d` resolves relative to the `.anf`'s directory, not your cwd.** Since the `.anf` sits in the
  showcase root, use `-d doc/media` (or an absolute path) — a repo-root path like
  `-d showcases/.../doc/media` gets doubled into a stray `showcases/.../showcases/...` tree.
- **Default size: 8×6 inches at 150 dpi** (→ 1200×900 px). Set the chart's `image_export_width=8` and
  `image_export_height=6` properties; **dpi is not a chart property — pass it at export with
  `--dpi 150`**. A chart created from a template inherits *its* width/height — override to 8×6 unless a
  specific showcase deliberately uses another size. (Older committed PNGs are ~80 dpi / 12×8 — don't
  match those.)
- **Output filename** = the chart's `image_export_filename` property, else a sanitized chart name.
  `-o <name>` overrides; the format adds the extension. Set the property only when the chart name is
  ambiguous or shared (most showcase charts rely on the name fallback).
- `-f` format defaults to **svg** — pass `-f png` for the raster figure (most showcase media is PNG).
- Export always goes through Matplotlib, **including native charts** — hence the native eyeball check.

## Design — can the reader see the point?

The test that matters: after rendering, **look at the chart and ask — can a reader see the thing it is
meant to show?** Every showcase chart exists to make one specific point (e.g. "under rate anomaly
every station collapses to the slow station's rate"). Good design is that point reading clearly and
unambiguously. Everything below is just the common ways it fails — **judgment calls, not rules**; fix
whatever obscures the point:

- **Distinguishable elements.** Series tell apart; and a non-data mark (reference line, threshold,
  annotation) must not blend into the data where that hides the point. *No blanket rule against
  reusing a color* — but e.g. in per-station-throughput the reference line reused the orange series
  color and merged with the bars, hiding the very level the chart is about; a neutral dark dashed line
  fixes it.
- **The point stands out.** Emphasize the element that carries the story; let context recede.
- **Legend vs data.** Does the legend overlap or obscure the data? Move it (`legend_placement`).
- **Whitespace / ranges.** Unwarranted empty space? Tighten the axis ranges — *unless* they're
  deliberately matched to another chart for side-by-side comparison (keep them aligned then).
- **Legibility.** Markers when points are few or lines overlap (square); the grid supports rather than
  competes.
- **Palette.** `default_colors` for the data series; non-data marks are a judgment call (often
  gray/black).
- **Consistency** across a showcase's charts where feasible (not always possible).

Most of this you only catch by **actually looking at the rendered PNG** — make the visual review a
step, not an afterthought.

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
             -f png --dpi 150 -d doc/media/   ; image_export_width/height 8×6 → 1200×900
   stamp:    captured 2026-06, INET 4.6
```

## Best practices (from the surveyed showcases)

- **Start from the latest template** (IDE new-from-template, or the template dir) — it brings the
  current script, dialogPages, property names, rc-params, and defaults. Use **Compare/Reset to
  Template** to keep an existing chart in sync; if you copy a sibling as a shortcut, **Compare to
  Template** first to confirm it isn't stale.
- **Keep the full `<dialogPage>` blocks** — showcase charts carry them (the IDE writes them), so the
  chart stays first-class/editable in the IDE. Don't strip them to "minimize" the `.anf`.
- **Every dialog-page widget needs its `<property>` declaration** — do not delete a property just
  because the script overrides it or leaves it empty. The IDE validates chart-vs-dialog on edit and
  rejects a mismatch with `Edited properties not declared: [<id>]`. `opp_charttool` skips this check,
  so a render can succeed while the IDE refuses to open the chart. If you must neutralize a property,
  set it declared-but-empty (see the `yaxis_unit` case in "Axis units and labels"), don't remove it.
- **Let the dialog drive presentation** — use `utils.plot_*` + `postconfigure_plot`; don't hardcode
  title, axis labels/limits, legend placement, grid, ticks, or cosmetics in the script (see "Let the
  dialog drive presentation" above). Drop to raw matplotlib only for what the helpers can't do.
- **Line charts with few data points** — add markers so each point reads clearly; house choice is the
  **square** marker. Set the chart's `marker` property (Lines page in the dialog; matplotlib code `s`),
  not in the script.
- **Bar charts** — grid *behind* the bars, *dashed*, and *horizontal lines only* (the value-axis
  lines, to read bar heights). Dashed + behind via rc-params (`grid.linestyle: --`,
  `axes.axisbelow: True`); the dialog grid covers both axes, so restrict it to the horizontal lines in
  the script after `postconfigure_plot`: `ax = plt.gca(); ax.grid(False); ax.grid(True, axis="y")`.
  (Axis-specific grid is the rare presentation detail with no dialog control — the one allowed
  exception to "grid from the dialog".)
- **House rc-params**: `savefig.transparent: True` (and often `bbox: tight`) for clean doc embedding —
  near-universal; inherited from the template.
- **Default size 8×6 inches at 150 dpi** — `image_export_width=8` / `height=6` properties; dpi is the
  export-time `opp_charttool --dpi 150` flag (not a chart property). Older PNGs are ~80 dpi / 12×8.
- **Make sure axis labels carry the unit** (e.g. `Throughput [Mbps]`, `Delay [ms]`). The clean way is
  to set the unit in the dialog (`yaxis_unit`/`xaxis_unit`) — the framework converts and appends
  `[unit]` automatically. For a derived quantity with no convertible unit, put the unit in the axis
  title and clear `df["unit"] = ""`, but leave the unit props **declared-but-empty** — do not delete
  them (see "Axis units and labels").
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

- **scripts/new_chart_from_template.py** — headless "new chart from the latest template" (no IDE);
  `--list` shows template ids. See "Start from the latest template" above.
- **references/chart-script-api.md** — the `omnetpp.scave` API cheatsheet: `results` getters + filter
  grammar, `chart`, the `utils` plotting/pivot/export helpers, `ideplot`, and `vectorops`.
- **references/anf-format.md** — the `.anf` XML format, the element/attribute reference, a minimal
  from-scratch skeleton (for understanding the structure), the template catalog, and both worked
  template scripts (native + matplotlib).
- **references/inet-scave-plot.md** — the `inet.scave.plot` helper reference (what each provides, when
  it beats the stock equivalent — `default_colors` and `add_to_dataframe` are the common ones), plus
  the INET "enhanced histogram" custom template.
