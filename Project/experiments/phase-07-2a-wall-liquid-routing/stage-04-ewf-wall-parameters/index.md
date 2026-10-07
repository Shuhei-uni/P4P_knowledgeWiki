# Stage 4 — EWF settings and wall parameters

| Item | Status / record |
| --- | --- |
| Human direction | 7 October 2026: retain Stage 3 as the startup-method reference; explore changed EWF settings and wall parameters |
| Stage 3 | Human is satisfied with the stage; retain its evidence and method; no new steady-film qualification claim |
| Completed first Stage 4 result | [Commercial steel roughness continuation](commercial-steel/results.md); N25815 → N29815 |
| Selected continuation | [Selected EWF mechanisms](realism-continuation/setup.md): loaded N29815 commercial-steel parent; +2000 bulk-and-film iterations, then +50 ms EWF only; aim for 15 microseconds |
| Completed retry | [Flow Momentum Coupling OFF result](realism-continuation/feedback-off/results.md); 4000 bulk updates and +50 ms EWF-only; N37149; film still filling |
| Continuation status | [Feedback-ON failures](realism-continuation/results.md); control recovered; feedback-OFF requested horizon complete |
| Completed setting sensitivity | Stripping OFF suppresses the four-step cycle but fails longer numerical checks; no tested OFF route retained. Stripping-ON / coupled-ON control continued +50 ms to N40483; peak Courant 0.07315; film still filling. [Results](setting-sensitivity/results.md); [research](setting-sensitivity/research.md). |
| Parent film limit / absorber audit | 0.3 m maximum film thickness at unchanged N40483; reaching it marks a run **UNREALISTIC**. The N40483 parent contact absorber has no direct EWF sink. [Configuration and drainage evidence](setting-sensitivity/film-limit.md). |
| Completed EWF-only drain | [Direct lower-film drain result](ewf-only-drain/results.md); native source proof and matched 15 ms screens PASS; ON current at N41483; direct sink 0.508790 kg; lower film 70.32% lower; bulk frozen; film still growing. |
| Selected long film development | [Native long-run design](ewf-only-drain/long-development/setup.md); +200,000 updates / +3 s from drain-ON N41483; full selected film physics; bulk frozen; laptop-independent native TUI. [Status](ewf-only-drain/long-development/results.md). |
| Scientific envelope | [Phase context](../CONTEXT.md) |
| Startup design | [Stage 4 setup](setup.md) |
| Result overview | [Stage 4 results](results.md) |
