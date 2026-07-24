from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.autonomy.analysis import (  # noqa: E402
    AnalysisContract,
    AnalysisDispatcher,
    AnalysisManifest,
    AnalysisRequirement,
    AnalysisResult,
    build_analysis_manifest,
)
from pyansys_fluent.autonomy.capability import (  # noqa: E402
    CapabilityFingerprint,
    CapabilityObservation,
    CapabilityProbe,
    CapabilityProbeSnapshot,
    CapabilityRecipe,
    CapabilityRegistry,
)
from pyansys_fluent.autonomy.common import (  # noqa: E402
    ContractValidationError,
)
from pyansys_fluent.autonomy.decision import (  # noqa: E402
    DecisionContext,
    DecisionRecord,
    evaluate_next_action,
)
from pyansys_fluent.autonomy.setup import (  # noqa: E402
    ControlledChange,
    RunPolicy,
    SetupCompiler,
    SetupSpec,
)


CASE_DIGEST = "a" * 64


def fingerprint(*, fluent_version: str = "25.2.0") -> CapabilityFingerprint:
    return CapabilityFingerprint(
        fluent_version=fluent_version,
        pyfluent_version="0.40.2",
        solver_mode="solution",
        dimension=3,
        precision="double",
        active_models=("energy", "mixture"),
        phase_count=2,
        boundary_types=(
            ("liquidinlet", "velocity-inlet"),
            ("steaminlet", "velocity-inlet"),
            ("steamoutlet", "pressure-outlet"),
        ),
        source_case_sha256=CASE_DIGEST,
    )


def recipe(
    semantic_id: str,
    current: CapabilityFingerprint,
    *,
    verified: bool = True,
) -> CapabilityRecipe:
    return CapabilityRecipe(
        recipe_id=f"recipe-{semantic_id}",
        semantic_id=semantic_id,
        strategy="settings_api",
        target=f"setup.{semantic_id}",
        readback_target=f"setup.{semantic_id}",
        fingerprint_digest=current.digest,
        verified=verified,
    )


def run_policy() -> RunPolicy:
    return RunPolicy(
        total_iterations=500,
        chunk_iterations=25,
        checkpoint_interval=25,
    )


def setup_spec(current: CapabilityFingerprint) -> SetupSpec:
    return SetupSpec(
        setup_id="08c-loading-low",
        experiment_id="08c-loading-sensitivity",
        parent_case_path=r"C:\cases\08b-parent.cas.h5",
        parent_case_sha256=CASE_DIGEST,
        required_fingerprint_digest=current.digest,
        controlled_changes=(
            ControlledChange(
                semantic_id="numerics.pressure_velocity_coupling",
                stage="numerics",
                requested_value="coupled",
                expected_parent_value="simple",
            ),
            ControlledChange(
                semantic_id="boundaries.steaminlet.velocity",
                stage="boundaries",
                requested_value=20.0,
                expected_parent_value=27.118,
            ),
        ),
        preserve_semantic_ids=(
            "models.multiphase",
            "materials.water_liquid",
        ),
        run_policy=run_policy(),
        analysis_contract_id="carrier-loading-v1",
    )


def analysis_contract() -> AnalysisContract:
    return AnalysisContract(
        contract_id="carrier-loading-v1",
        experiment_question="Does inlet loading change carrier separation?",
        requirements=(
            AnalysisRequirement(
                analysis_id="carrier_mass_balance",
                applicability="required",
                completion_predicates=("inlet_total", "outlet_total"),
            ),
            AnalysisRequirement(
                analysis_id="residual_history",
                applicability="required",
                completion_predicates=("final_residuals",),
            ),
            AnalysisRequirement(
                analysis_id="dpm_summary",
                applicability="not_applicable",
                reason="Carrier-only first vertical slice.",
            ),
        ),
    )


def complete_manifest() -> AnalysisManifest:
    return build_analysis_manifest(
        analysis_contract(),
        (
            AnalysisResult(
                analysis_id="carrier_mass_balance",
                status="complete",
                satisfied_predicates=("inlet_total", "outlet_total"),
                artifact_paths=("carrier.json",),
            ),
            AnalysisResult(
                analysis_id="residual_history",
                status="complete",
                satisfied_predicates=("final_residuals",),
                artifact_paths=("residuals.csv",),
            ),
        ),
    )


