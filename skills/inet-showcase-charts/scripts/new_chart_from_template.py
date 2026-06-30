#!/usr/bin/env python3
"""
Create an OMNeT++ Analysis chart from the LATEST chart template, headlessly — no IDE.

Uses the `omnetpp.scave` library (the same one `opp_charttool` uses), so the new chart
carries the current template's script, full `<dialogPage>` blocks, and default properties.
The `.anf` is just XML; this assembles it the same way the IDE's "new chart from template"
does, but from the command line.

Prerequisite: source the OMNeT++ setenv first so `omnetpp.scave` is importable:
    . "$HOME/omnetpp-dev/setenv"

Examples:
    # list available template ids (+ type and name)
    new_chart_from_template.py --list

    # create Foo.anf (if missing) with a native line chart from the current template
    # (dpi is an export-time flag, set on opp_charttool, not a chart property)
    new_chart_from_template.py Foo.anf --template linechart_native --name "End-to-end delay" \
        --filter 'name =~ "endToEndDelay:vector"' --width 8 --height 6

    # append another chart to an existing .anf
    new_chart_from_template.py Foo.anf --template barchart_native --name "Throughput [Mbps]" \
        --filter 'name =~ "throughput:last"'
"""

import argparse
import os
import sys


def main():
    p = argparse.ArgumentParser(
        description="Create an OMNeT++ Analysis chart from the latest chart template, without the IDE.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("anf", nargs="?", help=".anf file to create (if missing) or append the chart to")
    p.add_argument("--template", help="chart template id (see --list)")
    p.add_argument("--name", help="chart name (default: the template's name)")
    p.add_argument("--list", action="store_true", help="list available template ids and exit")
    p.add_argument("--template-dir", action="append", default=[], metavar="DIR",
                   help="extra template dir to search (e.g. inet/charttemplates); repeatable")
    p.add_argument("--filter", dest="filter_expr", metavar="EXPR",
                   help="result filter expression (set as the 'filter' property)")
    p.add_argument("--filename", help="image_export_filename (output PNG base name)")
    p.add_argument("--width", help="image_export_width in inches (house default 8)")
    p.add_argument("--height", help="image_export_height in inches (house default 6)")
    p.add_argument("--prop", action="append", default=[], metavar="KEY=VALUE",
                   help="set an arbitrary template property; repeatable")
    p.add_argument("--input", action="append", default=[], metavar="PATTERN",
                   help="input pattern for a NEW .anf (repeatable); "
                        "default: results/*.sca and results/*.vec")
    args = p.parse_args()

    try:
        from omnetpp.scave import analysis, charttemplate
    except ImportError:
        sys.exit("error: cannot import omnetpp.scave — source the OMNeT++ setenv first:\n"
                 '    . "$HOME/omnetpp-dev/setenv"')

    templates = charttemplate.load_chart_templates(args.template_dir, add_default_locations=True)

    if args.list:
        for tid in sorted(templates):
            t = templates[tid]
            print(f"{tid:34s} {t.type:11s} {t.name}")
        return

    if not args.anf or not args.template:
        p.error("ANF and --template are required (unless --list)")

    if args.template not in templates:
        sys.exit(f"error: unknown template '{args.template}'.\nAvailable: "
                 + ", ".join(sorted(templates)))
    template = templates[args.template]

    # Collect requested properties; keep only keys the template actually defines
    # (create_chart() rejects unknown keys).
    requested = {}
    if args.filter_expr is not None:
        requested["filter"] = args.filter_expr
    if args.filename is not None:
        requested["image_export_filename"] = args.filename
    if args.width is not None:
        requested["image_export_width"] = args.width
    if args.height is not None:
        requested["image_export_height"] = args.height
    for kv in args.prop:
        key, _, value = kv.partition("=")
        requested[key] = value

    props = {k: v for k, v in requested.items() if k in template.properties}
    skipped = [k for k in requested if k not in template.properties]
    if skipped:
        print(f"warning: template '{template.id}' does not define {skipped}; not set. "
              f"Its property keys are: {sorted(template.properties)}", file=sys.stderr)

    # Load the analysis FIRST so existing chart ids are registered (avoids id collisions),
    # then create the chart so it gets a fresh, non-colliding id.
    if os.path.exists(args.anf):
        an = analysis.Analysis.from_anf_file(args.anf)
    else:
        inputs = args.input or ["results/*.sca", "results/*.vec"]
        an = analysis.Analysis(inputs=list(inputs), items=[])

    chart = template.create_chart(name=args.name, props=props)
    an.root_folder.items.append(chart)
    an.to_anf_file(args.anf)
    print(f"Wrote chart '{chart.name}' (template {template.id}, type {chart.type}, id {chart.id}) "
          f"to {args.anf}")


if __name__ == "__main__":
    main()
