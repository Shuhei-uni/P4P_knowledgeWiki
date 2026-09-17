"""P4P authority restrictions; upstream remains the Python/API validator."""
from __future__ import annotations

import ast

UPSTREAM_COMMIT = "65de7c8226d1382c9620f11fac32def059a48e79"
CORE_TOOLS = (
    "session_status", "connect", "solver_status", "find_api", "get_help",
    "get_state", "get_targeted_context", "list_named_objects", "find_named_object",
    "select_named_objects", "run_code", "validate_code", "summarize_setup",
    "simulation_report", "screenshot",
)
DOMAIN_TOOLS = frozenset({
    "mesh_quality", "list_fields", "probe_path", "get_active_status",
    "get_allowed_values", "describe_named_object_template", "describe_path",
})
FORBIDDEN_TOOLS = frozenset({"disconnect", "manage_fluent", "manage_component", "compare_files"})


class SessionPolicyError(RuntimeError):
    """An operation exceeds the repository's session-preservation authority."""


# Check references as well as calls, so aliases cannot hide lifecycle methods.
# This supplements (and never replaces) upstream's AST sandbox.
_DENIED_NAMES = frozenset({
    "exit", "quit", "close", "force_exit", "kill", "terminate", "shutdown",
    "restart", "launch_fluent", "connect_to_fluent", "cleanup_on_exit",
    "tui", "scheme", "scheme_eval", "execute_tui", "read_journal",
    "getattr", "setattr", "delattr", "eval", "exec", "compile", "__import__",
    "globals", "locals", "vars", "attrgetter", "methodcaller",
})
_DENIED_MODULES = frozenset({"ansys", "os", "sys", "subprocess", "signal", "ctypes", "importlib", "builtins", "operator"})


def check_generated_code(code: str) -> None:
    """Reject session lifecycle and unapproved TUI/Scheme routes before upstream validation.

    Not a security sandbox or proof of scientific correctness. An explicitly
    human-approved TUI exception uses a reviewed P4P worker, not an MCP bypass.
    """
    if not isinstance(code, str) or not code.strip():
        raise SessionPolicyError("Supply a non-empty Python snippet.")
    tree = ast.parse(code)
    for node in ast.walk(tree):
        name = node.id if isinstance(node, ast.Name) else node.attr if isinstance(node, ast.Attribute) else None
        if name in _DENIED_NAMES or (name is not None and name.startswith("_")):
            raise SessionPolicyError(f"P4P forbids generated access to {name!r}; preserve the Fluent session.")
        if isinstance(node, ast.Import):
            modules = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            modules = [(node.module or "").split(".")[0]]
        else:
            modules = []
        if any(module in _DENIED_MODULES for module in modules):
            raise SessionPolicyError("Generated code may not import a lifecycle/transport escape route.")
