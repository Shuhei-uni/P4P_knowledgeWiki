# Observation Order Dictionary

## Purpose

This dictionary gives the project reasoning sequence for comparisons. It does not replace setup lineage in `Setups/`; it explains why a particular setup-to-setup comparison matters and what decision it should inform.

| Order | Observation | Primary comparison | Controlled question | Current use | Next decision supported |
|---|---|---|---|---|---|
| `01` | inlet-loading family | `08b` vs `08c-v20p00` vs `08c-v32p14` | Does inlet loading/speed alter steam-line carryover? | directional carrier-flow observation | retain a low/reference/high loading family and repeat at a common acceptance window |
| `02` | DPM dispersion | `09a` vs `09b` | Does DPM tracking/dispersion treatment alter completed fine-droplet fates? | DPM uncertainty observation | retain stochastic dispersion as an explicit sensitivity, not an invisible default |
| `03` | global DPM interaction | `08b` vs `09c` | Does DPM source feedback change the carrier field? | early coupling-screening observation | make a matched one-way/two-way comparison only after the carrier field is mature |
| `04` | isolated/combined EWF mechanisms | `010V2` vs `010V2a/b/c/d` | Which wall-film mechanism changes the clean deposition control? | EWF mechanism-screening observation | quantify mechanisms separately before treating the combined branch as physical |
| `05` | global DPM + EWF | `010V2d` vs `010V2d-2` | What does global DPM source feedback add to the combined EWF state? | conditional local film/fate observation | restart from one matched parent checkpoint with only global interaction toggled |

## Relationship map

```text
inlet loading (01)
    -> deterministic/stochastic DPM interpretation (02)
    -> one-way/two-way DPM feedback (03)
    -> EWF deposition and isolated mechanisms (04)
    -> combined EWF plus global DPM feedback (05)
```

The map is a reasoning path, not a claim that every earlier numerical gate has already passed. A later observation may be exploratory while an earlier one remains unresolved.
