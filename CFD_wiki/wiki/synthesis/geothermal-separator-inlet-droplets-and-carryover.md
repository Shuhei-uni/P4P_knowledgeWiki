# Synthesis: Geothermal Separator Inlet Droplets and Carryover Inventory

## Scope
This page answers the practical question: what enters a geothermal steam-water separator from production wells, what particle/droplet sizes are reported or assumed, and how much enters.

Key boundary:
- `Reported`: external and local sources support separator-feed steam/brine mass flows, moisture fractions, steam-purity chemistry, separator outlet/capture measurements, and CFD droplet assumptions.
- `Missing`: no source found in this pass gives a complete measured conventional geothermal well-to-separator inlet droplet size distribution, droplet number concentration, mineral-particle size distribution, or inlet solids mass loading.
- `Inferred` / `Calculated`: use only where a source gives enough information to derive a value, such as mass loading from flow and concentration.

## External-Web Evidence

| Source | Location in system | Material entering | Size / distribution | Amount / concentration / mass flow | Evidence label | Applicability to CFD inlet | Notes / limitations |
|---|---|---|---:|---:|---|---|---|
| Machemer & Jonas 2004, Coso LEAMS/cyclone separator test, DOI `10.1016/j.geothermics.2003.10.004` | Geothermal well flow routed through separator test hardware | Wet steam with water droplets | Particle Monitor measured droplet size distribution exiting separators; exact bins not available in public abstract/snippet | Well produces `113,400 kg/h = 31.5 kg/s` of `20% moisture` steam at `427.5 kPa`, `146 degC`; if moisture is mass fraction, liquid `6.30 kg/s`, steam `25.20 kg/s` | `Reported` for flow/moisture; `Calculated` for phase split | High for quantity scale; low for inlet size bins | Gives a real geothermal well moisture load before separator testing, but the accessible source describes separator-exhaust droplet monitoring, not a published well-inlet size table ([machemer-jonas-2004-web], DOI page). |
| Takahashi et al. 2004, J-STAGE DOI `10.1252/kakoronbunshu.30.200` | Geothermal mist separator simulation inlet | Steam including droplets | Minimum trapped droplet size `20-30 um` for `H = 3.4 m`; inlet pipe `0.8 m`, average steam velocity `22 m/s` | Amount not reported | `Reported` | Medium for separator capture sensitivity; low for measured inlet distribution | This is a capture threshold from computer simulation at geothermal-plant scale, not a measured upstream droplet distribution ([takahashi-2004-web]). |
| Rivera-Diaz & Koorey 2021, NZ Geothermal Workshop | Horizontal Rotokawa/RGEN separator demister design | Brine droplets in separated steam chamber | Demister supplier criterion: `99%` removal of droplets larger than `14 um`; droplet distribution unknown | Typical design performance stated as `>99.997%` steam; concrete carryover mass not reported | `Reported` | Medium for downstream demister sizing; low for inlet distribution | Useful because it explicitly says unknown droplet distribution makes performance translation difficult ([rivera-diaz-koorey-2021-web], p.7-8). |
| Pan et al. 2019, sCO2-water geothermal separator, DOI `10.1016/j.geothermics.2019.05.001` | sCO2-water hydrocyclone produced from geothermal reservoirs | Water droplets in sCO2 | Model reached `100%` separation when droplet size was greater than `7 um` | Water mass fraction varied as operational parameter; exact inlet package not used here | `Reported` | Low-medium; different working fluid, but relevant DPM sensitivity precedent | Do not treat as steam-water separator inlet evidence; use only as a separate geothermal-separator DPM sensitivity clue ([pan-2019-web]). |
| Gudjonsdottir, Chauhan & Saevarsdottir 2021, WGC 2020+1 | Superheated geothermal steam / IDDP-style system | Precipitated silica particles in steam | Experiments/model verification used `1-20 um` silica particles | IDDP-1 reported `66 ppm` precipitated silica in superheated steam | `Reported` | Low for conventional saturated separator inlet; medium for superheated-solid-particle modelling | Applies to superheated/supercritical geothermal steam, not normal wet-steam separator inlet droplets ([gudjonsdottir-2021-web], p.1). |
| Bordvik & Naess 2023, Energies DOI `10.3390/en16165981` | IDDP-1 superheated steam pressure-drop/scaling experiment | Silica/iron oxide solids in steam | Critical nuclei `1.4-2 nm`; nanocolloids about `1-10 nm`; observed morphology down to `100 nm`; threadlike deposits about `100 nm` to `1 um`; `10 um` upstream filter caught larger solids | Test: `64 kg` steam, total solids `22 mg/kg`, `19 mg/kg` deposited on orifices, `3.1 mg/kg` collected on upstream `10 um` filter | `Reported` for experiment; `Inferred` for use as particle-size precedent | Low for conventional separator inlet; high for superheated silica/solid-particle caution | Strongest external solid-particle evidence found, but for supercritical/superheated steam after pressure drop, not a saturated geothermal separator inlet ([bordvik-naess-2023-web], sec. 4.4-5). |
| Addison & Richardson 2020, NZ Geothermal Workshop | Geothermal steam turbine supply after separator/MRS | Brine droplets, dissolved contaminants, solid particles, NCGs | Droplet sizes not reported; turbine liquid films can be `100-120 um` thick | Example turbine supplier limits: total solids `<0.5 mg/L`; chloride/silica/iron commonly `<0.1-0.3 mg/L` depending supplier | `Reported` | Medium for what contaminants matter; low for separator-inlet quantities | Confirms material classes: mechanical brine carryover, vaporous silica, formation solids, corrosion products, CO2 and H2S NCGs ([addison-richardson-2020-web], p.1-4). |
| Truesdell et al. 1989, USGS / Geothermics DOI `10.1016/0375-6505(89)90039-4` | Superheated geothermal steam systems | Chloride as HCl vapor | Molecular/vapor transport; particle size not applicable | Amount field-specific; not a separator-inlet mass package | `Reported` | Low for droplet DPM; useful for chemistry interpretation | Chloride can be vaporous HCl in superheated systems and is not always brine droplet carryover ([truesdell-1989-web]). |

