"""Synchronous, discrete liquid face-flux evidence for Phase 7b.

The caller must first verify face-zone membership, ownership/counts, outward
orientation, and phase-2 SV_FLUX units against native flux reports. This helper
does not establish those scientific prerequisites, alter zones, start a solve,
or close Fluent. Register before a native iteration chunk and unregister only
after it returns. The installed PyFluent ITERATION_ENDED callback pauses Fluent
until the callback finishes; a live smoke test must verify that behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import math
from numbers import Integral
from pathlib import Path
import threading
from typing import Any, Sequence
from uuid import uuid4

import numpy as np

from pyansys_fluent.common import quote_scheme_string
from pyansys_fluent.remote_text import ascii_write_expression


@dataclass(frozen=True)
class FluxFaceZone:
    """One verified, non-overlapping owned face set; positive means outward."""

    name: str
    outward_sign: int
    expected_owned_count: int

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Face-zone name cannot be empty")
        if isinstance(self.outward_sign, bool) or self.outward_sign not in (-1, 1):
            raise ValueError("outward_sign must be -1 or +1")
        if (
            isinstance(self.expected_owned_count, bool)
            or not isinstance(self.expected_owned_count, Integral)
            or self.expected_owned_count <= 0
        ):
            raise ValueError("expected_owned_count must be a positive integer")
        object.__setattr__(self, "outward_sign", int(self.outward_sign))
        object.__setattr__(self, "expected_owned_count", int(self.expected_owned_count))


class Phase07bFluxMonitor:
    """Capture every iteration, latching any gap or persistence failure.

    ``start_iteration`` is the verified global iteration before the first chunk.
    Repeated callbacks for the current completed iteration (including the
    initial/chunk-boundary monitor evaluation) are recorded and skipped. Every
    advancing callback must be exactly the previous completed iteration + 1;
    indices are never offset. Remote_directory
    must already exist on the PC. A random capture ID makes each remote JSON
    destination unique, and a server-side existence check prevents overwrites.

    The local row is flushed before the remote write. A successful remote RPC
    proves the write returned, not independent file readback; verify remote
    files after the smoke/chunk. Inspect ``manifest()`` and call
    ``assert_complete(final_iteration)`` before accepting a chunk. Failures
    latch permanently and subsequent callbacks do no work. They do not stop
    the solver: the owning controller must reconcile the failed chunk.
    """

    def __init__(
        self,
        solver: Any,
        *,
        face_zones: Sequence[FluxFaceZone],
        start_iteration: int,
        local_jsonl: str | Path,
        remote_directory: str,
        prefix_source: str | Path | None = None,
    ) -> None:
        if not face_zones or len({z.name for z in face_zones}) != len(face_zones):
            raise ValueError("Require at least one unique face-zone name")
        if (
            isinstance(start_iteration, bool)
            or not isinstance(start_iteration, Integral)
            or start_iteration < 0
        ):
            raise ValueError("start_iteration must be a nonnegative integer")
        if not remote_directory.strip():
            raise ValueError("remote_directory cannot be empty")
        self._solver = solver
        self.face_zones = tuple(face_zones)
        self.start_iteration = int(start_iteration)
        self.local_jsonl = Path(local_jsonl)
        self.remote_directory = remote_directory.replace("\\", "/").rstrip("/")
        self.capture_id = uuid4().hex
        self.prefix_source = Path(prefix_source) if prefix_source else None
        self._callback_id: str | None = None
        self._file: Any = None
        self._lock = threading.RLock()
        self._error: dict[str, Any] | None = None
        self._rows = 0
        self._local_rows = 0
        self._last_iteration = self.start_iteration
        self._last_event: int | None = None
        self._skipped_duplicate_indices: list[int] = []
        self._started = False

    def remote_path(self, iteration: int) -> str:
        return (
            f"{self.remote_directory}/p7b-flux-{self.capture_id}"
            f"-i{iteration:07d}.json"
        )

    def register(self) -> str:
        """Register through the public API; never replace another callback."""
        from ansys.fluent.core.streaming_services.events_streaming import SolverEvent

        with self._lock:
            if self._started:
                raise RuntimeError("Create a new monitor for another registration")
            prefix = ""
            if self.prefix_source is not None:
                prefix = self.prefix_source.read_text(encoding="ascii")
                rows = [json.loads(line) for line in prefix.splitlines()]
                if [row['iteration'] for row in rows] != list(range(1, self.start_iteration + 1)):
                    raise ValueError('Resume flux prefix must cover exactly 1..start_iteration')
            self.local_jsonl.parent.mkdir(parents=True, exist_ok=True)
            self._file = self.local_jsonl.open("x", encoding="ascii")
            if prefix:
                self._file.write(prefix.rstrip('\n') + '\n')
                self._file.flush()
            self._started = True
            try:
                self._callback_id = self._solver.events.register_callback(
                    SolverEvent.ITERATION_ENDED, self._capture
                )
            except Exception as exc:
                self._latch(exc, stage="register", iteration=None)
                self._file.close()
                self._file = None
                raise
            return self._callback_id

    def unregister(self) -> None:
        """Remove only this callback after the solve; leave session connected."""
        # Do not hold the callback lock while the event service removes it.
        if self._callback_id is not None:
            try:
                self._solver.events.unregister_callback(self._callback_id)
            except Exception as exc:
                with self._lock:
                    self._latch(exc, stage="unregister", iteration=self._last_event)
                raise
            self._callback_id = None
        with self._lock:
            if self._file is not None:
                self._file.close()
                self._file = None

    def _latch(self, exc: Exception, *, stage: str, iteration: int | None) -> None:
        if self._error is None:
            self._error = {
                "iteration": iteration,
                "stage": stage,
                "exception_type": type(exc).__name__,
                "message": str(exc),
            }

    def _capture(self, session: Any, event_info: Any) -> None:
        with self._lock:
            if self._error is not None:
                return
            stage = "iteration_index"
            iteration: int | None = None
            try:
                raw_index = event_info.index
                if isinstance(raw_index, bool) or not isinstance(raw_index, Integral):
                    raise ValueError(f"Noninteger iteration event: {raw_index!r}")
                iteration = int(raw_index)
                self._last_event = iteration
                if iteration == self._last_iteration:
                    self._skipped_duplicate_indices.append(iteration)
                    return
                if iteration != self._last_iteration + 1:
                    raise RuntimeError(
                        f"Expected iteration {self._last_iteration + 1}, got {iteration}"
                    )
                stage = "read_phase_flux"
                data = session.fields.solution_variable_data.get_data(
                    variable_name="SV_FLUX",
                    zone_names=[z.name for z in self.face_zones],
                    domain_name="phase-2",
                )
                zone_rows = []
                for zone in self.face_zones:
                    values = np.asarray(data[zone.name], dtype=np.float64)
                    if values.ndim != 1 or values.size != zone.expected_owned_count:
                        raise RuntimeError(
                            f"{zone.name}: expected {zone.expected_owned_count} owned "
                            f"scalar face values, got shape {values.shape}"
                        )
                    if not np.isfinite(values).all():
                        raise ValueError(f"Nonfinite phase flux in {zone.name}")
                    outward = zone.outward_sign * values
                    delivery = float(np.maximum(-outward, 0).sum())
                    escape = float(np.maximum(outward, 0).sum())
                    net = float(outward.sum())
                    if not all(math.isfinite(v) for v in (delivery, escape, net)):
                        raise ValueError(f"Nonfinite flux reduction in {zone.name}")
                    zone_rows.append({
                        **asdict(zone),
                        "delivery_kg_s": delivery,
                        "escape_kg_s": escape,
                        "net_outward_kg_s": net,
                    })
                row = {
                    "schema_version": 1,
                    "capture_id": self.capture_id,
                    "iteration": iteration,
                    "captured_utc": datetime.now(timezone.utc).isoformat(),
                    "domain": "phase-2",
                    "variable": "SV_FLUX",
                    "zones": zone_rows,
                    "delivery_kg_s": math.fsum(z["delivery_kg_s"] for z in zone_rows),
                    "escape_kg_s": math.fsum(z["escape_kg_s"] for z in zone_rows),
                    "net_outward_kg_s": math.fsum(z["net_outward_kg_s"] for z in zone_rows),
                    "remote_path": self.remote_path(iteration),
                }
                payload = json.dumps(row, ensure_ascii=True, allow_nan=False, sort_keys=True) + "\n"
                stage = "write_local"
                self._file.write(payload)
                self._file.flush()
                self._local_rows += 1
                stage = "write_remote"
                path = quote_scheme_string(row["remote_path"])
                write = ascii_write_expression(row["remote_path"], payload)
                written = session.scheme.eval(
                    f'(if (file-exists? "{path}") #f (begin {write} #t))'
                )
                if written is not True:
                    raise RuntimeError("Remote write unconfirmed or destination already exists")
                self._rows += 1
                self._last_iteration = iteration
            except Exception as exc:
                self._latch(exc, stage=stage, iteration=iteration)

    def manifest(self) -> dict[str, Any]:
        """Return compact, JSON-serializable capture evidence and error state."""
        with self._lock:
            return {
                "schema_version": 1,
                "capture_id": self.capture_id,
                "registered": self._callback_id is not None,
                "start_iteration": self.start_iteration,
                "prefix_source": str(self.prefix_source.resolve()) if self.prefix_source else None,
                "inherited_rows": self.start_iteration if self.prefix_source else 0,
                "last_completed_iteration": self._last_iteration,
                "last_event_iteration": self._last_event,
                "skipped_duplicate_count": len(self._skipped_duplicate_indices),
                "skipped_duplicate_indices": list(self._skipped_duplicate_indices),
                "local_rows": self._local_rows,
                "remote_write_completed_rows": self._rows,
                "remote_readback_verified": False,
                "local_jsonl": str(self.local_jsonl.resolve()),
                "remote_path_pattern": self.remote_path(0).replace("-i0000000.json", "-i{iteration:07d}.json"),
                "face_zones": [asdict(z) for z in self.face_zones],
                "error": dict(self._error) if self._error else None,
            }

    def assert_complete(self, final_iteration: int) -> None:
        """Reject silent callback errors, missed events, or incomplete writes."""
        with self._lock:
            if isinstance(final_iteration, bool) or not isinstance(final_iteration, Integral):
                raise ValueError("final_iteration must be an integer")
            if self._error is not None:
                raise RuntimeError(f"Phase 7b flux capture failed: {self._error}")
            if (
                not self._started
                or final_iteration < self.start_iteration
                or self._last_iteration != final_iteration
                or self._rows != final_iteration - self.start_iteration
                or self._local_rows != self._rows
            ):
                raise RuntimeError(f"Incomplete Phase 7b flux capture: {self.manifest()}")
