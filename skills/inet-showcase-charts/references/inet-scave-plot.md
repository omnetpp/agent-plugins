# `inet.scave.plot` — INET chart helpers (how-to)

**Discipline first.** Default to the stock `omnetpp.scave` tools. Plain `utils.*` plus custom
Matplotlib can express anything, and `inet.scave.plot` may later fold into the OMNeT++ tools — so
don't build hard dependencies on it. Reach for it **only when one of its features genuinely removes
real boilerplate**: explicit per-row ordering, per-row style overrides, multi-dimensional / custom
legends, or faded color cycles. This file documents what it offers so that *when* you use it, you
use it correctly.

Source (read for exact current signatures — this module evolves and has deprecated members):
`/home/user/inet/python/inet/scave/plot.py`. Re-exported via `inet/python/inet/scave/__init__.py`
(`from inet.scave.plot import *`).

## Import

```python
import inet.scave.plot
default_colors = inet.scave.plot.default_colors
```
(INET showcase scripts use the fully-qualified `inet.scave.plot.*` form, not `from … import *`.)

## When it beats the stock equivalent

| Need | Stock | `inet.scave.plot` |
|---|---|---|
| Plot vectors/bars, default styling | `utils.plot_vectors` / `utils.plot_bars` | — (use stock) |
| **Force a specific series order** (not legend-alphabetical) | manual | `add_order_column` + enhanced plotters honor an `order` column |
| **Per-row style overrides** (one series gets a marker / dashes) | manual loop | `add_to_dataframe(...)` adds an `additional_style` column the enhanced plotters apply |
| **Custom / multi-dimensional legend** | `plt.legend` by hand | `create_custom_legend(...)` |
| **Faded color families** (related series in shades of one color) | manual | `get_faded_color_cycle`, `fade_color`, `scale_lightness` |

If none of these apply, use the stock helpers. (In the surveyed showcases, `default_colors` and
`add_to_dataframe` are by far the most-used — most charts use nothing else from this module.)

## Core pattern — ordering + per-row styling

The main value-add is attaching `order` and `additional_style` columns to the DataFrame, then using
the enhanced plotters which honor them. Sketch (confirm arg names against the source):

```python
import inet.scave.plot as iplot

# style_tuple_list pairs a selector with a style dict; default_dict styles the rest;
# order gives explicit row ordering.
df = iplot.add_to_dataframe(df, style_tuple_list, default_dict, order)
iplot.plot_vectors(df, props)          # superset of utils.plot_vectors; applies additional_style
iplot.postconfigure_plot(props)
```

`additional_style` is also settable directly: rows carry a stringified dict like
`"{'marker': '^'}"`, which the enhanced plotters merge into the per-series style (this is how the
`Throughput.anf` showcase marks analytical vs simulated series).

## Helper catalog

Confirm exact signatures in the source before relying on them.

**Colors**
- `default_colors` = `['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd']`; `get_default_colors()`
- `scale_lightness(color, factor)`, `fade_color(color, amount)`, `get_faded_color_cycle(...)`
- `hextriplet(...)`, `rgb2hex(...)`

**Enhanced plotters** (drop-in supersets of `utils.*` that add ordering + per-row styling)
- `plot_vectors(df, props, global_style=None, custom_cycle=None)`
- `plot_vectors_separate(...)`, `plot_vectors_separate_grouped(...)`, `plot_vectors_separate_faded(...)`
- `plot_bars(df, ..., order=None, zorder=None, rename=None, override_width=None)`
- `plot_lines(...)`, `postconfigure_plot(props)`

**DataFrame styling/ordering**
- `add_to_dataframe(df, style_tuple_list, default_dict, order)` — adds `additional_style` / `order`
- `add_legend_label_column(...)`, `add_order_column(...)`, `sort_values_by_legend_label(...)`

**Legends / annotations**
- `create_custom_legend(props, style_tuple_list, order, ...)` — the recommended legend builder
- `annotate_barchart(ax, ...)`, `fix_legend_transparency(...)`
- Deprecated — do **not** use: `create_multidimensional_legend`, `quick_reorder_legend`

**Caveats**
- Depends on `inet.common.util` logging and mutates global Matplotlib rc params.
- Several members are deprecated (above). Prefer `create_custom_legend` for custom legends.

## INET custom chart template — "enhanced histogram"

There is an INET-specific template at `/home/user/inet/charttemplates/` (a single custom template,
`type = MATPLOTLIB`, `resultTypes = histogram`, `scriptFile = "enhanced histogram.py"`, with its own
dialog pages). It is **not** on the default template path, so load it explicitly:

```bash
opp_charttool templates -I /home/user/inet/charttemplates    # list it
```

Use it as the starting script when authoring a richer histogram than `histogramchart_mpl` provides.
Note: `/home/user/inet/python/inet/documentation/media.py` is documentation-media housekeeping
(reconciles `.. figure:: media/...` references against checked-in PNGs) — not chart generation.
