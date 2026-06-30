# `omnetpp.scave` chart-script API

The contract every chart script is written against. Same API in the IDE and headless
(`opp_charttool`); the implementation is swapped based on `os.environ["WITHIN_OMNETPP_IDE"]`.
Source: `/home/user/omnetpp-dev/python/omnetpp/scave/`. Canonical reference appendix:
`/home/user/omnetpp-dev/doc/src/manual/appendix-chart-api.tex` (auto-generated from these docstrings).

## Contents
- [Script skeleton](#script-skeleton)
- [`chart` — chart context](#chart--chart-context)
- [`results` — querying results](#results--querying-results)
- [Filter grammar](#filter-grammar)
- [`utils` — plotting & export helpers](#utils--plotting--export-helpers)
- [`ideplot` — native plotting](#ideplot--native-plotting)
- [`vectorops` — vector operations](#vectorops--vector-operations)

## Script skeleton

Native (LINE/BAR/HISTOGRAM):
```python
import math
from omnetpp.scave import results, chart, utils

props = chart.get_properties()
utils.preconfigure_plot(props)

try:
    df = results.get_vectors(props["filter"], include_attrs=True, include_runattrs=True,
                             include_itervars=True)
except results.ResultQueryError as e:
    raise chart.ChartScriptError("Error while querying results: " + str(e))
if df.empty:
    raise chart.ChartScriptError("The result filter returned no data.")

df = utils.perform_vector_ops(df, props["vector_operations"])
utils.add_legend_labels(df, props)
utils.sort_rows_by_legend(df, props)
utils.plot_vectors(df, props, sort=False)        # plot_vectors picks ideplot vs plt automatically
utils.postconfigure_plot(props)

utils.export_image_if_needed(props)
utils.export_data_if_needed(df, props)
```

Matplotlib (MATPLOTLIB):
```python
import matplotlib.pyplot as plt
from omnetpp.scave import results, chart, utils

props = chart.get_properties()
utils.preconfigure_plot(props)

df = results.get_scalars(props["filter"], include_itervars=True, include_runattrs=True)
if df.empty:
    raise chart.ChartScriptError("The result filter returned no data.")

fig, ax = plt.subplots()
# ... arbitrary matplotlib ...
utils.export_image_if_needed(props)              # MUST be last; no-op interactively
```

`utils.export_image_if_needed(props)` is mandatory — without it `opp_charttool imageexport` produces
no file.

## `chart` — chart context
`/home/user/omnetpp-dev/python/omnetpp/scave/chart.py`

| Call | Returns / does |
|---|---|
| `chart.get_properties()` | `dict[str,str]` of this chart's `<property>` values. Entry point of every script. |
| `chart.get_property(key)` | single value or `None` |
| `chart.get_name()` | chart name |
| `chart.get_chart_type()` | `"BAR"` / `"LINE"` / `"HISTOGRAM"` / `"MATPLOTLIB"` |
| `chart.is_native_chart()` | `True` unless type is MATPLOTLIB. Branch with `p = ideplot if chart.is_native_chart() else plt` |
| `chart.set_suggested_chart_name(name)` | IDE hint; no-op headless |
| `chart.ChartScriptError(msg)` | raise for user-facing errors — charttool prints just the message, no traceback |

## `results` — querying results
`/home/user/omnetpp-dev/python/omnetpp/scave/results.py`. Every getter's first arg is a filter string
(stateful/IDE/charttool) or a raw DataFrame (stateless). `results.ResultQueryError` on bad filter.

| Getter (common kwargs: `include_attrs/runattrs/itervars/param_assignments/config_entries=False`) | Returns columns |
|---|---|
| `get_scalars(filter, include_fields=False, convert_to_base_unit=True)` | `runID, module, name, value(float), unit` + metadata |
| `get_vectors(filter, start_time=-inf, end_time=inf, omit_empty_vectors=False)` | `runID, module, name, vectime(ndarray), vecvalue(ndarray), unit` |
| `get_histograms(filter)` | `… count, sumweights, mean, stddev, min, max, underflows, overflows, binedges, binvalues, unit` |
| `get_statistics(filter)` | `… count, sumweights, mean, stddev, min, max, unit` (no bins) |
| `get_parameters(filter)` | `runID, module, name, value(str)` |
| `get_runs / get_runattrs / get_itervars / get_config_entries(filter)` | run-level metadata as `runID, name, value` |
| `get_results(filter, row_types=None, start_time, end_time)` | mixed/raw rows |
| `read_result_files / set_inputs / add_inputs` | stateless standalone loading |

Metadata `include_*` flags pivot extra columns in as **strings** — convert with `utils.to_numeric()`.

## Filter grammar
Documented in `results.py` docstring. Terms over fields `name`, `module`, `type`, `file`, `run`,
`runattr:<n>`, `attr:<n>`, `itervar:<n>`, `config:<k>`. Examples:
```
name =~ "throughput:last"
module =~ "*.host[*].app[0]" AND name =~ "packetReceived:count"
name =~ "endToEndDelay:vector" AND itervar:numHosts =~ "{10..50}"
```
Wildcards: `?` `*` `**` `{a-z}` `{32..255}`. Combine with `AND` / `OR` / `NOT`.

## `utils` — plotting & export helpers
`/home/user/omnetpp-dev/python/omnetpp/scave/utils.py`. The workhorses (note: **no `plot_scalars`** —
scalar charts go through the bar/scatter pivot pipeline).

```
preconfigure_plot(props)                     set up rc/style BEFORE plotting; call first
postconfigure_plot(props)                    apply axis/legend/grid/title props AFTER plotting
plot_vectors(df, props, sort=True)           line plot from vectime/vecvalue rows
plot_vectors_separate(df, props, sort=True)  one subplot per vector, shared X
plot_lines(df, props, sort=True)             generic X/Y line plot (columns x, y)
plot_bars(df, errors_df=None, meta_df=None, props={}, sort=True)   grouped/stacked bars
plot_histograms(df, props, sort=True)        histogram plot
plot_boxwhiskers(df, props, sort=True)       box-and-whiskers
perform_vector_ops(df, operations: str)      apply a vector_operations text block (see vectorops)
select_xaxis_and_groupby(df, props)          -> (xaxis_itervar, group_by)   for scatter
select_groups_series(df, props)              -> (groups, series)            for bars
pivot_for_barchart(df, groups, series, confidence_level=None)   -> (valuedf, errorsdf, metadf)
pivot_for_scatterchart(df, xaxis_itervar, group_by, confidence_level=None)
add_legend_labels(df, props)                 add a 'legend' column
sort_rows_by_legend(df, props=())
make_legend_label(legend_cols, row, props={})
extract_label_columns(df, props)             -> (title_cols, legend_cols)
make_chart_title(df, title_cols) / set_plot_title(title, suggested_chart_name=None)
get_confidence_level(props) / confidence_interval(alpha, data)
histogram_bin_edges_from_props(values, unit, props)
to_numeric(df, columns=[]) / split(s, sep=',') / parse_rcparams(rc_content)
export_image_if_needed(props)                THE export hook — must be last; renders via Matplotlib
export_data_if_needed(df, props, **kwargs)
```

Scalar→bar pipeline: `get_scalars` → `select_groups_series` → `pivot_for_barchart` → `plot_bars`.
Scalar→scatter: `get_scalars` → `select_xaxis_and_groupby` → `pivot_for_scatterchart` → `plot_lines`.

## `ideplot` — native plotting
`/home/user/omnetpp-dev/python/omnetpp/scave/ideplot.py`. A deliberate **subset of
`matplotlib.pyplot`**, so a native chart switches to pure matplotlib by changing the import. Native
charts use this (directly or via `utils.plot_*`).

- `plot(xs, ys, key=, label=, drawstyle=, linestyle=, linewidth=, color=, marker=, markersize=)`
- `hist(x, bins, key=, density=, weights=, cumulative=, histtype='stepfilled', color=, label=, …)`
- `bar(x, height, width=0.8, key=, label=, color=, edgecolor=)`
- pyplot-like: `title, xlabel, ylabel, xlim, ylim, xscale, yscale, xticks, grid, legend(show, frameon, loc)`
- `legend(loc=…)` also accepts `'outside top left'`, `'outside right center'`, etc.
- native-only (no-op headless): `set_property(key, value)`, `set_properties(props)`,
  `get_supported_property_keys()` (e.g. `'Plot.Title'`, `'X.Axis.Max'`, `'Bars.Baseline'`,
  `'Legend.Display'`), `set_warning(text)`, `is_native_plot()`

## `vectorops` — vector operations
`/home/user/omnetpp-dev/python/omnetpp/scave/vectorops.py`. Applied via
`utils.perform_vector_ops(df, text)` or the `vector_operations` property. One op per line:
`[compute|apply :] opname[(args)]` — default mode **apply** (replaces the row); **compute** adds rows.

```
aggregate(function='average')  combine several vectors into one (average/count/max/min/sum…)
merge                          merge several series into one, time-ordered
mean / sum                     running mean / running sum
movingavg(alpha)               exponentially weighted moving average
slidingwinavg(window_size)     mean over a sliding window
winavg(window_size=10)         batched average over winsize values
timewinavg(window_size=1)      time-window average
timewinthruput(window_size=1)  time-windowed throughput
timeavg(interpolation)         average over time
integrate(interpolation='sample-hold')   integrate as step/linear function
difference / diffquot          y[k]-y[k-1] / difference quotient
add(c) / multiply_by(a) / divide_by(a) / modulo(m) / lineartrend(a)
divtime                        y[k]/t[k]
subtractfirstval               y[k]-y[0]
removerepeats                  drop consecutive repeated values
crop(t1, t2)                   discard values outside [t1,t2]
compare(threshold, less, equal, greater)
timeshift(dt) / timedilation(c) / timediff / timetoserial
expression(expression, as_time)   evaluate a Python expr per value, e.g. 'y+(t-tprev)*100'
```
