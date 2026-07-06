# Enthalpy 1600 Particle Settings

This table is generated from the extracted particle definition files in `data/Enthalpy_1600`.

Legend: `on` = `true`, `off` = `false`.

## Core Parameters

| Particle | Diameter (um) | Total flow rate | Boundary | Surfaces | Num pts | N tries | Time scale constant | Injection type | Material |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| injection-112-micron | 112.54 | 1.95 | 30047 | 2 | 2 | 1 | 0.15 | surface | water-liquid |
| injection-1631-micron | 1631.84 | 29.23 | 30047 | 2 | 2 | 1 | 0.15 | surface | water-liquid |
| injection-168-micron | 168.811 | 1.95 | 30047 | 2 | 2 | 1 | 0.15 | surface | water-liquid |
| injection-28-micron | 28.14 | 0.78 | 30047 | 2 | 2 | 1 | 0.15 | surface | water-liquid |
| injection-348-micron | 348.88 | 23.38 | 30047 | 2 | 2 | 1 | 0.15 | surface | water-liquid |
| injection-5-micron | 5.63 | 0.19 | 30047 | 2 | 2 | 1 | 0.15 | surface | water-liquid |
| injection-56-micron | 56.27 | 0.97 | 30047 | 2 | 2 | 1 | 0.15 | surface | water-liquid |
| injection-562-micron | 562.7 | 29.23 | 30047 | 2 | 2 | 1 | 0.15 | surface | water-liquid |
| injection-844-micron | 844.06 | 29.23 | 30047 | 2 | 2 | 1 | 0.15 | surface | water-liquid |

## On/Off Settings

| Particle | Stochastic | Random eddy | Cloud | Scale by area | Use face normal | Devolatilizing species | Evaporating species | Oxidizing species | Product species | RR distrib | RR uniform ln d | Evaporating liquid | Evaporating material | Multiple surface | Active law | Switch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| injection-112-micron | off | off | off | off | off | off | off | off | off | off | off | off | off | on | law-1: Inert Heating | Default |
| injection-1631-micron | off | off | off | off | off | off | off | off | off | off | off | off | off | on | law-1: Inert Heating | Default |
| injection-168-micron | off | off | off | off | off | off | off | off | off | off | off | off | off | on | law-1: Inert Heating | Default |
| injection-28-micron | off | off | off | off | off | off | off | off | off | off | off | off | off | on | law-1: Inert Heating | Default |
| injection-348-micron | off | off | off | off | off | off | off | off | off | off | off | off | off | on | law-1: Inert Heating | Default |
| injection-5-micron | off | off | off | off | off | off | off | off | off | off | off | off | off | on | law-1: Inert Heating | Default |
| injection-56-micron | off | off | off | off | off | off | off | off | off | off | off | off | off | on | law-1: Inert Heating | Default |
| injection-562-micron | off | off | off | off | off | off | off | off | off | off | off | off | off | on | law-1: Inert Heating | Default |
| injection-844-micron | off | off | off | off | off | off | off | off | off | off | off | off | off | on | law-1: Inert Heating | Default |

## Notes

- All nine particles share the same boolean on/off pattern in the extracted source files.
- The flow rate and diameter vary per particle; the remaining geometry and law settings are identical across the set.
- The original source uses `law-1 = Inert Heating` and keeps the remaining laws inactive.