class CapabilityContractTests(unittest.TestCase):
    def test_fingerprint_round_trip_and_digest_are_stable(self) -> None:
        current = fingerprint()
        rebuilt = CapabilityFingerprint.from_dict(current.to_dict())
        self.assertEqual(rebuilt, current)
        self.assertEqual(rebuilt.digest, current.digest)

    def test_observation_round_trip_preserves_active_api_evidence(self) -> None:
        observation = CapabilityObservation(
            semantic_id="boundaries.steaminlet.velocity",
            path="setup.boundary_conditions.velocity_inlet.steaminlet",
            active=True,
            read_only=False,
            active_children=("momentum", "turbulence"),
            active_commands=("get_state",),
            active_queries=("allowed_values",),
            allowed_values=(20.0, 27.118),
            compact_state={"velocity": 27.118},
        )
        self.assertEqual(
            CapabilityObservation.from_dict(observation.to_dict()),
            observation,
        )

    def test_string_is_not_silently_accepted_as_an_array(self) -> None:
        payload = fingerprint().to_dict()
        payload["active_models"] = "mixture"
        with self.assertRaises(ContractValidationError):
            CapabilityFingerprint.from_dict(payload)

    def test_registry_refuses_unverified_or_mismatched_recipe(self) -> None:
        current = fingerprint()
        registry = CapabilityRegistry(
            (recipe("boundaries.steaminlet.velocity", current),)
        )
        resolved = registry.resolve(
            "boundaries.steaminlet.velocity",
            current,
        )
        self.assertTrue(resolved.verified)

        with self.assertRaises(ContractValidationError):
            registry.resolve(
                "boundaries.steaminlet.velocity",
                fingerprint(fluent_version="26.1.0"),
            )
        registry.invalidate(
            "boundaries.steaminlet.velocity",
            "live readback shape changed",
        )
        with self.assertRaises(ContractValidationError):
            registry.resolve(
                "boundaries.steaminlet.velocity",
                current,
            )

    def test_probe_uses_injected_read_only_backend(self) -> None:
        current = fingerprint()

        class FakeBackend:
            def capture_fingerprint(self):
                return current

            def observe(self, semantic_id):
                return CapabilityObservation(
                    semantic_id=semantic_id,
                    path=f"fake.{semantic_id}",
                    active=True,
                    read_only=False,
                )

        snapshot = CapabilityProbe(FakeBackend()).capture(
            ("boundaries.steaminlet.velocity",)
        )
        self.assertEqual(
            CapabilityProbeSnapshot.from_dict(snapshot.to_dict()),
            snapshot,
        )
        self.assertEqual(snapshot.fingerprint, current)


class ExampleContractTests(unittest.TestCase):
    def test_08c_example_bundle_matches_python_contracts(self) -> None:
        path = (
            PROJECT_ROOT
            / "contracts"
            / "examples"
            / "08c-carrier-autonomy-scaffold.json"
        )
        bundle = json.loads(path.read_text(encoding="utf-8"))
        current = CapabilityFingerprint.from_dict(
            bundle["capability_fingerprint"]
        )
        recipes = tuple(
            CapabilityRecipe.from_dict(item)
            for item in bundle["capability_recipes"]
        )
        spec = SetupSpec.from_dict(bundle["setup_spec"])
        contract = AnalysisContract.from_dict(
            bundle["analysis_contract"]
        )

        self.assertTrue(bundle["example_only"])
        self.assertEqual(spec.required_fingerprint_digest, current.digest)
        self.assertTrue(all(not item.verified for item in recipes))
        self.assertEqual(spec.analysis_contract_id, contract.contract_id)


class SetupCompilerTests(unittest.TestCase):
    def test_spec_round_trip_and_compiler_use_dependency_stage_order(self) -> None:
        current = fingerprint()
        spec = setup_spec(current)
        self.assertEqual(SetupSpec.from_dict(spec.to_dict()), spec)
        registry = CapabilityRegistry(
            tuple(
                recipe(change.semantic_id, current)
                for change in spec.controlled_changes
            )
        )

        plan = SetupCompiler().compile(spec, current, registry)

        self.assertEqual(
            [step.stage for step in plan.steps],
            ["boundaries", "numerics"],
        )
        self.assertTrue(
            all(step.readback_required for step in plan.steps)
        )
        self.assertTrue(plan.requires_fresh_session_reopen)

    def test_controlled_and_preserved_overlap_is_rejected(self) -> None:
        current = fingerprint()
        spec = setup_spec(current)
        invalid = SetupSpec(
            setup_id=spec.setup_id,
            experiment_id=spec.experiment_id,
            parent_case_path=spec.parent_case_path,
            parent_case_sha256=spec.parent_case_sha256,
            required_fingerprint_digest=spec.required_fingerprint_digest,
            controlled_changes=spec.controlled_changes,
            preserve_semantic_ids=(
                "boundaries.steaminlet.velocity",
            ),
            run_policy=spec.run_policy,
            analysis_contract_id=spec.analysis_contract_id,
        )
        with self.assertRaises(ContractValidationError):
            invalid.validate()

    def test_run_policy_requires_checkpoint_alignment(self) -> None:
        with self.assertRaises(ContractValidationError):
            RunPolicy(
                total_iterations=500,
                chunk_iterations=30,
                checkpoint_interval=100,
            ).validate()

    def test_compiler_refuses_missing_recipe_and_fingerprint_drift(self) -> None:
        current = fingerprint()
        spec = setup_spec(current)
        with self.assertRaises(ContractValidationError):
            SetupCompiler().compile(
                spec,
                current,
                CapabilityRegistry(),
            )
        with self.assertRaises(ContractValidationError):
            SetupCompiler().compile(
                spec,
                fingerprint(fluent_version="26.1.0"),
                CapabilityRegistry(),
            )


