#!/usr/bin/env python3
"""Supervise setup-07k with the locked setup-07j overnight controller."""

from __future__ import annotations

import prepare_setup07k_transient_vof_massflow_outlet as prepare07k
import supervise_setup07j_transient_vof as engine


engine.prepare07j = prepare07k
engine.PREPARATION_SCRIPT = (
    "scripts/setup/prepare_setup07k_transient_vof_massflow_outlet.py"
)
engine.QUALIFICATION_SCRIPT = (
    "scripts/setup/run_setup07k_transient_vof_massflow_outlet.py"
)


if __name__ == "__main__":
    raise SystemExit(engine.main())
