# Discrete Phase Model / DPM Settings Tree

```text
Setup
└── Models
    └── Discrete Phase Model
        ├── Interaction
        │   ├── Interaction with Continuous Phase
        │   ├── Update DPM Sources Every Flow Iteration
        │   └── DPM Iteration Interval
        ├── Particle Treatment
        │   ├── Steady / Unsteady Particle Tracking
        │   ├── Track with Fluid Flow Time Step
        │   ├── Inject Particles at Particle/Fluid Time Step
        │   ├── Particle Time Step Size
        │   └── Number of Time Steps
        ├── Tracking
        │   ├── Max. Number of Steps
        │   ├── Specify Length Scale
        │   ├── Step Length Factor
        │   ├── High-Res Tracking
        │   ├── Accuracy Control
        │   ├── Tolerance
        │   ├── Max. Refinements
        │   ├── Track in Absolute Frame
        │   └── Tracking Scheme Selection
        ├── Physical Models
        │   ├── Saffman Lift Force
        │   ├── Virtual Mass Force
        │   ├── Pressure Gradient Force
        │   ├── Erosion / Accretion
        │   ├── Two-Way Turbulence Coupling
        │   ├── DEM Collision
        │   ├── Stochastic Collision
        │   ├── Breakup
        │   └── Volume Displacement
        ├── UDF
        │   ├── Body Force
        │   ├── Scalar Update
        │   ├── Source
        │   └── DPM Time Step
        ├── Numerics
        ├── Parallel
        └── Injections
            ├── Create / Copy / Delete
            ├── List Particles / List Properties
            ├── Read / Write
            └── Injection list
```

## Injection object tree

```text
DPM
└── Injections
    └── <injection-name>
        ├── Injection Name
        ├── Injection Type
        │   ├── single
        │   ├── group
        │   ├── cone
        │   ├── surface
        │   ├── file
        │   └── atomizer/model-specific types
        ├── Injection Surfaces
        ├── Particle Type
        │   ├── Massless
        │   ├── Inert
        │   ├── Droplet
        │   ├── Combusting
        │   └── Multicomponent
        ├── Material
        ├── Diameter Distribution
        ├── Species Fields
        │   ├── Evaporating Species
        │   ├── Devolatilizing Species
        │   ├── Oxidizing Species
        │   └── Product Species
        ├── Laws
        ├── Particle Reinjection
        ├── Discrete Phase Domain
        ├── Point Properties
        │   ├── position components
        │   ├── velocity components
        │   ├── diameter
        │   ├── temperature if Energy on
        │   ├── start time
        │   ├── stop time
        │   ├── total flow rate
        │   ├── stagger options
        │   ├── surface options
        │   └── wallfilm injection option
        ├── Physical Models
        │   ├── drag law
        │   ├── rough wall model
        │   └── particle rotation
        ├── Turbulent Dispersion
        │   ├── dispersion model
        │   ├── random eddy lifetime
        │   ├── number of tries
        │   ├── time scale constant
        │   └── length scale constant
        ├── Parcel
        ├── Wet Combustion
        ├── Components
        ├── UDF
        └── Multiple Reactions
```
