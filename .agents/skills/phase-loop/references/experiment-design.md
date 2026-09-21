# Experiment design and setup packet

Use this branch when selecting, shaping, screening, or formalising an experiment
inside an already recorded phase envelope. Design from the uncertainty and the
evidence needed to reduce it; do not start from an available parameter list.

## Reconstruct the comparison

Before proposing a new case, search `Project/` by physical mechanism, model,
boundary condition, numerical change, initialization, operating regime, and
intended observation. Classify the closest precedent as:

- `NEW` — no meaningful prior test;
- `PARTIAL REPEAT` — same family, but a material controlled delta remains;
- `REPLICATION` — same test repeated to check a concrete implementation or
  numerical difference; or
- `REDUNDANT` — existing evidence already answers the question.

A failed or partial predecessor is still evidence. State the exact delta and why
the retained evidence cannot already answer the new question. Prefer the closest
contrast or evidence repair over an unrelated new case.

## Design the smallest discriminating strategy

Discovery is a contrastive screen: choose the fewest cases that separate the
plausible mechanisms or explanations. Keep parents, invariants, analysis window,
and comparison basis comparable. State for every candidate what response would
make it worth deeper qualification and what response would point elsewhere.

Qualification works backward from a bounded intended statement. Record:

```text
question or falsifiable hypothesis
discovery basis and strongest competing explanation
controlled delta and frozen invariants
observation that would support, weaken, or leave the hypothesis ambiguous
run horizon and any continuation/restart window
required numerical and physical evidence
claim limit
```

Use a horizon that can show the behaviour the claim names. A short discovery
tail cannot establish a stationary, bounded, or durable response merely because
it looks favourable at its endpoint. When persistence matters, plan a later
window or a save/reopen continuation that could reveal a transient disguise.

## Design evidence before compute

For each planned core figure or table, record a stable ID and all of:

| Item | Specify before running |
| --- | --- |
| Question | Exact sub-question the artifact answers |
| Quantity | Field/report, units, sign, phase/zone/surface scope |
| Source | Monitor, report file, checkpoint, or derived metric |
| Comparison | Cases, parent/reference, window, and normalization |
| Reduction | Raw, final-window statistic, profile, contour, etc. |
| Instrumentation | What must be configured before the solve |
| Decision use | Observation that distinguishes explanations |

Use one scientific message per figure. A spatial claim needs a contour, vector,
or profile with a defined surface; an evolving claim normally needs native
iteration or physical-time coordinates. Preserve raw oscillation or drift when a
reduction is overlaid. If a quantity cannot be reconstructed from the final
case/data, require its report or monitor before the case is run.

Core evidence is usually 1–3 artifacts for discovery and 2–5 for deeper
qualification. The first should usually be the most direct answer to the phase
question, not a generic residual dashboard.

## Compile the setup packet

`setup.md` is the server-neutral scientific handoff. It should carry:

- phase/context path and exact parent/reference identity;
- intentional delta, frozen invariants, and initialization intent;
- run mode, planned horizon, analysis window, checkpoints, and durability need;
- required versus supporting evidence, including the core-figure plan;
- expected output identities and the claim limit; and
- working assumptions labelled separately from missing external facts.

Keep server placement and machine paths in the run artifact map, not in the
scientific comparison definition. A missing fact that materially determines the
answer should become a bounded sensitivity or an explicit limitation, never an
unlabelled default.
