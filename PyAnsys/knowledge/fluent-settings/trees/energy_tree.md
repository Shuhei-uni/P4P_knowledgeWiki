# Energy Settings Tree

```text
Setup
└── Models
    └── Energy
        ├── Energy Equation
        │   ├── Off
        │   └── On
        ├── Viscous Heating
        ├── Pressure Work
        ├── Kinetic Energy
        ├── Diffusion Energy Source
        └── Coupled Energy Options
            ├── radiation coupling
            ├── species coupling
            ├── multiphase heat transfer
            ├── DPM heat/mass transfer
            └── wall film thermal model
```

## Indirect tree expansions after Energy is enabled

```text
Energy enabled
├── Materials
│   ├── Cp
│   ├── thermal conductivity
│   ├── latent heat if phase change
│   └── saturation/temperature-dependent properties
├── Boundary Conditions
│   ├── inlet temperature
│   ├── outlet backflow temperature
│   └── wall thermal condition
├── Multiphase
│   └── interphase heat transfer / mass transfer
├── DPM
│   └── particle temperature, vaporization, boiling laws
└── Eulerian Wall Film
    └── film temperature, evaporation, boiling
```
