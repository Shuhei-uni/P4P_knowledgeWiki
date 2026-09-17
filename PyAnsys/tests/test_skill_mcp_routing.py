"""Offline instruction-contract checks; not a live Fluent qualification test."""
from pathlib import Path
import re

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".agents" / "skills"
OPERATIONS = (
    "create-figure", "dpm-analysis", "ewf-analysis", "fluent-case-build-and-run",
    "fluent-fleet-orchestration", "fluent-live-inspection", "fluent-manual-researcher",
    "fluent-report-histories", "implement-experiment", "pool-patch-volume",
    "pyansys-workflow", "residual-history-analysis", "supervise-fluent-run",
)
GUIDE = SKILLS / "fluent-live-inspection" / "mcp-integration.md"


@pytest.mark.parametrize("name", OPERATIONS)
def test_live_skills_link_shared_mcp_contract(name):
    path = SKILLS / name / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    header = yaml.safe_load(text.split("---", 2)[1])
    assert header["name"] == name
    assert header["description"]
    assert not header.get("disable-model-invocation", False)
    links = re.findall(r"\]\(([^)]+mcp-integration\.md)\)", text)
    if name == "fluent-live-inspection":
        assert "](mcp-integration.md)" in text
        links.append("mcp-integration.md")
    assert links, name
    assert all((path.parent / link).resolve() == GUIDE.resolve() for link in links)
    assert GUIDE.is_file()


@pytest.mark.parametrize("name", OPERATIONS)
def test_live_skills_do_not_restore_script_first_discovery(name):
    text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    assert "Inspect known-working repository code before constructing" not in text
    assert "docs/agent-guides/fluent-guidance.md" not in text
    assert "build_02d_vof_ic0_ic1_ic2_from_loaded_mesh.py" not in text
    assert "Add a targeted non-mutating probe" not in text
    for block in re.findall(r"```(?:python)?\n(.*?)```", text, re.S):
        assert not re.search(r"^\s*(?:import ansys\.fluent|from ansys\.fluent)", block, re.M)
        assert "connect_to_fluent(" not in block
        assert "launch_fluent(" not in block
        assert "solver.exit(" not in block


def test_shared_contract_keeps_tools_and_evidence_distinct():
    text = GUIDE.read_text(encoding="utf-8")
    for name in ("describe_path", "validate_code", "run_code", "mesh_quality", "list_fields"):
        assert f"`{name}`" in text
    for concept in ("MCP first", "EXECUTED", "<large_state_omitted>",
                    "one writer", "explicit human approval", "save/reopen"):
        assert concept in text
    assert "does not authorize agent-generated direct-PyFluent scripts" in text
    assert "not live deployment qualification" in text


@pytest.mark.parametrize("name", ("implement-experiment", "fluent-case-build-and-run", "supervise-fluent-run"))
def test_execution_skills_preserve_phase_and_completion_gates(name):
    text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    for concept in ("HYPOTHESIS_RUN_READY", "run-paths.yaml", "save/reopen", "smoke", "BLOCK"):
        assert concept in text, (name, concept)
    assert "EXECUTED" in text


@pytest.mark.parametrize("name", ("pyansys-workflow", "fluent-case-build-and-run", "pool-patch-volume"))
def test_updated_ui_prompts_use_the_same_route(name):
    path = SKILLS / name / "agents" / "openai.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    prompt = data["interface"]["default_prompt"]
    assert f"${name}" in prompt
    assert "MCP" in prompt
    assert "start its native run" not in prompt


def test_root_and_execution_guides_link_canonical_contract():
    for path in (ROOT / "AGENTS.md", ROOT / "PyAnsys" / "AGENTS.md",
                 ROOT / "PyAnsys" / "knowledge" / "fluent-settings" / "native_run_and_autosave.md"):
        text = path.read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)]+mcp-integration\.md)\)", text)
        assert links, str(path)
        assert all((path.parent / link).resolve() == GUIDE.resolve() for link in links)
