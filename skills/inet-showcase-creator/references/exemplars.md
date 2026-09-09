# Showcase exemplars: the house style of eleven maintainer-rated pages

Derived from eleven `showcases/<path>/doc/index.rst` files, read in full and measured with
grep/scripts (counts are exact): wireless/{txop,blockack,aggregation,fragmentation,coexistence,
analogmodel}, tsn/framepreemption, tsn/timesynchronization/clockdrift,
visualizer/canvas/{radiomediumactivity,spectrum}, general/pcaprecording. Paths below are relative
to `showcases/`. Pages are 1162-4248 words (median 2542), 212-611 lines.

## 1. Shared conventions

### Section skeleton and order
- Heading marks: `=` title, `-` sections, `~` subsections (11 of 11 use `=`/`-`; 10 of 11 use `~`;
  only framepreemption goes deeper, to `+` and `*`).
- First section is `Goals` and it ends with the version/source-location lines: 11 of 11.
- A theory section before the model ("About TXOP", "About Block Acknowledgment", "About the
  visualizer", "About Analog Models", clockdrift's "Simulating Clock Drift and Time
  Synchronization"): 8 of 11. coexistence, framepreemption and pcaprecording put the theory
  inside `The Model` instead.
- A separate "X in INET" section ("TXOP in INET", "Block Acknowledgment in INET", "802.11
  Fragmentation in INET"): 3 of 11. Elsewhere the INET module/parameter mapping sits at the end
  of the About section.
- `The Model` heading (or "The model", "The Model and Results"): 8 of 11. A `Configuration(s)`
  subsection under it: 5 of 11 (aggregation, coexistence, framepreemption, radiomediumactivity,
  pcaprecording).
- `Results` as its own `-` heading: 6 of 11 (txop, aggregation, fragmentation, coexistence,
  framepreemption, pcaprecording). The other 5 interleave config and results per example or per
  feature (blockack: one `~` per config; clockdrift: "Example:" chain; radiomediumactivity,
  spectrum, analogmodel: one `-` section per feature/model).
- `Sources:` line after the last result: 11 of 11; immediately followed by `Try It Yourself` in
  10 of 11 (radiomediumactivity inserts a "More information" section).
- Last two sections are `Try It Yourself` then `Discussion`: 11 of 11.
- Fixed headings are Title Case in 11 of 11; sentence-case topical subheadings in 3 of 11.

### Goals
- 1-3 paragraphs, 34-216 words (median 101). No figure in Goals in 10 of 11 (framepreemption
  has two before/after diagrams).
- Opens with a general definition of the feature or problem, never with "This showcase": 11 of 11.
  txop: "Transmit opportunity (TXOP) is a MAC feature in 802.11, which increases throughput for
  high priority data by providing contention-free channel access for a period of time."
- Contains one sentence naming the showcase's job: "In this showcase, we will demonstrate ..."
  6 of 11; "This showcase demonstrates/presents/consists of ..." 4 of 11; "This demonstration
  includes ..." 1 of 11.
- Closing "By the end of this showcase, you will understand ...": 4 of 11 (blockack,
  coexistence, framepreemption, analogmodel).
- Then the version and source-location lines: 11 of 11, identical form (section 4).

### Introducing a figure or video
- Of 120 figure/video directives, 100 are directly preceded by a sentence ending in a colon;
  4 directly follow another figure (paired charts); 16 follow a full-stop sentence. The colon
  lead-in is the dominant pattern in 11 of 11 pages (txop 3/3, pcaprecording 11/11).
- "Here is ..." lead-ins in 10 of 11 pages; "The following ..." in 7 of 11. Typical forms:
  "Here is the configuration:", "Here is a video of the simulation:", "The simulation uses the
  following network:" (7 of 11 pages), "Here is the same chart zoomed in:".
- Explanation comes AFTER the image: 104 of 120 directives are followed directly by a prose
  paragraph that reads the image (the rest are followed by another figure, a heading, or a note).
  The lead-in sentence says only what the image is; the reading comes after.
- Video lead-ins name what the viewer will see; analogmodel adds the legend in parentheses:
  "Here is a video of the simulation (successful link-layer transmissions are indicated with
  arrows; incorrectly received packets are indicated with packet drop animations):"

### Figure directives
- `.. figure::` for every image (107); `.. video::` for every video (13); standalone
  `.. image::` 0 of 11 (spectrum uses 4 `.. |x| image::` substitutions inside grid tables).
- `:width:` on 111 of 120 figure/video directives: 100% (39), 90% (38), 80% (10), 70% (10),
  60% (8), 50% (3), 30% (1), 25% (1). Full width for charts, packet views, videos; 60-80% for
  network diagrams and inspector shots; 25-50% for small icons.
- `:align: center` on every figure in 9 of 11 pages (radiomediumactivity 0 of 10,
  pcaprecording 1 of 10). Videos: `:align:` on 5 of 13.
- Captions: 1 of 107 figures (analogmodel `dimensional3d.png`); 10 of 11 pages have none.
- Capture-recipe comments next to videos in 3 of 11 (radiomediumactivity and pcaprecording as an
  HTML comment inside the directive body, analogmodel as an rst comment after it).

### Showing omnetpp.ini
- `literalinclude` of `../omnetpp.ini`: 10 of 11 pages, 72 blocks. radiomediumactivity instead
  pastes lines into `.. code-block:: none` (2 blocks). NED files literalincluded: 0 of 11.
- Every block is bounded by `:start-at:` (70) or `:start-after:` (2) and by `:end-at:` (56) or
  `:end-before:` (14); 2 run to end of file. `:language: ini` on 72 of 72.
- Option order `:start-at:`, `:end-at:`, `:language: ini` in 8 of 10 pages; clockdrift and
  pcaprecording put `:language:` first.
- Block size (non-blank ini lines): median 3; 53 of 72 blocks are <=5 lines, 60 of 72 <=10;
  per-page medians 2-4.5 except clockdrift (9) and analogmodel (24), which show whole configs
  with `:start-at: Config X` / `:end-before: Config Y`.
- Lead-in ends with a colon: 65 of 72 blocks; one sentence saying what the lines do, the block,
  often one sentence of consequence. blockack: "Transmitter power is lowered to make the
  communication more noisy, in order to get some lost packets:"
- `:download:`omnetpp.ini <../omnetpp.ini>`` in prose when naming where a config lives: 11 of 11
  (41 hits). "Here is the configuration ..." 6 of 11 pages, 18 hits.
- Excerpts anchor on config lines, so ini comments (4-31 lines per file) never render.

### Naming and describing configurations
- Config names are CamelCase describing the varied factor (`NoFragmentation`, `DCFfrag`,
  `RandomClockDriftGptpSync`, `RealisticPriorityQueueing`); 1-7 configs per showcase; base configs
  to extend in 2 of 11 (`OutOfBandSyncBase`, `RealisticBase`).
- Config names in prose in double backticks: 10 of 11 (analogmodel never names its configs).
- Bullet list `- ``Name``: description` introducing the configs: 5 of 11 (19 bullets); in
  aggregation and fragmentation each bullet states the expected outcome.
  aggregation: "- ``Aggregation``: Aggregation is on, and the MAC sends UDP packets in the best
  effort access category. Throughput is expected to increase substantially."
- "The simulation can be run by choosing the ``X`` configuration from the ini file.": 3 of 11.

### Presenting results
- Network screenshot before the configuration: 11 of 11.
- Evidence kinds: charts 5 of 11 (aggregation, fragmentation, coexistence, framepreemption,
  clockdrift); sequence charts 4 of 11 (txop, aggregation, coexistence, framepreemption); Qtenv
  packet traffic view / packet log 2 of 11 (blockack, framepreemption); packet inspector 3 of 11
  (blockack, framepreemption, pcaprecording); Wireshark 2 of 11; tcpdump 1 of 11; videos 6 of 11.
- Order inside Results: framepreemption and coexistence show behaviour evidence (video, packet
  log, sequence chart) before performance charts; aggregation shows charts first and the sequence
  chart after. Charts come in pairs (count + throughput) in aggregation, fragmentation, coexistence.
- Zoomed copy right after an overview chart: clockdrift (8), framepreemption (1). Predictions
  before the numbers ("expect"): 3 of 11. Numbers approximated with "about": 8 of 11.
- Implementation caveats named as such ("limitation", "implementation detail", "currently"): 5 of 11.

### Admonitions
- `.. note::` in 8 of 11 pages, 31 notes, 26-222 words (median 66), one paragraph or one bullet
  list. No other admonition type in any page (pcaprecording's `.. todo::` hides an old draft).
- Notes hold implementation limits, numbering/unit caveats, how-to tips, pointers to extra files.
- Inline "Note that ..." sentences in body text: 8 of 11 (24 hits).

### Roles and inline code
- `:ned:` for module types: 11 of 11 (5-26 per page, 151 total).
- `:par:` for parameter names: 10 of 11 (75 total; framepreemption uses backticks instead).
- `:cpp:` 1 of 11 (txop, inside one note); `:doc:` cross-links 4 of 11; `:ref:` 1 of 11.
- Double-backtick inline code for module instance names (``host1``), submodule paths
  (``mac.hcf.edca.edcaf[*].txopProcedure``), config names, parameter values (``true``), packet
  names (``Data-16``): 11 of 11, 15-74 per page.
- Grid tables for small comparisons: 3 of 11; `list-table` for side-by-side histograms: 1 of 11.

### Paragraph and sentence style
- 556 prose paragraphs; per-page median 25-46 words, mean 31-55. 71 of 556 (13%) exceed 70
  words, 26 (5%) exceed 100; longest 208 (radiomediumactivity).
- Sentences: per-page mean 14-19 words, median 13-18.
- First person plural "we"/"we'll" in 11 of 11 (1-35 hits); "Let's" in 2 of 11. Present tense for
  what the model does; "will"/"'ll" for the plan. "you" outside Goals and boilerplate: 1 hit in
  1 page (a framepreemption note).
- Passive for configuration facts is normal: "is/are configured|set|enabled|turned" 11 of 11
  (70 hits). Abbreviations expanded with the short form in parentheses: 8 of 11 (17 hits).
  "e.g."/"i.e." used freely: 9 of 11 (42 hits).
- Words per figure/video: 150-387 per page (median 254).

## 2. Anti-patterns absent from all eleven (each verified 0 of 11 by grep)
- "In one minute" / summary boxes; Conclusion, Summary or Key-takeaways sections.
- Details / Fine-print admonitions; any `warning`, `tip`, `important`, `seealso`, `admonition`.
- Bold takeaway lines directly under a figure or video.
- Numbered figure references ("Figure 3", `:numref:`); `:scale:`; `.. math::`.
- Standalone `.. image::` directives; YouTube/Vimeo embeds.
- RFC citations; standard clause or section numbers (framepreemption names "the 802.1Qbu
  standard" once, without a clause). Uppercase MUST/SHOULD normative language.
- Explanations of what omnetpp.ini is or how ini syntax works.
- Literalincluded NED files. Wikipedia links.
Not 0 of 11, so not listed: figure captions (1 of 107 figures), headings deeper than `~` inside
Results (framepreemption only), C++ names in prose (txop `:cpp:`, framepreemption ``cPacket``,
pcaprecording ``inet::ArpPacket`` and a link to Protocol.cc).

## 3. Per-page distinctive techniques

**wireless/txop** (protocol mechanism, 1162 words, 3 figures, 5 ini blocks). A complete page under
1200 words: one network figure, one sequence chart, nothing else. Lists the frame-sequence alternatives as
bullets before showing one; a TXOP-limit table replaces prose; ends with an invitation and a
limitation note. "This frame sequence is just an example. Various
combinations of frames can be sent during a TXOP. Observe the simulation for other combinations."
"The gap between the frames is a SIFS; the TXOP frame exchange is preceded and followed by a much
longer contention period." (wireless/txop/doc/index.rst)

**wireless/blockack** (protocol mechanism, 14 screenshots). An `Experiments` umbrella with `The
Model` then one `~` section per config; each config section = one sentence of purpose, the whole
config literalincluded, then packet-view/inspector screenshots. Every screenshot has a
what-and-where lead-in and a reading sentence after: "Here is the block ack request frame displayed
in Qtenv's packet inspector:" ... "The block ack request contains the starting sequence number,
which indicates the first packet to be acked. Here is the block ack response frame:" Losses are
engineered on purpose: "Transmitter power is lowered to make the communication more noisy, in order
to get some lost packets:" (wireless/blockack/doc/index.rst)

**wireless/aggregation** (performance comparison). Configs form "a progression to improve
throughput", each bullet ending with the expected effect; traffic is tuned so delay is comparable:
"To negate the effect of queue length on the delay of packets, we set the amount of traffic to
match the possible throughput in each configuration." Two charts back to back, prose with
percentages ("throughput increases by more than 400%"), then one sequence chart "on the same
time scale". Reads chart geometry: "The multiple data points above each other signify the
reception of an aggregate frame".
(wireless/aggregation/doc/index.rst)

**wireless/fragmentation** (performance comparison + parameter study). Same skeleton as
aggregation, plus a `Further Analysis` subsection of four parameter studies introduced in
sequence: "First, the iteration variable was the packet size (going from 100B to 2500B), with a
constant fragmentation threshold of 250 bytes:" / "Secondly, the fragmentation threshold was
iterated, using a 1000-byte packet size:". Justifies the operating point: "If there is too
much noise, the fragmentation doesn't make any difference, as communication becomes impossible.
If there is too little noise, fragmentation is disadvantageous due to the extra overhead." A note
points to `parameterstudy.ini` and the `.anf`. (wireless/fragmentation/doc/index.rst)

**wireless/coexistence** (cross-technology interference, 3241 words). No About section; `The
Model` carries the theory, a duration table and a linear sequence chart "The scale is linear."
Each spectral-mask figure is paired with the `frequencyGains` literalinclude that encodes it; the
syntax is explained once in bullets ("Briefly about the syntax:") that analogmodel reuses via
`.. include::`. Results open with a prediction paragraph before any evidence: "The Wifi host waits less than the WPAN host before accessing the channel, so it is
expected that the Wifi host will gain channel access most of the time. The Wifi might even starve
the WPAN." Then a video, then two bar charts. (wireless/coexistence/doc/index.rst)

**tsn/framepreemption** (TSN mechanism, 16 figures/videos, 4 heading levels). Two diagrams inside
Goals. A "Transmission on the Wire" background section explains OMNeT++ transmission updates so
the reader can decode the evidence. Results run behaviour evidence first -- video, packet log,
non-linear and linear sequence charts, Wireshark, packet inspector, module paths -- and only then
the delay chart, histograms in a `list-table`, back-of-the-envelope estimates in code lines
(``delay ~= txDuration + 2.6 * txDuration + IFG = 3.6 * txDuration = 0.36ms``), "Realistic Traffic". "Here is a video of the frame preemption behavior:" ... "The
frame sequence is displayed in the Qtenv packet log:" (tsn/framepreemption/doc/index.rst)

**tsn/timesynchronization/clockdrift** (mechanism tour, 4248 words, 23 charts). `The Model and
Results` merged, then six chained `Example:` subsections, each: one or two sentences of intent,
the whole config literalincluded (`:start-at: Config X`, `:end-before:` next), a paragraph on what
the lines set, chart, reading, zoomed chart. "Example: Out-of-Band Synchronization of Clocks,
Constant Drift" ... "Let's see the time differences:" ... "Let's zoom in on the beginning of the
above chart:". A forward-referencing note defers the gating config to the delay section; 8 notes,
two of them bullet lists; a "time dilation" analogy explains the delay curves. (tsn/timesynchronization/clockdrift/doc/index.rst)

**visualizer/canvas/radiomediumactivity** (visualizer feature tour). No `literalinclude` at all:
the five or six relevant visualizer keys are pasted into `.. code-block:: none` blocks; no
`:align:`. Each configuration is a top-level section ("Multiple nodes", "Interfering signals")
holding network figure, key block, video, reading. Explains the animation physically in long
paragraphs (mean 55 words): "When there is a signal boundary (either at the beginning or the end
of a transmission) traveling on the scene, the simulation is slowed down". Video lead-in: "When
the simulation is run, this happens:" (visualizer/canvas/radiomediumactivity/doc/index.rst)

**visualizer/canvas/spectrum** (visualizer feature tour). One `-` section per figure type
(Probe, Spectrum Figure, Spectrogram, Power Density Map); each: what it shows, its parameters as
bullets, two reference images side by side in a grid table of `|substitution|` images, the
config's literalinclude, "Here is a video of the simulation:", then a narrated reading of the
video: "In the above video, the two hosts start transmitting at the same time." The `General`
config is shown once in the first feature section. 6 notes carry the tuning caveats ("Decrease the
pixmap density if the simulation is running slowly"). (visualizer/canvas/spectrum/doc/index.rst)

**wireless/analogmodel** (model catalogue). Three models, each `Overview` + `Example:`
subsection; examples are: network figure, "Here is the configuration in omnetpp.ini:" with the
whole 13-27-line config, "Here is a video of the simulation (...legend...):", video, reading.
Has the set's only figure caption ("An example of a signal with a complex spectrum but constant
in time"), a `.. code-block:: ini` example value, and the `.. include::` of coexistence's syntax
bullets. States which model to pick: "When a less complex model is adequate
in a showcase or tutorial, the unit disk model is used; when a more complex one is needed, the
dimensional is chosen." (wireless/analogmodel/doc/index.rst)

**general/pcaprecording** (tooling). `The model` is a parameter reference ending in "To
summarize: the :par:`moduleNamePatterns` parameter specifies which modules' outputs should be
captured." `The configuration` walks the network host by host with 1-5-line excerpts: "In
``host1``, we'll record 802.11 traffic on the ``wlan0`` interface:". Results pair a Qtenv
inspector shot with the same packet in Wireshark under label-style lead-ins: "TCP data, in
``ethHost1`` (sent from ``ethHost1`` to ``ethHost2``):". `:language: ini` listed first; no
`:align:`. (general/pcaprecording/doc/index.rst)

## 4. Verbatim templates (copied from wireless/txop/doc/index.rst; identical in all 11 modulo path)

Version and source-location lines (end of Goals):
```
| Verified with INET version: ``4.6``
| Source files location: `inet/showcases/wireless/txop <https://github.com/inet-framework/inet/tree/master/showcases/wireless/txop>`__
```

Sources line (after the last result, before Try It Yourself; 11 of 11):
```
Sources: :download:`omnetpp.ini <../omnetpp.ini>`, :download:`TxopShowcase.ned <../TxopShowcase.ned>`
```

Try It Yourself (byte-identical in 11 of 11 after substituting the showcase path):
```
Try It Yourself
---------------

If you already have INET and OMNeT++ installed, start the IDE by typing
``omnetpp``, import the INET project into the IDE, then navigate to the
``inet/showcases/wireless/txop`` folder in the `Project Explorer`. There, you can view
and edit the showcase files, run simulations, and analyze results.

Otherwise, there is an easy way to install INET and OMNeT++ using `opp_env
<https://omnetpp.org/opp_env>`__, and run the simulation interactively.
Ensure that ``opp_env`` is installed on your system, then execute:

.. code-block:: bash

    $ opp_env run inet-4.6 --init -w inet-workspace --install --build-modes=release --chdir \
       -c 'cd inet-4.6.*/showcases/wireless/txop && inet'

This command creates an ``inet-workspace`` directory, installs the appropriate
versions of INET and OMNeT++ within it, and launches the ``inet`` command in the
showcase directory for interactive simulation.

Alternatively, for a more hands-on experience, you can first set up the
workspace and then open an interactive shell:

.. code-block:: bash

    $ opp_env install --init -w inet-workspace --build-modes=release inet-4.6
    $ cd inet-workspace
    $ opp_env shell

Inside the shell, start the IDE by typing ``omnetpp``, import the INET project,
then start exploring.
```

Discussion (wording identical in 10 of 11; pcaprecording writes `` `this page <...>`__ ``):
```
Discussion
----------

Use `this <https://github.com/inet-framework/inet-showcases/issues/45>`__ page in the GitHub issue tracker for commenting on this showcase.
```
Link target: `inet-showcases/issues/N` in 9 of 11; `inet/discussions/N` in 2 of 11
(framepreemption 676, clockdrift 797).
