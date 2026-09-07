# Andy's local source recovery snapshot — 8 September 2026

This branch preserves the code and text notes from Andy's uncommitted
`P4P_knowledgeWiki` checkout and the surrounding `P4P` workspace. It is a
historical recovery source, not the current project structure or run authority.

Continue shared development on `main` and short-lived topic branches in
[Shuhei-uni/P4P_knowledgeWiki](https://github.com/Shuhei-uni/P4P_knowledgeWiki).
The integration branch is `andy/unify-workspace-20260908`.

- Original local checkout: `Andy_Dev`, based on commit `3dd8209`.
- Shared main at reconciliation: `e4169e2` (6 September 2026).
- The separate Stage 4 checkout at `a0d1ed5` is already an ancestor of main.
- `Workspace/Code/` contains the loose calculation scripts and compact inputs.
- `Workspace/` also preserves the loose text notes and document-editing scripts.
- Local source files were copied as found; their scientific claims, old agent
  instructions, experiment IDs and absolute paths have not been upgraded.
- Andy's historical `08b`/`08c` enthalpy sweeps are different experiments from
  the same numbered IDs on the other research lane. Compare descriptive names,
  geometry, model and parent artifacts before reusing anything.

Credentials, virtual environments, caches, raw source papers, binary documents,
generated output and temporary working files are excluded. Andy retains the
original directories, a Git bundle, a working-tree patch, and a compressed
local backup with a SHA-256 inventory under `_reconciliation/2026-09-08/`.
Those private backups must remain local.

To recover a specific source without replacing the current tree, use
`git show origin/archive/andy-local-20260908:path/to/file` or browse this branch.
Do not merge this snapshot wholesale into main; the newer structure deliberately
retired the old wiki, numbered setup tree and campaign wrappers.
