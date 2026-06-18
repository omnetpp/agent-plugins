# New Simulation Platform — Plan

## Core ideas
- **You ask a question; the platform finds the answer.** Users want to *simulate to get an answer*,
  not to write code. A model and its code are just artifacts the system may or may not produce on the
  way to the answer — like interpreting vs. compiling an expression, the route doesn't matter to the
  person who wants the result. The platform knows the question being asked and works toward it:
  combining existing models, tools, and components, writing new ones when needed, running
  simulations, and analyzing results.
- **The AI is the central component — the driving force.** Not one feature among many: the AI runs
  the platform. It controls and combines the tools, uses the platform's features, builds and runs
  models, and works toward the user's goal. Everything else — engine, tools, libraries, UI — exists
  for the AI to use. Built around AI agents from the start, not bolted on.
- **One consistent thread** (`question → model → config → run → results → answer`). The platform
  keeps these consistent with each other, so changing one updates the rest. The answer — not the
  code — is the deliverable.
- **The AI works inside the simulation, not just around it.** It can read and change the state of a
  running simulation and see the event/causality history — not only start a run and read a summary.
  It builds models from existing, tested components instead of generating everything from scratch.
- **Secret by design.** Anything we expose, the next generation of AI learns from — so we expose as
  little as possible. The primitives, the ways they combine, the ways they abstract, and the tools
  the agents use are kept secret. White-box to our own agents inside; black-box to everyone outside.

## Keeping our value as AI improves
This is the core of the plan, and it has to be built into the platform — not bolted on as a license.

**The threat.** Each new AI generation trains on what already exists. Anything we expose — source
code above all, but also docs, examples, even clean input→output behavior — becomes training data,
and the next model reproduces it. Whatever we publish, we hand to our future competitor. **So the
source cannot be open**: open-sourcing the platform would directly teach the next AI what makes us good.

**The principle: expose as little as possible.** Keep secret, as much as we can:
- the **primitives** — the basic building blocks the agents work with;
- the **means of combination** — how primitives are put together into working models;
- the **means of abstraction** — how higher-level models and behavior are built from lower ones;
- the **tools** the agents use to build, run, and analyze.
These are the source of our expressive power, so they are exactly what we protect.

**How it's built in.**
- **White-box inside, black-box outside.** Our agents run behind the boundary with full access to
  the secret machinery; users and their AIs see a thin interface and the results, not the mechanisms.
- **Hosted, or shipped as a sealed binary.** The secret parts run on our servers, or as a hardened
  binary on the customer's hardware that can't practically be reverse-engineered — never as source or
  in any readable form. No open source. This lets even air-gapped or secret customers run it with us
  out of the loop, without the value leaking.
- **No copyleft (GPL) code, anywhere.** Copyleft would legally force us to publish our source —
  fatal to all of the above; **AGPL is worst**, since it triggers even for a hosted service. Zero
  GPL/AGPL (and no statically-linked LGPL) in the system; audit every dependency and component.
- **Show results, not methods.** Publish validation evidence and benchmark numbers so people trust
  it, while keeping the components, tools, and methods that produced them secret.
- **Limit leakage.** Reveal less through the interface; rate-limit and watch for distillation
  (harvesting input→output pairs to train a copy); terms that forbid training on our output.