External-web conclusion:
- The best external quantity found for well flow before separator testing is the Coso test value: `31.5 kg/s` wet steam with `20%` moisture, giving an estimated `6.30 kg/s` liquid and `25.20 kg/s` steam if moisture is by mass.
- External literature gives separator outlet/capture or superheated-solid particle sizes (`7 um`, `14 um`, `20-30 um`, `1-20 um`, nm-to-um silica solids), but these are not measured conventional separator-inlet droplet distributions.

## Local-Wiki Evidence

| Source | Location in system | Material entering | Size / distribution | Amount / concentration / mass flow | Evidence label | Applicability to CFD inlet | Notes / limitations |
|---|---|---|---:|---:|---|---|---|
| Purnanto et al. 2013 | Separator inlet in CFD model | Steam/vapour phase | Continuous primary phase | Baseline `80.69 kg/s`; sweep `64.85-96.52 kg/s` | `Reported` | High for local baseline | Separator pressure `11.2 bara`; total two-phase flow `197.61 kg/s` in baseline case ([purnanto-2013], p.5). |
| Purnanto et al. 2013 | Separator inlet in CFD model | Liquid/brine droplets | Uniform average droplet diameter `1e-5 m = 10 um` in setup assumptions | Baseline `116.92 kg/s`; sweep `101.09-132.76 kg/s` | `Reported` | High for local baseline; low as measured inlet truth | Pre-separation pipe flow was not modelled; this is a CFD inlet package, not a measured upstream droplet spectrum ([purnanto-2013], p.5). |
| Purnanto et al. 2013 | DPM outlet-quality calculation | Harwell droplet distribution | Harwell gives Sauter mean droplet diameter; `x_med = 1.42 x_sa`; standard distribution says about `5% <= 0.3 x_med`, all `< 2.9 x_med`; if `x_sa = 10 um`, then `x_med = 14.2 um`, `5% <= 4.26 um`, all `< 41.18 um` | Distribution fractions only; per-bin mass not listed | `Reported` for relation; `Inferred` for numeric envelope | Medium for sensitivity design | The paper says nine injections used different Harwell-derived droplet diameters, but exact nine diameters and parcel mass allocation are not listed in text ([purnanto-2013], p.3-4, p.8). |
| Chan & Zarrouk 2023 citing Pointon et al. 2009 | Cited separator CFD precedent | Water droplets | `8` water droplets of `3 um` diameter injected | Lazalde-Crabtree design removed `99.987%` in cited separator CFD | `Reported-as-cited` | Medium as sensitivity lower bound, low as inlet measurement | Useful as a small-droplet precedent, not a measured well-inlet distribution ([chan-2023], p.1). |
| Rizaldy et al. 2016 | Separator and steam line after primary separation | Liquid film / entrained droplets | Droplets range from very small to larger droplets; exact distribution not given | Entrainment increases with liquid loading fraction and inlet velocity; film fraction difficult to measure | `Reported`; `Missing` for size/amount bins | Medium for mechanism | Best local mechanism source for wall-film re-entrainment; not a direct inlet PSD source ([rizaldy-2016], p.4-8). |
| Umanzor et al. 2021 Berlin | Separator feed and downstream steam line | Dissolved chloride in geothermal fluid/brine carryover tracer | Dissolved species; not particle size | TR-4A: `82.0 kg/s` total flow with `4724 ppm` chloride, about `0.387 kg/s` chloride. TR-2/9: `97.6 kg/s` total flow with `5508 ppm` chloride, about `0.538 kg/s` chloride | `Calculated` from reported field values | High for chemistry mass balance, low for DPM solids | Separated-steam chloride flux downstream of separators: `14.9 mg/s` and `19.2 mg/s` for the two branches ([umanzor-2021], p.2, p.4-5). |
| Local source set | Separator inlet | Solid/mineral particles and corrosion products | Size not reported | Mass loading at separator inlet not reported | `Missing` | Low | Downstream deposits and ferrous iron/solid-particle damage are reported, but no separator-inlet solid PSD or mass-flow package is available in the maintained local sources ([rizaldy-2016], p.1; [arifien-2015], p.2-3). |