class AnalysisGateTests(unittest.TestCase):
    def test_required_complete_and_not_applicable_are_safe(self) -> None:
        manifest = complete_manifest()
        self.assertTrue(manifest.safe_for_interpretation)
        self.assertEqual(
            AnalysisManifest.from_dict(manifest.to_dict()),
            manifest,
        )
        dpm = next(
            result
            for result in manifest.results
            if result.analysis_id == "dpm_summary"
        )
        self.assertEqual(dpm.status, "not_applicable")

    def test_missing_required_predicate_blocks_interpretation(self) -> None:
        manifest = build_analysis_manifest(
            analysis_contract(),
            (
                AnalysisResult(
                    analysis_id="carrier_mass_balance",
                    status="complete",
                    satisfied_predicates=("inlet_total",),
                ),
                AnalysisResult(
                    analysis_id="residual_history",
                    status="incomplete",
                    blocking_reasons=("history file missing",),
                ),
            ),
        )
        self.assertFalse(manifest.safe_for_interpretation)
        self.assertTrue(
            any("outlet_total" in item for item in manifest.blocking_reasons)
        )
        self.assertTrue(
            any("history file missing" in item for item in manifest.blocking_reasons)
        )

    def test_undeclared_result_is_rejected(self) -> None:
        with self.assertRaises(ContractValidationError):
            build_analysis_manifest(
                analysis_contract(),
                (
                    AnalysisResult(
                        analysis_id="ewf_snapshot",
                        status="complete",
                    ),
                ),
            )

    def test_dispatcher_blocks_missing_plugin_and_accepts_complete_plugins(self) -> None:
        class CompletePlugin:
            def __init__(self, analysis_id, predicates):
                self.analysis_id = analysis_id
                self.predicates = predicates

            def execute(self, _context):
                return AnalysisResult(
                    analysis_id=self.analysis_id,
                    status="complete",
                    satisfied_predicates=self.predicates,
                )

        missing = AnalysisDispatcher().execute(
            analysis_contract(),
            context={},
        )
        self.assertFalse(missing.safe_for_interpretation)

        complete = AnalysisDispatcher(
            (
                CompletePlugin(
                    "carrier_mass_balance",
                    ("inlet_total", "outlet_total"),
                ),
                CompletePlugin(
                    "residual_history",
                    ("final_residuals",),
                ),
            )
        ).execute(analysis_contract(), context={})
        self.assertTrue(complete.safe_for_interpretation)


class DecisionGateTests(unittest.TestCase):
    def context(self, **overrides) -> DecisionContext:
        values = {
            "capability_ready": True,
            "setup_verified": True,
            "run_outcome": "completed",
            "analysis_manifest": complete_manifest(),
            "evidence_adequate": True,
            "evidence_refs": ("analysis-manifest.json",),
        }
        values.update(overrides)
        return DecisionContext(**values)

    def test_gate_priorities_cover_bounded_recovery_actions(self) -> None:
        cases = (
            (
                {"capability_ready": False},
                "CAPABILITY_RESEARCH_REQUIRED",
            ),
            ({"setup_verified": False}, "REPAIR_SETUP"),
            ({"run_outcome": "interrupted"}, "RERUN_FROM_CHECKPOINT"),
            ({"run_outcome": "nonconverged"}, "CONTINUE_ITERATIONS"),
            (
                {
                    "analysis_manifest": build_analysis_manifest(
                        analysis_contract(),
                        (),
                    )
                },
                "INCREASE_ANALYSIS_BUDGET",
            ),
            ({"evidence_adequate": False}, "HUMAN_REVIEW_REQUIRED"),
            ({"stop_requested": True}, "STOP_PROJECT_BRANCH"),
        )
        for overrides, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(
                    evaluate_next_action(self.context(**overrides)).action,
                    expected,
                )

    def test_all_gates_pass_only_proposes_approved_next_experiment(self) -> None:
        record = evaluate_next_action(self.context())
        self.assertEqual(record.action, "NEXT_EXPERIMENT")
        self.assertTrue(record.approval_required)
        self.assertEqual(
            DecisionRecord.from_dict(record.to_dict()),
            record,
        )


if __name__ == "__main__":
    unittest.main()
