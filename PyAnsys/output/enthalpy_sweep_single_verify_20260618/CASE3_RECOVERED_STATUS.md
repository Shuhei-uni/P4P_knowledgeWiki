# Case 3 Recovered File Status

The recovered Case 3 files in this folder should be treated as unverified for
1500 completed iterations:

- `C:\Users\qtra338\Documents\enthalpy_sweep_single_verify_20260618\case_3_1520_1500_recovered.cas.h5`
- `C:\Users\qtra338\Documents\enthalpy_sweep_single_verify_20260618\case_3_1520_1500_recovered.dat.h5`

The Mac-side controller log for this run did not record `progress: 1500/1500`
for Case 3. It only captured early solver output before the controller lost
connection. Later logs reported `iteration_count: 1500`, but that value is
Fluent's current iteration/run setting and is not reliable proof that a
disconnected controller completed 1500 iterations.

If Fluent GUI reports this recovered case has only 100 iterations, trust the
GUI and do not use this recovered file as a 1500-iteration result.

The older Case 3 file in `C:\Users\qtra338\Documents\enthalpy_sweep` has log
evidence for `progress: 1500/1500` and final case/data writes:

- `C:\Users\qtra338\Documents\enthalpy_sweep\case_3_1520_1500.cas.h5`
- `C:\Users\qtra338\Documents\enthalpy_sweep\case_3_1520_1500.dat.h5`