## Purnanto Separator-Inlet Phase Flow Table

At `Psep = 11.2 bara` and total flow `197.61 kg/s`, Purnanto reports the following inlet phase-flow values:

| Inlet enthalpy | Liquid/brine flow | Gas/steam flow | Steam mass fraction |
|---:|---:|---:|---:|
| `1440 kJ/kg` | `132.76 kg/s` | `64.85 kg/s` | `32.82%` |
| `1520 kJ/kg` | `124.84 kg/s` | `72.77 kg/s` | `36.82%` |
| `1600 kJ/kg` | `116.92 kg/s` | `80.69 kg/s` | `40.83%` |
| `1680 kJ/kg` | `109.00 kg/s` | `88.61 kg/s` | `44.84%` |
| `1760 kJ/kg` | `101.09 kg/s` | `96.52 kg/s` | `48.84%` |
| `1600 kJ/kg`, total flow reduced 25% | `87.69 kg/s` | `60.52 kg/s` | `40.84%` |

## Interpretation For CFD Setup
- For the current separator reconstruction, use Purnanto as the complete local inlet package: total flow `197.61 kg/s`, steam `80.69 kg/s`, liquid/brine `116.92 kg/s`, and average droplet diameter `10 um` at `1600 kJ/kg` and `11.2 bara`.
- For DPM droplet-size sensitivity, do not claim a measured inlet PSD. Use labelled bins: `3 um` (`Reported-as-cited` Pointon/Chan small-droplet precedent), `10 um` (`Reported` Purnanto baseline), `14.2 um` (`Inferred` Harwell median if `10 um` is Sauter mean), and `40-41 um` (`Inferred` Harwell upper-envelope check).
- For separator capture/demister checks, external sources support testing `7 um`, `14 um`, and `20-30 um` thresholds, but these are capture-performance thresholds, not inlet measurement.
- Treat dissolved minerals as brine chemistry/carryover tracers first. Model minerals as solid DPM only if the case specifically targets superheated silica precipitation, corrosion products, or measured solids; otherwise use chloride/sodium/TDS/silica mass balance.
- Include NCGs such as CO2 and H2S in thermodynamic/property or plant-process modelling when field data exists, but do not invent a separator-inlet NCG fraction for the Purnanto baseline.

