# Recovery

Failure type matters more than the fact that something failed.

## Classify

- **Implementation failure** — wrong API path/order, build script error, missing
  output, transfer/path problem. The scientific experiment is **untested**.
- **Numerical failure** — divergence/FPE/non-viable method after the intended case
  was built correctly. This is evidence about the numerical route, not automatic
  falsification of the physical idea.
- **Scientific result** — a verified run produced interpretable evidence that
  supports, weakens, or distinguishes the hypothesis.

## Recover

For implementation failure, inspect the live state/error, repair the smallest
cause, recreate/restart from a clean parent when useful, and retry. If one
implementation route repeatedly fails, try a materially different verified route
before blocking it.

For numerical failure, change only the numerical factor needed to test viability
unless the phase question itself is about numerics. Preserve the original failed
attempt as evidence.

Reject or weaken a scientific idea only from interpretable scientific evidence,
not because code or case construction was faulty.

## Keep the log tiny

Record one line only for material events, for example:

`<setup> | <kind> | <change/error> -> <outcome>`

Do not create diary-style run logs. Git history, artifacts, `results.md`, and
the compact phase state carry the detail.

## Escalation

A blocker becomes external only when all reasonable in-scope recovery routes are
exhausted or a required fact/resource is genuinely unavailable. Continue other
useful in-scope work instead of waiting for a reply.
