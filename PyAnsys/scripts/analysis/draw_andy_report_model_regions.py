"""Original conceptual diagram for AndyReport; no CFD data are modified."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "Project/Final research report/AndyReport/figures/model-removal-regions.png"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
fig, axes = plt.subplots(1, 3, figsize=(12, 5.1), gridspec_kw={"width_ratios": [1.2, 1.2, 1]})
blue, pale, ochre = "#226d9c", "#dcecf5", "#b37019"

for ax, title in zip(axes[:2], ["(a) Truncated model", "(b) Full lower vessel"]):
    ax.set(xlim=(-.55, 2.85), ylim=(-.9, 4.5)); ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.add_patch(Rectangle((0, 0), 2, 3.65, fill=False, lw=1.5))
    ax.annotate("Two-phase inlet", xy=(0, 2.8), xytext=(-.35, 4.0),
                ha="left", arrowprops={"arrowstyle": "->", "color": "black"})
    ax.text(1, 2.25, "Bulk flow", ha="center")
    ax.text(1, 1.83, "Steam passage / outlet\nnot drawn", ha="center", fontsize=9, color="#555555")

a=axes[0]
a.add_patch(Rectangle((0, 0), 2, .48, facecolor="#f4e5cf", edgecolor=ochre, hatch="///", alpha=.8))
a.plot([1.97, 1.97], [.48, 3.6], color=blue, lw=4)
a.plot([1.97, 1.97], [.05, .48], color="#a32434", lw=5)
a.annotate("Wall film", xy=(1.97, 3.2), xytext=(.65, 3.4), ha="center", color=blue,
           arrowprops={"arrowstyle": "->", "color": blue})
a.annotate("Local film drain", xy=(1.97, .22), xytext=(2.7, 1.03), ha="right", fontsize=9,
           arrowprops={"arrowstyle": "->", "color": "#a32434"})
a.text(.9, .22, "Bulk collector", ha="center", fontsize=9)
a.text(1, -.2, "Closed truncation boundary", ha="center", va="top", fontsize=9)
a.text(1, -.72, "Bulk sink and film sink act\non different liquid stores", ha="center", fontsize=9)

b=axes[1]
b.plot([0, 2], [1.12, 1.12], ls="--", color="#777777", lw=1)
b.text(1, 1.24, "Mapped historical cutoff", ha="center", fontsize=9)
b.add_patch(Rectangle((0, 0), 2, .5, facecolor="#f4e5cf", edgecolor=ochre, hatch="///", alpha=.8))
b.text(1, .23, "Lower bulk collector", ha="center", fontsize=9)
b.annotate("Brine boundary", xy=(2, .75), xytext=(2.75, -.23), ha="right", fontsize=9,
           arrowprops={"arrowstyle": "->", "color": "black"})
b.text(1, -.72, "Closed for collector tests;\nopen for resolved drainage", ha="center", fontsize=9)

c=axes[2]; c.set(xlim=(-.1, 2.6), ylim=(-.9, 4.5)); c.axis("off")
c.set_title("(c) Imposed split inlet", fontsize=12, fontweight="bold", pad=12)
c.add_patch(Rectangle((.35, 1.55), 1.8, 1.8, facecolor=pale, edgecolor="black", lw=1.5))
c.add_patch(Rectangle((.35, 1.55), .24, 1.8, facecolor=blue, edgecolor="black"))
c.text(1.38, 2.45, "Vapour", ha="center")
c.annotate("Liquid strip beside\nouter inlet wall", xy=(.47, 2.3), xytext=(1.2, .72), ha="center",
           arrowprops={"arrowstyle": "->", "color": blue})
c.text(1.2, -.48, "Strip width exaggerated;\narea fractions in Table D.2", ha="center", fontsize=9)
fig.text(.5, .015, "Conceptual region map, not CAD or a scale drawing. Alternative configurations are shown; not all treatments act together.",
         ha="center", fontsize=9)
fig.subplots_adjust(left=.025, right=.99, top=.88, bottom=.09, wspace=.2)
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=220, facecolor="white")
plt.close(fig)
print(OUT)