## Open Gaps
- Measured droplet size distribution at a conventional geothermal well/separator inlet.
- Droplet number concentration or DPM parcel-to-real-mass mapping for Purnanto's nine Harwell-derived injections.
- Mineral-particle or corrosion-product particle size and mass loading before a conventional separator.
- Non-condensable gas and salinity package tied to the exact Purnanto separator inlet.
- Publicly accessible Coso/Machemer-Jonas droplet histogram values; the source confirms measurement but not the exact bins in accessible text.

## External Source IDs
- `[machemer-jonas-2004-web]`: Machemer, L. and Jonas, O. (2004), *Monitoring of geothermal steam moisture separator efficiency*, Geothermics 33(5), DOI `10.1016/j.geothermics.2003.10.004`, https://www.sciencedirect.com/science/article/abs/pii/S0375650504000100
- `[takahashi-2004-web]`: Takahashi et al. (2004), *On Flow Dynamics and Separation Efficiency in Mist Separators Composed of Coaxial Cylinders for Geothermal Power Plant*, DOI `10.1252/kakoronbunshu.30.200`, https://www.jstage.jst.go.jp/article/kakoronbunshu/30/2/30_2_200/_article/-char/en
- `[rivera-diaz-koorey-2021-web]`: Rivera-Diaz and Koorey (2021), *Steam Separator Selection for a Geothermal Power Station*, NZ Geothermal Workshop, https://www.worldgeothermal.org/pdf/IGAstandard/NZGW/2021/120.pdf
- `[pan-2019-web]`: Pan et al. (2019), *Design and performance analysis of a supercritical CO2 (sCO2)-water separator for power generation systems using hot sCO2 from geothermal reservoirs*, DOI `10.1016/j.geothermics.2019.05.001`, https://www.sciencedirect.com/science/article/abs/pii/S0375650518301755
- `[gudjonsdottir-2021-web]`: Gudjonsdottir, Chauhan and Saevarsdottir (2021), *Computational Modelling and Experimental Investigation of Silica Particle Transport and Deposition Occurring in Superheated Geothermal Steam*, WGC 2020+1, https://www.worldgeothermal.org/pdf/IGAstandard/WGC/2020/27065.pdf
- `[bordvik-naess-2023-web]`: Bordvik and Naess (2023), *Silica Nanoparticle Formation from Supercritical Geothermal Sources*, Energies, DOI `10.3390/en16165981`, https://www.mdpi.com/1996-1073/16/16/5981
- `[addison-richardson-2020-web]`: Addison and Richardson (2020), *Geothermal Steam Turbine Deposition Fundamentals and Proposed IAPWS Geothermal Steam Purity Limits*, NZ Geothermal Workshop, https://www.worldgeothermal.org/pdf/IGAstandard/NZGW/2020/027.pdf
- `[truesdell-1989-web]`: Truesdell, Haizlip, Armannsson and D'Amore (1989), *Origin and transport of chloride in superheated geothermal steam*, USGS / Geothermics, DOI `10.1016/0375-6505(89)90039-4`, https://pubs.usgs.gov/publication/70015368

## Related Pages
- [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
- [geothermal-boc-separator-fluent-2013-baseline](../setups/geothermal-boc-separator-fluent-2013-baseline.md)
- [geothermal-boc-separator-two-zone-split-inlet](../setups/geothermal-boc-separator-two-zone-split-inlet.md)
- [geothermal-boc-separator-pure-phase-split-velocity-inlet](../setups/geothermal-boc-separator-pure-phase-split-velocity-inlet.md)
- [geothermal-separator-design-and-cfd-patterns](geothermal-separator-design-and-cfd-patterns.md)
- [droplets-carryover-and-re-entrainment](../physics-basis/droplets-carryover-and-re-entrainment.md)
- [operating-pressure-enthalpy-and-phase-split](../physics-basis/operating-pressure-enthalpy-and-phase-split.md)
- [uncertainties-and-assumption-register](../physics-basis/uncertainties-and-assumption-register.md)
