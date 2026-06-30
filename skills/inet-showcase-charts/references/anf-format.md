# The `.anf` format, templates, and worked chart scripts

## Contents
- [XML structure](#xml-structure)
- [Minimal working skeleton (matplotlib)](#minimal-working-skeleton-matplotlib)
- [Authoring a native chart](#authoring-a-native-chart)
- [Built-in template catalog](#built-in-template-catalog)
- [Worked idiom 1 — native line chart](#worked-idiom-1--native-line-chart-linechartpy)
- [Worked idiom 2 — matplotlib](#worked-idiom-2--matplotlib-generic_mplpy)

## XML structure

Root `<analysis version="2">` with two children: `<inputs>` then `<charts>`.

| Element | Notes |
|---|---|
| `<inputs>` | one or more `<input pattern="results/*.sca"/>`. Patterns relative to the `.anf` dir. Typically one `.sca` and one `.vec` line. |
| `<charts>` | contains `<chart>` and/or `<folder>` elements |
| `<folder id name>` | optional grouping, may nest and contain charts; charttool flattens them |
| `<chart …>` | one chart (attributes below) |
| `<script><![CDATA[ … ]]></script>` | the Python chart script (required) |
| `<property name value/>` | zero or more; exactly what `chart.get_properties()` returns |
| `<dialogPage id label><![CDATA[ <xswt>… ]]></dialogPage>` | IDE config-form tabs. **Optional** — omit for hand-authored matplotlib charts; the IDE falls back to the template's pages. |

`<chart>` attributes: `id` (unique), `name`, `type` (`LINE`/`BAR`/`HISTOGRAM`/`MATPLOTLIB`),
`template` (a template id — provenance only; the embedded `<script>` is authoritative),
`icon`, `resultTypes` (often `""`), `createdWith` (often `""`).

XML escaping inside attribute values: `&quot;` for `"`, `&gt;`/`&lt;`, backslash-escaped inner
quotes — relevant for the `filter` property when it contains quoted patterns.

**Property precedence:** the `<property>` tags in the `.anf` are authoritative. When a chart is first
created in the IDE they are seeded from the template's xswt-widget defaults. The script only *reads*
`props[...]`; it never defines defaults. So to change a chart, edit its `<property>` values (and/or
the script). `opp_charttool templates --properties` dumps a template's default property set.

## Minimal working skeleton (matplotlib)

Verified to render via `opp_charttool imageexport`. Also in `assets/starter.anf`.

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<analysis version="2">
    <inputs>
        <input pattern="results/*.sca"/>
        <input pattern="results/*.vec"/>
    </inputs>
    <charts>
        <chart id="1" name="My Chart" type="MATPLOTLIB" template="generic_mpl"
               icon="icons/full/obj/linechart.png" resultTypes="" createdWith="">
            <script><![CDATA[from omnetpp.scave import results, chart, utils
import matplotlib.pyplot as plt

props = chart.get_properties()
utils.preconfigure_plot(props)

df = results.get_scalars('name =~ "packetReceived:count" AND module =~ "*.app[*]"',
                         include_runattrs=True, include_itervars=True)
if df.empty:
    raise chart.ChartScriptError("The result filter returned no data.")

fig, ax = plt.subplots()
ax.bar(df["module"], df["value"])
ax.set_ylabel("packets received")
plt.tight_layout()

utils.export_image_if_needed(props)
]]></script>
            <property name="image_export_filename" value="my-chart"/>
        </chart>
    </charts>
</analysis>
```
Render: `opp_charttool imageexport file.anf -i 0 -f png --dpi 150 -d out/` → `out/my-chart.png`.

## Authoring a native chart

For an explorable chart (zoom/pan/toggle in the IDE), use `type="LINE"` (or `BAR`/`HISTOGRAM`) and
`template="linechart_native"` (etc.). Embed the template's script (see idiom 1) and the `<property>`
tags it reads — at minimum `filter`, `vector_operations` (can be empty), and the styling/axis props
you care about, plus `image_export_filename`. You can omit `<dialogPage>` blocks; the IDE uses the
referenced template's pages. After authoring, **export and eyeball** — the headless PNG is
Matplotlib-emulated and may differ slightly from the on-screen native widget.

To discover the exact property names a native template expects, run
`opp_charttool templates --properties` and copy the relevant keys.

## Built-in template catalog

`opp_charttool templates` (source: `/home/user/omnetpp-dev/ui/org.omnetpp.scave.templates/charttemplates/`):

| Template id | type | for |
|---|---|---|
| `linechart_native` | LINE | vector results as interactive line chart |
| `linechart_mpl` / `linechart_separate_mpl` | MATPLOTLIB | vectors, matplotlib (single / per-series subplots) |
| `barchart_native` / `barchart_mpl` | BAR / MATPLOTLIB | scalar results as grouped/stacked bars |
| `histogramchart_native` / `histogramchart_mpl` | HISTOGRAM / MATPLOTLIB | histogram results |
| `histogramchart_vectors_native` / `_mpl` | HISTOGRAM / MATPLOTLIB | build histograms from vectors |
| `scatterchart_itervars_native` / `_mpl` | LINE / MATPLOTLIB | scalar vs iteration variable (parameter studies) |
| `generic_xyplot_native` / `_mpl` | LINE / MATPLOTLIB | arbitrary X/Y |
| `generic_mpl` | MATPLOTLIB | blank matplotlib canvas — the base for custom charts |
| `boxwhiskers` | MATPLOTLIB | box-and-whiskers from statistics |
| `3dchart_itervars_mpl` | MATPLOTLIB | 2-itervar surface/heatmap |
| `linechart_legacy` / `scatterchart_legacy` | LINE | older variants |

Pick the closest template, copy its `scriptFile` (e.g. `linechart.py`, `barchart.py`,
`histogramchart.py`, `scatterchart.py`, `generic_mpl.py`) as your script, and adapt.

## Worked idiom 1 — native line chart (`linechart.py`)

Plots via `utils.plot_vectors`, which internally targets `ideplot` for native charts and `plt`
for matplotlib charts:

```python
import math
from omnetpp.scave import results, chart, utils

props = chart.get_properties()
utils.preconfigure_plot(props)

filter_expression = props["filter"]
start_time = float(props["vector_start_time"] or -math.inf)
end_time = float(props["vector_end_time"] or math.inf)
omit_empty_vectors = props["omit_empty_vectors"] == "true"

try:
    df = results.get_vectors(filter_expression, include_attrs=True, include_runattrs=True,
                             include_itervars=True, start_time=start_time, end_time=end_time,
                             omit_empty_vectors=omit_empty_vectors)
except results.ResultQueryError as e:
    raise chart.ChartScriptError("Error while querying results: " + str(e))

if df.empty:
    raise chart.ChartScriptError("The result filter returned no data.")

df = utils.perform_vector_ops(df, props["vector_operations"])

utils.add_legend_labels(df, props)
utils.sort_rows_by_legend(df, props)
utils.plot_vectors(df, props, sort=False)

utils.postconfigure_plot(props)

utils.export_image_if_needed(props)
utils.export_data_if_needed(df, props)
```

## Worked idiom 2 — matplotlib (`generic_mpl.py`)

The canonical "pure matplotlib" base — read a property, do anything, export:

```python
import numpy as np
import matplotlib.pyplot as plt
from omnetpp.scave import chart, utils

input = chart.get_property("input")     # arbitrary per-chart input string from the dialog
props = chart.get_properties()

r = np.arange(0, 2, 0.01)
theta = 2 * np.pi * r
ax = plt.subplot(111, projection='polar')
ax.plot(theta, r)
ax.set_title("A line plot on a polar axis", va='bottom')
ax.grid(True)

utils.export_image_if_needed(props)
```

For a real showcase matplotlib chart, replace the demo body with a `results.get_*(props["filter"])`
query, an empty-data guard, and your plotting — keep `utils.preconfigure_plot(props)` first and
`utils.export_image_if_needed(props)` last.
