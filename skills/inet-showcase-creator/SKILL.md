---
name: inet-showcase-creator
description: |
  Plan and create new INET Framework showcases under the inet/showcases/ directory.
  Use when asked to add a new showcase simulation study and its Sphinx documentation page.
  Always start with discovery and planning; do not create files until user confirms.
---

# Workflow

## Phase 0: Discover existing patterns (before asking questions)

1. Use `inet-framework/inet` deepwiki MCP for INET-specific documentation if needed.
2. Check the destination directory for existing simulation model. Explore and
    analyze it. Use it as a template or starting point.
3. Find the best matching existing showcase as template:
   - `grep_search` or `find_by_name` in `showcases/` for similar features
   - Read its `doc/index.rst`, `omnetpp.ini`, and `.ned` files
4. Check the relevant category `index.rst` for toctree structure.
5. Analyze the `results/` directory for existing results. Check what kind of data is available. Possibly ask the user later to provide them if it is needed for better end-result. 

## Phase 1: Clarify scope (do not create files yet)

Ask only what's essential. Infer defaults from existing model and template showcase.

**Core questions:**
- **Source**: What is the source of the showcase? If a base model is not present, what other example should it be based on?
- **Goal**: What feature is demonstrated? What claim should the showcase prove?
- **Category**: Where does it belong?
- **Detail**: 
  - How much the underlying network standards should be detailed (i.e. generic, non-INET specific info)? (on the level of 0-10)
  - How much detail should be given about how to actually configure this simulation scenario (i.e. INET specific configuration info)? (on the level of 0-10)
  - How much detail about the actual implementation in INET should be given (i.e. info from c++ files)? (on the level of 0-10)

**Ask only if unclear from context:**
- Network topology size/complexity (if not yet specified by the user)
- Expected outputs (plots, pcap, metrics)
- Linux-only requirements (namespaces, `RealTimeScheduler`, `CAP_SYS_ADMIN`)
- Multiple ini configs needed

**Iterate with the user until you are sure about the scope and the basic outline of the showcase.**
- ask the user to generate new result files if needed (like new diagrams, logs, pcap files, eventlogs, statistics, screenshots, screen video captures etc.)
- incorporate the new results into the plan

**Summarize before proceeding:**
- The general scope and the planned outline and claims of the showcase
- Final path: `showcases/<category>/<showcaseName>/`
- Which `index.rst` to update
- Files to create

Wait for explicit user confirmation (until the user switches to code mode)

## Phase 2: Implement (after confirmation)

### 2.1 Directory structure

Create `showcases/<category>/<showcaseName>/` and `doc/` subdirectory (if not yet present)

### 2.2 Simulation files

**Required:**
- `omnetpp.ini` with `sim-time-limit`, clear `[Config ...]` sections
- `.ned` file(s) with package `inet.showcases.<category>.<showcaseName>`
- you can modify existing files to achieve the goal of the showcase inside the new showcase directory (but do not delete or modify files that are not part of the showcase)

**Conventions:**
- Network name: `<Feature>Showcase` (e.g., `HandoverShowcase`)
- Use `extends = ...` for config inheritance
- Add `description = "..."` to configs
- When literalincluding network files, only include the relevant parts (e.g. no license header or package and import statements))
- Don't use image captions but describe the image either before or after the image
- Network screenshot: use `area="module_rectangle"` and `margin=5`
- Most of the time we don't need :width: 100% for figures

### 2.3 Documentation page

Create `doc/index.rst` following this structure:

```rst
Title
=====

Goals
-----
[What is demonstrated and why]

| Verified with INET version: ``X.Y``
| Source files location: `inet/showcases/... <GitHub URL>`__

The Model
---------
[Explanation of concepts and approach]

Configuration
~~~~~~~~~~~~~
[Use .. literalinclude:: ../omnetpp.ini blocks]

Results
-------
[Observations, screenshots, plots]

Sources: :download:`omnetpp.ini <../omnetpp.ini>`, :download:`*.ned <../*.ned>`

Try It Yourself
---------------
[Standard opp_env instructions - copy from template]

Discussion
----------
Use `this page <GitHub issue URL>`__ in the GitHub issue tracker for commenting on this showcase.
```

### 2.4 Wire into toctree

Add entry to appropriate `index.rst`:
- Simple category: `showcases/<category>/index.rst` → add `<name>/doc/index`
- Nested (TSN): `showcases/tsn/<subcategory>/index.rst` → add `<name>/doc/index`
- New subcategory: may require creating intermediate `index.rst` and wiring to parent

### 2.5 Verify

- NED `package` matches folder path
- All `:download:` links reference existing files
- No broken `:doc:` or `:ned:` references

# Output

Provide:
- Final showcase path
- List of created/modified files
- Run command: `inet` (or `inet -c ConfigName` if multiple configs)

Do not modify files outside the new showcase except required `index.rst` wiring.

# Documentation Writing Principles

- Goals should answer "why does this feature exist?" before "what does it do?" — structure as: problem → solution → what we demonstrate
- Separate domain knowledge (the protocol/standard) from tool knowledge (INET configuration) — use an "About X" section for protocol background before The Model, and an "X in INET" subsection inside The Model for module/parameter overview
- Never reference a concept before defining it — follow dependency order (e.g. define "lease" before describing the DORA exchange that grants one)
- Explain the *why* behind each mechanism, not just the *what* (e.g. why Renewing uses unicast but Rebinding uses broadcast)
- When a parameter appears in multiple places, the mechanism must be described the same way, not just the outcome (e.g. don't describe `numReservedAddresses` differently in the module overview vs the results section)
- Abstract models (state machines, protocol layers) need explicit grounding in previously described concrete steps
- For each config/scenario, identify the primary reader question and answer it explicitly in the Results section (e.g. "does the client get the same IP after reboot?")
