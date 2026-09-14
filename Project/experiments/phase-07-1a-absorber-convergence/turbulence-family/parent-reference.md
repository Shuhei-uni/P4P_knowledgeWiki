# Turbulence-family parent reference

## Selected parent

The first three queued turbulence packets will use the same complete paired
absorber state:

| Field | Value |
| --- | --- |
| Parent setup | P7-E5-CZ-ABSORB-COLD-RAMP11692 |
| Parent state | Active-1000 final case/data pair |
| Server reference | student@10.0.0.5 |
| Fluent version | 2025 R2 |
| Parent case | C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneAbsorberCold\20260910T135421Z\P7-E5-CZ-ABSORB-COLD-RAMP11692\P7-E5-CZ-ABSORB-COLD-RAMP11692-active1000.cas.h5 |
| Parent data | C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneAbsorberCold\20260910T135421Z\P7-E5-CZ-ABSORB-COLD-RAMP11692\P7-E5-CZ-ABSORB-COLD-RAMP11692-active1000.dat.h5 |
| Parent run paths | [P7-E5 cold-start run paths](../../../phase-07a-simplified-purnanto-liquid-removal/cell-zone-absorber-control-family/p7-e5-cz-absorb-cold-ramp11692/run-paths.yaml) |
| Parent results | [P7-E5 cold-start results](../../../phase-07a-simplified-purnanto-liquid-removal/cell-zone-absorber-control-family/p7-e5-cz-absorb-cold-ramp11692/results.md) |
| Execution manifest | PyAnsys/output/phase07_cz_absorb_cold/P7-E5-CZ-ABSORB-COLD-RAMP11692-student-20260910T135421Z-manifest.json |

## Parent evidence

The prior execution record reports:

- the exact E0-style initialized case/data pair was loaded before the
  absorber treatment;
- the existing mesh was split into the 3,794-cell
  p7-e5-lower-y010 zone;
- the lower phase-2 absorber and matched momentum-source tree were read back;
- the bottom remained a wall;
- direct phase-1 source and parent-zone sources remained off;
- the source ramp reached 116.92 kg/s;
- the final active-1000 pair was saved and reopened successfully.

The active-1000 state is intentionally selected rather than the later
continuation endpoint. The active-5000 continuation did not reach its declared
horizon and is not a valid parent for this family.

The child implementation must load this active-1000 pair without
reinitialization, patching, resetting, remeshing, resplitting, or restart-field
alteration. The only child delta before the first solve is the declared
turbulence setting.

## Parent identity limitation

The paired parent is proven by the prior execution manifest and run-path
record, and the files are available under the student runtime path. The
The current student session confirmed both active-1000 files exist at the
recorded paths using a read-only Fluent file-existence probe on 2026-09-11.
This is a presence check, not a checksum. Before mutation, fleet orchestration
must still load both files, read back the full parent state, save, and reopen
the prepared child.

The same read-only probe also confirmed the E0 initialized case/data pair
exists at the recorded OneDrive path on student.

The E0 initialized OneDrive pair used to create the absorber parent is also
available locally and has these hashes:

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| initialized.cas.h5 | 40,873,688 bytes | 4f894a9df391584953e42810421fa09d2aa251e7f6d73b3e600dd400a4cce3da |
| initialized.dat.h5 | 93,083,127 bytes | 6b6ccb6b0192ca98993eb3708f5a452a751b1d40bdfcc12a85499e9cefa98702 |

Those E0 files are provenance support, not substitutes for the selected
active-1000 absorber parent.
