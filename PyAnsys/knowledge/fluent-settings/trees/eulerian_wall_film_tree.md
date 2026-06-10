# Eulerian Wall Film Settings Tree

```text
Setup
└── Models
    └── Eulerian Wall Film
        ├── Model
        │   ├── Off
        │   └── On
        ├── Wall Film Options
        │   ├── film momentum
        │   ├── film energy if Energy on
        │   ├── film species if Species on
        │   ├── film evaporation
        │   ├── film boiling
        │   ├── film solidification
        │   └── stripping/breakup if available
        ├── Coupling
        │   ├── continuous phase coupling
        │   ├── DPM coupling
        │   ├── DPM-to-wall-film transition
        │   └── wall-film-to-DPM stripping
        ├── Numerics
        │   ├── film thickness discretization
        │   ├── film momentum discretization
        │   ├── film energy discretization
        │   └── under-relaxation/stability controls
        ├── Physical Models
        │   ├── shear-driven film motion
        │   ├── gravity-driven film motion
        │   ├── surface tension/contact angle
        │   ├── roughness effects
        │   ├── heat transfer
        │   ├── mass transfer
        │   └── phase change
        └── Boundary Conditions
            ├── wall boundary wall-film tab
            │   ├── film condition
            │   ├── initial film thickness
            │   ├── film temperature if Energy on
            │   ├── film velocity
            │   └── contact angle/adhesion
            └── DPM boundary condition tab
                ├── reflect
                ├── trap
                ├── escape
                ├── wall-film
                └── user-defined
```
