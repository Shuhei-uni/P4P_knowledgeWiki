#!/usr/bin/env python3
"""Local PyFluent watertight meshing starter.

This script is a small, low-risk starting point for driving Fluent Meshing
from Python against a local Fluent installation.

Scope:
- launch Fluent in meshing mode,
- import a CAD/geometry file,
- run the Watertight Geometry workflow,
- apply a coarse global surface and volume sizing,
- optionally add boundary layers,
- optionally switch to solver mode and write a mesh/case.

It is intentionally conservative and meant for first contact with the API.
It does not try to fully repair dirty CAD, name every boundary automatically,
or guarantee a final production-quality mesh.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import traceback

import ansys.fluent.core as pyfluent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Launch local Fluent Meshing and run a basic watertight workflow."
    )
    parser.add_argument(
        "--geometry-file",
        required=True,
        help="Local CAD/geometry file to import into Fluent Meshing.",
    )
    parser.add_argument(
        "--length-unit",
        default="mm",
        help="Geometry length unit passed to the import task. Default: mm.",
    )
    parser.add_argument(
        "--surface-max-size",
        type=float,
        default=80.0,
        help="Global surface max size. Start coarse, then reduce. Default: 80.0.",
    )
    parser.add_argument(
        "--volume-fill",
        choices=("tet", "poly", "poly-hexcore"),
        default="poly",
        help="Volume fill method. Default: poly.",
    )
    parser.add_argument(
        "--hex-max-cell-length",
        type=float,
        default=120.0,
        help=(
            "Hexcore max cell length for poly-hexcore mode. "
            "Ignored for other modes. Default: 120.0."
        ),
    )
    parser.add_argument(
        "--add-boundary-layers",
        action="store_true",
        help="Try to insert one default boundary-layer control.",
    )
    parser.add_argument(
        "--processor-count",
        type=int,
        default=2,
        help="Processor count to request. Default: 2.",
    )
    parser.add_argument(
        "--dimension",
        type=int,
        choices=(2, 3),
        default=3,
        help="Fluent meshing dimension. Default: 3.",
    )
    parser.add_argument(
        "--write-mesh",
        default="",
        help="Optional output mesh path to write after switching to solver mode.",
    )
    parser.add_argument(
        "--write-case",
        default="",
        help="Optional output case path to write after switching to solver mode.",
    )
    return parser


def resolve_existing_file(path_text: str) -> Path:
    path = Path(path_text).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Geometry file not found: {path}")
    return path


def maybe_write_outputs(solver_session, mesh_path: str, case_path: str) -> None:
    if mesh_path:
        output_mesh = Path(mesh_path).expanduser().resolve()
        solver_session.settings.file.write_mesh(file_name=str(output_mesh))
        print(f"WRITE_MESH_OK: {output_mesh}")
    if case_path:
        output_case = Path(case_path).expanduser().resolve()
        solver_session.settings.file.write_case(file_name=str(output_case))
        print(f"WRITE_CASE_OK: {output_case}")


def main() -> int:
    args = build_parser().parse_args()
    meshing_session = None
    solver_session = None

    try:
        geometry_file = resolve_existing_file(args.geometry_file)
        print(f"GEOMETRY_FILE: {geometry_file}")

        meshing_session = pyfluent.launch_fluent(
            mode=pyfluent.FluentMode.MESHING,
            precision=pyfluent.Precision.DOUBLE,
            processor_count=args.processor_count,
            dimension=args.dimension,
        )
        print(f"MESHING_LAUNCH_OK: {meshing_session.get_fluent_version()}")
        print(f"HEALTH: {meshing_session.health_check.check_health()}")

        watertight = meshing_session.watertight()

        import_geometry = watertight.import_geometry
        import_geometry.file_name.set_state(str(geometry_file))
        import_geometry.length_unit.set_state(args.length_unit)
        import_geometry()
        print("IMPORT_GEOMETRY_OK")

        create_surface_mesh = watertight.create_surface_mesh
        create_surface_mesh.cfd_surface_mesh_controls.max_size = args.surface_max_size
        create_surface_mesh()
        print(f"SURFACE_MESH_OK: max_size={args.surface_max_size}")

        describe_geometry = watertight.describe_geometry
        describe_geometry.update_child_tasks(setup_type_changed=False)
        describe_geometry.setup_type = "fluid"
        describe_geometry.update_child_tasks(setup_type_changed=True)
        describe_geometry()
        print("DESCRIBE_GEOMETRY_OK")

        watertight.update_regions()
        print("UPDATE_REGIONS_OK")

        if args.add_boundary_layers:
            add_boundary_layers = watertight.add_boundary_layers
            add_boundary_layers.add_child_to_task()
            add_boundary_layers.control_name.set_state("default_bl_1")
            add_boundary_layers.insert_compound_child_task()
            watertight.add_boundary_layers_child_1()
            print("BOUNDARY_LAYERS_OK")

        create_volume_mesh = watertight.create_volume_mesh_wtm
        create_volume_mesh.volume_fill.set_state(args.volume_fill)
        if args.volume_fill == "poly-hexcore":
            create_volume_mesh.volume_fill_controls.hex_max_cell_length.set_state(
                args.hex_max_cell_length
            )
        create_volume_mesh()
        print(f"VOLUME_MESH_OK: fill={args.volume_fill}")

        solver_session = meshing_session.switch_to_solver()
        print("SWITCH_TO_SOLVER_OK")
        maybe_write_outputs(solver_session, args.write_mesh, args.write_case)

        print("MESHING_STARTER_OK")
        return 0
    except Exception as exc:
        print(f"MESHING_STARTER_FAILED: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        return 1
    finally:
        if solver_session is not None:
            try:
                solver_session.exit()
                print("EXIT_OK")
            except Exception as exc:
                print(f"EXIT_FAILED: {exc}")
        elif meshing_session is not None:
            try:
                meshing_session.exit()
                print("EXIT_OK")
            except Exception as exc:
                print(f"EXIT_FAILED: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
