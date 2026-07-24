"""Offline contracts and pure planning gates for future Fluent autonomy phases.

Nothing in this package connects to Fluent or mutates a case. Live adapters
must be added deliberately after the corresponding phase exit gate is proven.
"""

from .analysis import (
    AnalysisContract,
    AnalysisDispatcher,
    AnalysisManifest,
    AnalysisPlugin,
    AnalysisRequirement,
    AnalysisResult,
    build_analysis_manifest,
)
from .capability import (
    CapabilityFingerprint,
    CapabilityObservation,
    CapabilityProbe,
    CapabilityProbeSnapshot,
    CapabilityRecipe,
    CapabilityRegistry,
)
from .decision import DecisionContext, DecisionRecord, evaluate_next_action
from .setup import (
    CompiledSetupPlan,
    ControlledChange,
    RunPolicy,
    SetupCompiler,
    SetupSpec,
)

__all__ = [
    "AnalysisContract",
    "AnalysisDispatcher",
    "AnalysisManifest",
    "AnalysisPlugin",
    "AnalysisRequirement",
    "AnalysisResult",
    "CapabilityFingerprint",
    "CapabilityObservation",
    "CapabilityProbe",
    "CapabilityProbeSnapshot",
    "CapabilityRecipe",
    "CapabilityRegistry",
    "CompiledSetupPlan",
    "ControlledChange",
    "DecisionContext",
    "DecisionRecord",
    "RunPolicy",
    "SetupCompiler",
    "SetupSpec",
    "build_analysis_manifest",
    "evaluate_next_action",
]
