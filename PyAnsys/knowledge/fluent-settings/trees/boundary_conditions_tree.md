# Boundary Conditions Settings Tree

```text
Setup
└── Boundary Conditions
    ├── steaminlet
    │   ├── boundary type
    │   ├── mixture/global flow values
    │   ├── turbulence values
    │   ├── phase volume fractions if Multiphase on
    │   ├── temperature if Energy on
    │   └── DPM injection target surface if used indirectly
    ├── liquidinlet
    ├── steamoutlet
    │   ├── pressure/outlet values
    │   ├── backflow phase fractions if Multiphase on
    │   └── backflow temperature if Energy on
    ├── bottom
    │   ├── wall or outlet depending model
    │   ├── DPM boundary condition if DPM on
    │   └── wall-film condition if EWF on
    └── wall
        ├── no-slip / roughness
        ├── wall thermal condition if Energy on
        ├── DPM boundary condition if DPM on
        └── Eulerian wall film tab if EWF on
```
