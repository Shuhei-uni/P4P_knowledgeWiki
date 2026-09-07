# Local data and recovery

The shared source of truth is this repository's `main` branch. Andy's active
checkout is `P4P/P4P_shared`. The surrounding `P4P` folder remains a local
workspace and data store; do not initialize another Git repo around it.

## Where existing material went

| Original material in `P4P/` | Shared location or treatment |
|---|---|
| `P4P_friend_stage4` | Its `a0d1ed5` history is already in main; original checkout retained |
| `P4P_knowledgeWiki` on `Andy_Dev` | Source/text recovery snapshot and selected integration into the current structure; original dirty checkout retained |
| `Code/` | Maintained calculations and compact inputs copied into `PyAnsys/scripts/analysis/droplet_calculations/`; deprecated variants in recovery |
| `Project_Context.md`, text meeting notes, document-editing scripts | Historical copies under `Workspace/` in recovery; current scientific state remains in `Project/` |
| `Lit Review/`, Word/PowerPoint drafts | Original binaries retained locally and included in the private backup |
| `Literature/`, raw PDFs and large CFD imports | Local only; accessible through ignored `local-data/` links on Andy's Mac |
| `Separator_CFD/` | Earlier geometry/data repo retained; its Git history bundled locally; large payloads stay in place |
| `PyAnsys/output/`, temporary diagnostics, generated reports | Preserved locally and in the private backup; selected findings summarized in Project records |

The original `08b`/`08c` labels named different experiments across research
lanes. The [historical Andy index](Project/experiments/parallel-andy-studies/README.md)
records this distinction. Matching numbers do not establish case identity.

## Recover sources

The [recovery snapshot](https://github.com/Shuhei-uni/P4P_knowledgeWiki/tree/archive/andy-local-20260908)
contains 405 original source/text files plus a recovery README. Credentials,
binaries, raw papers, generated output, caches and environments are excluded.
It is a source archive, not a branch to merge wholesale into main.

```bash
git fetch origin
git show 'origin/archive/andy-local-20260908:Setup report/07n-resolved-brine-outlet-model-solver-screening.md'
```

Andy also has `_reconciliation/2026-09-08/` outside the active checkout:
complete Git bundles for both repos, the tracked-change patch, a compressed
backup of 2,178 local files and a SHA-256 inventory. The backup includes
private connection settings; keep it private. Large CFD directories and the
paper collection remain in place. Keep originals until the data has another
verified copy.

## Use data on another computer

Cloning restores code and notes, not ignored data. Restore required papers
to the paths described by the CFD wiki. Transfer required matching case/data
pairs through agreed private storage, verify their identity, and record the
actual paths in the selected experiment's `run-paths.yaml`.

The ignored `local-data/` links are a convenience for Andy's Mac, not portable
backups. Shared cloud storage for the loose historical data has not been
selected or configured by this migration.
