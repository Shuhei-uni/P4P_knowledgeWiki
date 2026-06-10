# Multiphase Settings Tree

```text
Setup
└── Models
    └── Multiphase
        ├── Model
        │   ├── Off
        │   ├── Volume of Fluid / VOF
        │   ├── Mixture
        │   └── Eulerian
        ├── Number of Phases
        ├── Phase Assignment
        │   ├── Primary Phase
        │   └── Secondary Phase(s)
        ├── Volume Fraction Parameters
        │   ├── explicit/implicit formulation
        │   ├── volume fraction cutoff
        │   └── Courant/interface controls
        ├── Interface Modeling
        │   ├── sharp
        │   ├── dispersed
        │   └── sharp/dispersed or model-dependent options
        ├── Surface Tension
        │   ├── enable surface tension
        │   ├── phase-pair coefficient
        │   └── wall adhesion/contact angle
        ├── Phase Interaction
        │   ├── drag
        │   ├── lift
        │   ├── wall lubrication
        │   ├── turbulent dispersion
        │   ├── virtual mass
        │   ├── heat transfer
        │   ├── mass transfer
        │   ├── surface tension
        │   └── interfacial area / population balance
        ├── Slip / Relative Velocity
        │   ├── none
        │   ├── algebraic slip
        │   └── user-defined
        ├── Open Channel Flow
        │   ├── enable
        │   ├── free surface level
        │   └── bottom level
        └── Advanced / Numerics
            ├── phase-coupled SIMPLE
            ├── interface compression
            ├── implicit body force
            └── stability controls
```

## VOF branch

```text
Multiphase
└── VOF
    ├── number of phases
    ├── volume fraction formulation
    ├── interface capturing scheme
    ├── surface tension
    ├── wall adhesion/contact angle
    ├── phase interaction
    ├── open channel flow
    └── volume fraction numerics
```

## Mixture branch

```text
Multiphase
└── Mixture
    ├── number of phases
    ├── phase assignment
    ├── slip / relative velocity
    ├── drag law
    ├── optional lift / virtual mass / turbulent dispersion if exposed
    ├── surface tension if exposed
    └── mixture-specific numerics
```

## Eulerian branch

```text
Multiphase
└── Eulerian
    ├── number of phases
    ├── phase assignment
    ├── drag
    ├── lift
    ├── wall lubrication
    ├── turbulent dispersion
    ├── virtual mass
    ├── heat transfer if Energy enabled
    ├── mass transfer / phase change if enabled
    ├── interfacial area
    ├── granular options if solid phase
    ├── turbulence interaction
    └── phase-coupled numerics
```
