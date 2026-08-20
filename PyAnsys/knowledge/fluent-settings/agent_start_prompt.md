# Agent Start Prompt: Fluent Automation

Treat Fluent as a dependency-ordered live state machine.

Before setting a dependency-sensitive value:

1. confirm the parent/model/object is active;
2. reacquire after parent/type/object changes;
3. inspect active children, commands, and allowed values;
4. set the value;
5. read it back.

Canonical pattern:

```text
enable/create parent -> reacquire -> inspect -> set -> read back
```

Use `orders/global_setup_order.yaml`, the relevant model `trees/*.md` / `orders/*.yaml`, and `indices/path_dependency_index.json`. If those do not match the live session, inspect Fluent and consult current official documentation rather than forcing an old path.

Keep three responsibilities separate:

1. setup building;
2. run planning;
3. run execution.

Choose the run mode deliberately:

- **TUI** — one prepared case, uninterrupted run;
- **journal** — multiple independent/fixed cases or stages;
- **agent-owned Python** — staged/adaptive workflow where intermediate evidence controls what happens next.

For agent-owned Python, make the workflow recoverable and provide the exact command plus supervisor/resume instructions.

Use `native_run_and_autosave.md` for run execution and recovery details.

Do not rerun a whole setup because one deep setting fails. Isolate the failure, classify it, use TUI fallback only after inspecting the Settings API path, and record reusable successful paths or order dependencies.
