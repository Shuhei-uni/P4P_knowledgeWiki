# Project Claim Classes

## Purpose
Project-facing summary of the allowed claim classes for separator CFD runs in this repo.

Method source:
- `../../../CFD_wiki/wiki/synthesis/separator-cfd-verification-and-validation-workflow.md`

## Claim Classes

| Claim class | Meaning in this project | Typical evidence |
|---|---|---|
| `Debug only` | useful for setup behavior or failure diagnosis only | short run, unstable monitors, incomplete setup check, or no external anchor |
| `Numerically verified` | stable enough for internal technical comparison | setup check + solution-acceptance gate + mesh/monitor/repeatability evidence |
| `Trend supported` | agrees with a defensible trend or correlation anchor | numerically verified case + literature/correlation comparison |
| `Externally validated` | strong enough for report-facing validation language | numerically verified case + predefined direct target + human-reviewed target appropriateness |

## Practical Interpretation
- Internal A/B changes do not become validation by themselves.
- Numerical stability does not imply physical validation.
- A script may recommend a maximum allowable claim class, but final sign-off happens in this wiki.
