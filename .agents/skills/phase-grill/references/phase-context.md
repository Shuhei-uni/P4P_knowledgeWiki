# Phase `CONTEXT.md` schema

Create one current planning record at
`Project/experiments/<phase>/CONTEXT.md` for an active or newly framed phase.
It records the human-approved planning state, not a verbatim transcript or run
chronology. Git history preserves superseded wording.

```md
# Phase Context — <phase name>

## Status

- **Planning state:** phase framing | screening design | screening active |
  qualification candidate selected | human decision required
- **Last human review:** YYYY-MM-DD
- **Experiment-selection authority:** human-approved-context-only
- **Current decision:** [one sentence]

## Human thinking

### Current intent

[Concise attributed synthesis of the human's goal, intuitions, worries, and
priorities.]

### Ideas raised by the human

| ID | Human idea | Why it seems worth considering | Status |
| --- | --- | --- | --- |
| H1 | ... | ... | exploring / selected / deferred / rejected |

### Constraints expressed by the human

- [...]

## Evidence anchors

- **Observed:** [Project evidence link and supported observation]
- **Reported:** [reusable source link when relevant]
- **Inferred:** [reasoning and basis]
- **Assumed:** [temporary, bounded condition]
- **Missing Info:** [human-owned unresolved fact]

## Phase contract

### Phase question

> [Human-confirmed question.]

### Scope, invariants, and claim limit

- **In scope:** [...]
- **Out of scope:** [...]
- **Must remain fixed:** [...]
- **Claim limit:** [...]

### Useful evidence standard

[What outcome/evidence makes the phase worthwhile without predicting it.]

## Candidate experiment pool

| ID | Origin | Controlled delta | Screening question | Required evidence | Artifact/rejection signal | Human status |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | H1 — human idea | ... | ... | ... | ... | proposed / approved / rejected |

## Approved screening campaign

| Screen ID | Candidate | Parent/reference | Delta | Invariants | Short horizon | Core evidence | Gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | E1 | ... | ... | ... | ... | ... | G1 |

## Decision gates

### G1 — <name>

- **Evidence required:** [...]
- **Decision condition:** [...]
- **Allowed next action:** [named approved path, rejection, or return]
- **Not established by this screen:** [...]
- **Return to human when:** [...]

## Conditional qualification paths

### Q1 — <name>

- **Triggered only by:** G1 condition [...]
- **Hypothesis:** [...]
- **Competing explanation:** [...]
- **Long-run comparison:** [...]
- **Intended claim form:** [...]
- **Required qualification evidence and horizon:** [...]
- **Further human review before `setup.md`:** yes | no

## Human locks and handoff rules

- [Exact decision/fact the loop may not self-authorize.]
- `scientific-phase-loop` executes only approved context items and evaluates
  declared gates. It returns to the human for a new candidate, changed purpose,
  ambiguous gate, or unplanned observation.
```
