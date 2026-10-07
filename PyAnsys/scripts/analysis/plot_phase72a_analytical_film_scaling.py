"""Illustrate analytical gravity scaling; not a separator prediction."""
from pathlib import Path
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    repo = Path(__file__).resolve().parents[3]
    source = repo / "PyAnsys/output/phase72a-stage4-realism/20261007/run-manifest.json"
    material = json.loads(source.read_text())["dpm_material_compatibility"]
    density = material["density"]["value"]
    viscosity = material["viscosity"]["value"]
    thickness_mm = np.linspace(0, 2.1, 300)
    velocity = density * 9.81 * (thickness_mm / 1000)**2 / (3 * viscosity)
    folder = repo / "Project/experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/figures"
    folder.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.5, 4.6), constrained_layout=True)
    ax.plot(thickness_mm, velocity, color="#2166ac", linewidth=2.3)
    points = [0.25, 1, 2]
    values = []
    for h_mm in points:
        speed = density * 9.81 * (h_mm / 1000)**2 / (3 * viscosity)
        values.append({"thickness_mm": h_mm, "velocity_m_s": speed})
        ax.scatter([h_mm], [speed], color="#2166ac", s=35, zorder=3)
        offset = (8, 10) if h_mm < 2 else (-115, -15)
        ax.annotate(f"{h_mm:g} mm: {speed:.2f} m/s", (h_mm, speed), xytext=offset,
                    textcoords="offset points", fontsize=10)
    ax.set(xlabel="Film thickness (mm)", ylabel="Gravity contribution to mean film velocity (m/s)",
           xlim=(0, 2.15), ylim=(0, 94), title="Analytical film velocity remains sensitive to thickness")
    ax.text(.035, .92, "Vertical wall; gravity only\nNo gas shear or general momentum equation", transform=ax.transAxes,
            fontsize=10, va="top", bbox={"facecolor": "white", "edgecolor": "none"})
    ax.grid(alpha=.22)
    fig.suptitle("Algebraic illustration using saved compatible-material properties", fontsize=10, color="#555555")
    target = folder / "analytical-gravity-scaling.png"
    fig.savefig(target, dpi=180)
    plt.close(fig)
    provenance = {
        "classification": "analytical_illustration_not_separator_prediction",
        "source": str(source.relative_to(repo)),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "density_kg_m3": density, "viscosity_Pa_s": viscosity,
        "gravity_m_s2": 9.81, "equation": "u_mean_gravity = rho*g*h^2/(3*mu)",
        "assumptions": ["vertical wall", "gravity only", "analytical equilibrium closure"],
        "points": values,
        "theory_source": "https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_vel.html",
        "figure_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
    }
    (folder / "analytical-gravity-scaling.provenance.json").write_text(json.dumps(provenance, indent=2)+"\n")
    print(target)


if __name__ == "__main__":
    main()
