# E7 run paths

Latest interrupted recovery: `p7b-s40-t100-coupled-cfl20-nphase-resume-20260924T054531Z`. Job `PyAnsys/output/phase07b-convergence-investigation/e7/recovery-n0-retry1/job.yaml`; manifest `PyAnsys/output/p7b-s40-t100-coupled-cfl20-nphase-resume-20260924T054531Z/manifest.json`. Reuses unchanged verified live N0, without reload or initialization. Unique local-PC checkpoint/report paths use this recovery prefix. Its controller exited after a transport failure; live solver progress is unknown. Do not resume/reload until API reconciliation.

Original build: `p7b-s40-t100-coupled-cfl20-nphase-20260924T053024Z`; job `PyAnsys/output/phase07b-convergence-investigation/e7/job.yaml`. Preserved implementation failure at the diagnostic schema comparator before any solve. Initial/prepared paired reopens passed. Retired first N0 recovery `p7b-s40-t100-coupled-cfl20-nphase-resume-20260924T054356Z` stopped at report-path representation assertion without solve or mutation; read-only API confirmed idle N0. Never relaunch either job.

Fresh scientific parent is original clean N0. E6 final is the comparison control and was preserved before replacement. Phase-state owns the active controller/disposition.
