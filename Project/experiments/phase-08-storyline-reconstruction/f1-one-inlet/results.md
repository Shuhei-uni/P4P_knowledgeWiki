# F1 26.81 m/s base preparation

## Artifact and provenance

On `student`, Fluent 2025 R2 Student Edition loaded the Phase 7.2A Family E0 prepared case `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase72A\FamilyE\E0\20260922T115500Z\P72A-E0-prepared.cas.h5` (SHA-256 `1c5b1a5f5e68fcc6ff7248b50f6df83e788363faf7492315da42960fbce3e9f5`). The saved F1 pair is:

- Case: `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\F1\F1-mixed-26p81-base.cas.h5` (SHA-256 `653b5e9d0f95886ab6a1ee20787b4e97d25f8c63027c375969ef6073460d770c`).
- Data: `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\F1\F1-mixed-26p81-base.dat.h5` (SHA-256 `e8c12cedd721b56143077ffa3ecb11965538f5d494fa4c991bda5a7533d8be6f`).

Machine builder: [`build_phase8_f1_from_p72a_e0.py`](../../../../PyAnsys/scripts/setup/build_phase8_f1_from_p72a_e0.py). [Readback receipt](../../../../PyAnsys/output/phase8_f1_base_20260926.json).

## Verified F1 setup

The child retained the Phase 7.2A `60,964`-cell geometry and its two fluid zones, but sources are disabled in both zones for all phases. The absorber partition is geometrically present; it removes no mass or momentum. The mesh check passed. The `bottom` remains a wall, `steamoutlet` a pressure outlet, EWF off, roughness zero, DPM interaction off, and all six inherited injections removed. The Phase 7 report definitions, report files, and absorber expressions were removed.

The live inlet areas were `0.0048899165 m²` (`liquidinlet`) and `0.51928608 m²` (`steaminlet`). With the retained phase densities (`5.79743385` and `881.21087646 kg/m³`) and 1600 kJ/kg mass proportion, the read-back total feeds are `80.70292372 kg/s` vapor and `116.93872650 kg/s` liquid, giving the nominal combined volumetric speed `26.81 m/s`. Both phases were apportioned to each face by its area. Coupled pressure–velocity with steady Global Time Step remained from the Phase 7.2A parent. A fresh Hybrid field was initialized; the parent data field was not carried over. Case and data reopened with the same critical readbacks.

This is a **prepared base**, not a developed carrier or a DPM result. Phase 8 report definitions and file destinations, the carrier development window, and the seven-bin 09cV3 post-development injection still need to be installed/verified before the F1 run.

### Surface-tension audit (2026-09-26)

The prepared model is Fluent 2025 R2 **Mixture**. Its `setup.models.multiphase.phase_interaction` and `liquid_surface_tension` branches are inactive, so no bulk interfacial surface-tension force or coefficient is active in F1. The source paper reports `0.0411 N/m` at the separator condition, but that number is a reference property here, not a saved solver setting. The official Fluent 2025 R2 model documentation lists surface-tension force modeling for VOF and Eulerian, while the current Mixture branch exposes no active setting. A carrier-model change would alter the Phase 8 family contract and is awaiting a scientific decision.