- **What AI makes cheap** (so it isn't our value): text-to-model, glue code, simple analysis
  scripts, the "describe → run → summarize" loop.

## Open use, closed source — the reversal from OMNeT++
OMNeT++ is open source, and the analysis treated that openness as an advantage. **We deliberately
reverse it** — the source stays closed (see above). But openness gave OMNeT++ two real benefits, and
we keep both, without giving away the source:

- **Free for academia → kept, as free *use*, not free *source*.** OMNeT++ conflated the two; we
  separate them. Academic and non-commercial users get the platform for free (hosted, use-only), so
  we keep the adoption, credibility, and trained-up user base — without handing the next AI our code.
- **Combining existing models with new ones → kept, as a service capability.** Mixing validated
  library models with your own newly-written components is central, and stays. What's secret is the
  *machinery* of combination and abstraction, not the *ability* to combine: the user combines by
  asking, and the platform wires it up behind the boundary. Already-public models (INET, ns-3, …) can
  still be imported and mixed in — they are public anyway; our value is in how we combine, abstract,
  and validate them, which stays secret.

Net: **anyone can use it; no one can read or copy how it works.**

## What the platform does
Given a question, the AI drives the whole process to an answer — the user doesn't have to drive every
step, but is a **partner in it, not a bystander**. The AI works **iteratively and collaboratively**,
checking in on the decisions that matter — key design choices, agreeing on *what* is being built and
on *how* it will be validated and tested — and handling the routine itself. The model/code is produced
only as a means to the answer. Throughout, the AI keeps a working understanding of everything involved
— the user's goals, the domain documentation (IEEE, RFC, …), the model source, its verification and
validation, the test framework, the configuration, and the results — drawing conclusions, correcting
course when something is wrong, and reporting interim findings as it goes, until the question is
answered.

- **Understand the documentation** — read and apply the domain standards and specs (IEEE, RFC, …) the
  model must follow.
- **Build models** — assemble from tested component libraries, and write new components only when
  needed; the model/code is an artifact on the way to the answer, not the goal.
- **Validate and verify** — check the model is built right and is the right model (see V&V); don't
  trust generation.
- **Regression-test automatically** — re-run the test framework's reference tests whenever models or
  components change, to catch breakage early.
- **Configure runs** — network topologies, parameterization, scenarios, parameter studies, and
  experiments, from the question.
- **Run** — on a laptop or in the cloud; the AI can also inspect and control a run while it goes
  (read/change state, step, set breakpoints), not just start and wait.
- **Analyze** — query the result data (scalar and vector), compute aggregates, generate plots, and
  trace the event history to answer "why did X happen?" — real analysis, not a text summary.
- **Draw conclusions** — turn the analysis into an answer to the question, with how confident it is.
- **Document** — a domain-specific agent writes and maintains the docs.

## Main dimensions
- **Engine:** from discrete-event to dynamic systems — continuous (ODE/DAE), hybrid, agent-based,
  system dynamics — behind one engine API that can host **multiple kernels at once** (an existing
  wrapped kernel and a new one side by side), not a single fixed kernel.
- **Interface:** the UI is generated automatically for the task instead of a fixed GUI; includes a
  shared 2D/3D view the AI and the user can both point at and control (highlight a node, replay).
- **Running it:** one API for the AI, same on a laptop or as a headless (no-GUI) cloud service (job
  queue, many workers, results in storage); a shared test suite keeps them consistent. The valuable
  parts never appear in readable form — they run on our servers, or ship as a **sealed binary** the
  customer runs on their own (even air-gapped) hardware, hardened against reverse engineering and
  needing no phone-home, so they can use the system with us out of the loop.
- **Licensing:** closed source, commercial — delivered as a hosted service or a sealed on-prem
  binary; free *use* (not source) for academia. See *Keeping our value as AI improves*.

## AI/agent architecture
- One versioned set of tools (an MCP-style API) is how the AI talks to the engine(s): build, inspect,
  run-control, results, event trace, experiments.
- The secret parts — primitives, means of combination and abstraction, and the tool internals — live
  on our side of the boundary. Our agents use them in full; the external interface is deliberately
  thin and reveals as little as possible.
- The AI inspects a live run through those tools, plus a sandboxed way to run its own code against
  the live model for questions the fixed tools don't cover.
- One coordinating agent plus specialists (modeling, configuration, running, analysis, docs) that
  share memory.

## Checking models are correct (V&V)
The most important part: if the AI builds the models, we have to check they are right. Make it a
required step the agents run, not an afterthought.

- **Did we build the model right?** Don't trust generation — build, then type/parameter-check and
  dry-run before saying it works. Check structure (units, conservation laws, interfaces,
  well-posedness) and numerics (convergence, solver tolerance, step-size independence). Have another
  agent review it. Run regression against reference scenarios. Build from tested components.
- **Did we build the right model?** Compare against real data, analytical solutions, and trusted
  reference simulators. Do sensitivity and sanity checks. Have a domain expert or specialist agent
  review it. Give results error bars, not just numbers.
- **Reproducibility and record-keeping.** Record what the agent changed, ran, and concluded; make
  runs repeatable from the same inputs and seed; attach a validation status to each result; sandbox
  and limit what the tools can do; reuse per-domain test suites; let a human approve results for
  important uses.

## Other dimensions
- **Component libraries** — reusable, tested components agents can find and combine; a place to
  share third-party ones.
- **Interop and co-simulation** — import existing models (OMNeT++, ns-3, MATLAB), support standards
  (FMI/FMU), couple different simulators. Matters for adoption.
- **Goal-driven runs** — give a goal, the AI proposes configs, runs a batch, looks at results, and
  iterates; fit parameters to data; use ML approximations to run faster.
- **Digital twins / real-time** — connect to live systems and data.
- **Multi-user** — shared workspaces; keep a team's models and knowledge.
- **Debugging and explanation** — use the event history/causality as a tool; debug both the
  simulation and the agents; explain results in domain terms.
- **Resource limits** — cap AI and compute usage; quotas; show costs.
- **Protecting the user's models and data** — keep their proprietary models and data private and
  isolated; for sensitive or air-gapped work, ship a **sealed binary** they run on their own hardware,
  so no data ever leaves their site and we are not in the loop. (Protecting *our* IP is covered above
  in *Keeping our value as AI improves*.)

## Licensing & access
What it provides: get answers from simulation faster — including for people who aren't simulation
experts — with results you can trust.

Who uses it: researchers and students; individual engineers and consultants; industry teams
(telecom, automotive, aerospace, energy, manufacturing).

Closed source, delivered as a hosted service:
- **Commercial license** for paid/commercial use. The platform is never shipped as source; the
  valuable parts (secret primitives/combinations/abstractions, tested libraries, domain agents,
  accumulated data) run on our servers or as a sealed, non-reverse-engineerable binary on the
  customer's hardware.
- **Free for academia / non-commercial use** — by design, to keep the adoption and credibility
  OMNeT++ got from being free. Free *use*, never source; with limits and terms that forbid training
  on our output. (We accept that use leaks some behavior; the source and machinery never leak.)
- **The cost of "free" is real.** Hosting free academic use can be expensive. Options: run it on
  academic infrastructure, or have academic users pay only for the compute they use (e.g. their own
  AWS instance). *Tension:* if a user can pay for AWS anyway, the free-software pull weakens — paying
  for a commercial license isn't far off. So "free" mainly works when hosting is genuinely free to the
  user (subsidized or on academic infrastructure).
- **On-prem / air-gapped as a sealed binary** for customers who must run on their own or secret
  hardware — hardened against reverse engineering, no phone-home, used with us out of the loop. (Or
  single-tenant isolation in our cloud if they prefer a managed option.)
- Paid support optional later.

## Decisions
- **Scope:** general dynamic-systems platform from the start, not just communication systems.
- **Question-first, not code-first:** the user's deliverable is the answer to their question; any
  model or code is an internal artifact, produced only when it helps reach the answer.
- **Engine:** no need to choose between old and new — the engine API supports **both an existing
  wrapped kernel and a new kernel at the same time**, behind one interface. Use whichever fits a given
  task or paradigm; add a new kernel without dropping the old one. (Cost guides *where to invest*, not
  a yes/no switch.)
- **Starting point:** wrap OMNeT++ 6.4 as the first engine — it already has the in-kernel MCP server,
  inside-the-run inspection, tested libraries (INET/Simu5G), and reproducibility. A new kernel can be
  added later behind the same API and run alongside it. The base kernel is already public; our AI
  layer on top (primitives, combinations, abstractions, tools) stays closed. **Caveat:** OMNeT++ contains GPL parts (found recently) that must
  be removed, replaced, or isolated before we can ship a closed product built on it.
- **Closed source by design — a deliberate reversal of OMNeT++'s openness.** We do not open-source
  the platform — the next generation of AI would learn from it and erode our value. Keep secret, as
  much as possible, the primitives, the means of combination and abstraction, and the tools. But keep
  the two benefits openness gave OMNeT++ — **free academic use** and **combining existing models with
  new ones** — delivered as a hosted service — or a sealed, non-reverse-engineerable binary for on-prem/air-gapped
  use — not as source (see *Open use, closed source*).

## Development stages
Each stage finishes when it hits its goal, not on a date. Secrecy is built in from Stage 0: nothing
is open-sourced, and the secret layer stays server-side throughout.

- **Stage 0 — Thin end-to-end version.** Smallest full loop (ask a question → model → configure →
  run → analyze → answer) with agents driving, on top of a wrapped engine (most likely OMNeT++'s
  in-kernel MCP). Demo: answer a real question (e.g. debug a run) by chatting. Result: the loop
  works; first real numbers on integration cost.
- **Stage 1 — Engine API (multiple kernels).** Define the engine API so it can host more than one
  kind of simulation *and* more than one kernel behind the same interface; prove it by running the
  wrapped existing kernel and a second engine side by side. Result: no forced old-vs-new choice;
  "general" shown across at least two kinds, and the API proven to host multiple kernels at once.
- **Stage 2 — Fill out the workflow.** Make each step actually good: build from tested libraries
  (with the checking loop), goal-driven runs, real analysis tools; keep the question and the
  model/config in sync. Result: someone can get real answers end to end.
- **Stage 3 — Correctness and components.** Reproducibility, record-keeping, safety; tested
  component libraries; interop/co-sim; a benchmark vs. the wrapper tools. Result: answers you can
  trust, models you can reuse.
- **Stage 4 — Scale and release.** Headless cloud service (queue, workers, storage); shared 2D/3D
  view; automatic UI; multi-user; then release as a closed, hosted product under a commercial
  license. Result: from internal tool to released product.

## Risks
- **Code execution safety** → sandbox, limit what tools can do, no host access; off by default on
  shared cloud.
- **AI builds invalid models** → never trust generation; always type-check, validate, and dry-run
  before claiming success.
- **Cloud cost** → quotas, hard caps on batch size, cheap/auto-scaling workers, show costs.
- **Laptop vs. cloud drift** → one API plus a shared test suite both must pass.
- **Doing too much too soon** → strengthen the hard-to-copy parts first; cloud scale-out only after
  the local loop works.
- **Protecting the shipped binary** → a sealed binary on the customer's hardware is the hardest case
  to protect; invest heavily in anti-reverse-engineering (obfuscation, tamper-resistance,
  hardware-binding/attestation). This is the central risk of on-prem delivery.
- **GPL / copyleft contamination** → one GPL dependency can force source disclosure and break the
  whole model. Audit all code and dependencies and make license-scanning part of the build; OMNeT++
  already has GPL parts (found recently) that must be excised, replaced, or isolated before we wrap it.
- **Upfront investment, know-how, and maintenance** → building and running a hosted system needs real
  investment and hosted-application expertise. AI-assisted development lowers the barrier but doesn't
  remove it; consider a **separate startup** to tackle this rather than building inside the current
  company.
