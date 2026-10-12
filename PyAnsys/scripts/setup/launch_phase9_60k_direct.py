"""Keep the user-authorized local Phase 9 solver alive in an interactive terminal."""
import os
from pathlib import Path
import ansys.fluent.core as pyfluent

fluent_work_dir = Path(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\FluentDirectUse")
fluent_work_dir.mkdir(parents=True, exist_ok=True)
os.chdir(fluent_work_dir)
solver = pyfluent.launch_fluent(
    product_version="25.2",
    fluent_path=r"C:\Program Files\ANSYS Inc\ANSYS Student\v252\fluent\ntbin\win64\fluent.exe",
    cwd=str(fluent_work_dir), mode="solver", dimension=3, precision="double",
    processor_count=4, ui_mode="no_gui", py=True, cleanup_on_exit=False,
    start_transcript=True,
)
print("LOCAL_PHASE9_SOLVER_READY", flush=True)
