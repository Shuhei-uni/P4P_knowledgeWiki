# Working together

Use [Shuhei-uni/P4P_knowledgeWiki](https://github.com/Shuhei-uni/P4P_knowledgeWiki)
as the shared repository. `main` is the combined, agreed version. Each person
uses a short-lived branch for one task, then a pull request into `main`.
This follows [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow).

## Set up once

Andy should use the `P4P_shared` folder created during reconciliation. On a
new computer, clone a fresh copy into an empty destination:

```bash
git clone https://github.com/Shuhei-uni/P4P_knowledgeWiki.git P4P_shared
cd P4P_shared
git config pull.ff only
git config push.default simple
git config fetch.prune true
git config merge.conflictstyle diff3
```

Check `git remote -v` points to the shared repo. Check `git config user.name`
and `git config user.email`; set them to your own commit identity if needed.
Authenticate with your own GitHub account. Both people need write access;
Andy's connected account `grtenSWE` had it at reconciliation.

For Python work on a new computer:

```bash
python3 -m venv PyAnsys/.venv
PyAnsys/.venv/bin/python -m pip install -r PyAnsys/requirements-minimal.txt
cp PyAnsys/.env.example PyAnsys/.env
```

Skip the final copy if `.env` already exists. Enter your own connection
settings locally; `.env` stays ignored. Follow the [PyAnsys guide](PyAnsys/README.md)
and [server profiles](PyAnsys/server-profiles/README.md) before connecting.
Matching server numbers do not establish matching machines or case identity.

## Start each task

Run `git status` first. Commit unfinished edits on their existing task branch
before switching; do not discard them to update main. With a clean tree:

```bash
git switch main
git pull --ff-only
git switch -c andy/describe-the-task
```

Shuhei can use `shuhei/describe-the-task`. Choose a new description each time.
Agree who owns a shared file while both people edit it. Start scientific work
at [Project/index.md](Project/index.md) and follow [AGENTS.md](AGENTS.md).

## Save and share

```bash
git status
git diff
git add path/to/changed-file
git diff --cached
git commit -m "Describe what changed and why"
git push -u origin HEAD
```

Open a pull request with **base `main`** and your task branch as the head.
Include relevant checks and let the other person review. Merge after it is
agreed. In GitHub Desktop the equivalent is Fetch/Pull → New Branch → Commit
→ Publish Branch → Create Pull Request.

If main changes while your branch is open, commit your edits, then:

```bash
git fetch origin
git merge origin/main
```

Resolve conflicts by keeping the intended contributions from both people,
run checks, commit the resolution, and push. `git merge --abort` returns to
the start of an in-progress merge. Avoid force pushes and whole-file
"ours/theirs" resolutions for scientific records.

After merging your pull request:

```bash
git switch main
git pull --ff-only
```

Start the next task on a new branch. Stop using `Andy_Dev` and the old Stage 4
branch for ongoing work; their histories remain available.

## Data, checks and main protection

Commit source code, compact inputs, selected experiment records and reusable
knowledge. Keep credentials, environments, raw PDFs, meshes/case-data pairs
and generated output local or in agreed private storage. See
[local data and recovery](LOCAL_DATA.md). Git does not back up ignored files.

The `repository-checks` GitHub workflow runs the offline tests, active Markdown
link check and calculation example on pull requests and main. It needs no
Fluent credentials. Run the offline checks from the repository root:

```bash
PyAnsys/.venv/bin/python -m unittest discover -s PyAnsys/tests
PyAnsys/.venv/bin/python scripts/check_stale_paths.py --fail-on-missing
git diff --check
```

The repository owner should protect `main` in Settings → Rules → Rulesets:
require a pull request, one approval, resolved conversations and the passing
`repository-checks` status; block force pushes and deletion. Apply this to administrators too
if both people want the same safeguards. Andy's connected account has write
access but lacks administration permission, so this owner setting was not
changed. See [GitHub's protection guide](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
