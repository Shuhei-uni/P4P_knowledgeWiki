---
name: fluent-manual-researcher
description: Research uncertain Fluent semantics or prerequisites in the version-matched official manual, ground the implementation through MCP, and prove an authorized recipe by readback and save/reopen.
---

# Fluent manual researcher

Resolve a specific configuration uncertainty, not the experiment's scientific
direction. Use [MCP integration](../fluent-live-inspection/mcp-integration.md) for
tool routing and session policy. Start with `fluent-live-inspection` when the
question is only an object/path/value lookup.

For decision support, follow [focused lookup](../references/focused-lookup.md):
a focused subagent receives one target-state question, decision context, exact
Fluent/case fingerprint and the fact that could change the decision. A lookup
subagent does not delegate recursively. The parent retains selection authority.

## Trigger and scope

Use for unclear model meaning, prerequisites, activation order, phase-pair/domain
scope, version-dependent options, persistence, or an unresolved automation path.
A known live path does not prove its scientific suitability. Do not mutate a
running/important parent merely to investigate an unfamiliar setting.

## Evidence order

1. Version-matched official Fluent User's Guide for semantics and prerequisites.
2. Its screenshots for panel structure and visible controls, not recommendations.
3. Matching PyFluent documentation for candidate Settings/API paths.
4. MCP live descriptors/state for what exists in this exact session.
5. Compatible proven repository code as a domain pattern, never path authority.
6. A version-pinned TUI candidate only under the explicit approval policy.

Separate what a screenshot shows, what the manual recommends, and what the
approved experiment requires. Cite sections/pages and distinguish Reported,
Inferred, Assumed and Missing Info. A default is not a justified model choice.

## Workflow

### 1. Fingerprint and state the question

Record Fluent/PyFluent versions, solver mode/dimension/precision where relevant,
exact parent identity, active models, phase identities, materials, object/boundary
types and intended state. Missing identity stays missing. State the target
configuration in physical/model terms before asking for a Python attribute.

### 2. Build the manual state checklist

Extract prerequisites, required/optional controls, ordering, restrictions, default
or recommended choices, phase/zone scope and documented persistence implications.
Classify each choice as `experiment-specified`, `manual-required`, `manual-default`,
`candidate` or `unknown`. Never silently promote a default/candidate to an approved
scientific setting. Return missing scientific decisions to the calling workflow.

### 3. Ground the implementation through MCP

Use `find_api`/`get_help` for candidate paths, then `describe_path`, named-object
and template tools, allowed values and `get_state` for the exact live branch.
Reinspect after every model, type, phase or object change. Existing recipes are
candidates until the current fingerprint and live state support them.

Do not add a crawler, use `dir()` as live authority, or repeatedly invent paths
when the uncertainty is semantic. Missing/inactive/truncated probes are not proof
that a requested configuration exists or that an absent field equals zero.

### 4. Prove only an authorized recoverable child

Receive explicit test scope and ownership before mutation. Preserve required
recovery and use an owned, still-running Fluent session. Through `validate_code`
and `run_code`, apply the smallest dependency-ordered sequence: approved parent
change → reacquire → inspect child/options → approved child change → independent
readback. Stop dependent actions on mismatch or missing proof.

A research-only brief grants no mutation, initialization, solve or save authority.
Return the documented candidate and its unproved conditions rather than conducting
an unrequested live test. Only a fully proved recipe earns `VERIFIED_RECIPE`.

### 5. Fallback is a separately approved exception

A TUI/journal path requires explicit human approval for that run, a documented
matching-version command family, evidence that the MCP/Settings route is inadequate,
a reviewed worker, recoverable-child testing, independent readback and save/reopen.
Researching a command, an autonomous-loop lease or passing an AST precheck does
not grant that approval. Never change the MCP sandbox or expose forbidden lifecycle
operations to make a fallback work. If unavailable, return `RESEARCH_BLOCKED` and
continue another authorized lane through the parent workflow.

### 6. Save/reopen proof

Audit the manual state checklist; save the authorized child (paired case/data
when its state requires both); verify the exact files; reopen in an owned,
still-running session; reacquire and repeat critical readback. Protect the source
pair. A fresh reopen is not permission to restart or launch Fluent.

A setter return, MCP report or matching broad snapshot alone is insufficient.
Record requested versus observed values, pre/post-save audits and exact artifacts.

## Output contract

Return `VERIFIED_RECIPE` only after live mutation, independent readback and
save/reopen proof. Keep the existing handoff fields:

```yaml
status: VERIFIED_RECIPE
fingerprint: {}
research_question: ...
manual_authority:
  section: ...
  url: ...
  screenshot_evidence: []
manual_state_checklist: []
scientific_classification:
  experiment_specified: []
  manual_required: []
  manual_defaults: []
  candidates_requiring_scientific_choice: []
verified_recipe:
  strategy: settings-api
  dependency_order: []
  operations: []
verification:
  pre_save_readback: pass
  saved_case: ...
  fresh_reopen: pass
  post_reopen_readback: pass
limitations: []
```

Record MCP execution evidence with the recipe; approved fallback strategies may
be `tui` or `mixed`, with approval and capability-gap evidence. The result proves
configuration mechanics, not physical accuracy or model selection.

Otherwise return `RESEARCH_BLOCKED`: exact unproved state/fingerprint, manual
findings, MCP queries, authorized attempts (or none), last verified state, why
proof is missing, bounded cause and smallest permissible next action. A read-only
research result may still help the parent even when live verification is blocked.
Return control to the caller; do not design a new phase or production run.
