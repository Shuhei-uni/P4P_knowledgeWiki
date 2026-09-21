"""Verified ASCII text transfer using Fluent's Scheme API, without a shell."""

from __future__ import annotations

from typing import Any

from pyansys_fluent.common import quote_scheme_string, remote_file_exists


def read_text(solver: Any, path: str) -> str:
    """Read a required text file through Fluent; distinguish missing from empty."""
    if not remote_file_exists(solver, path):
        raise FileNotFoundError(path)
    quoted = quote_scheme_string(path.replace("\\", "/"))
    expression = (
        f'(let ((p (open-input-file "{quoted}"))) '
        "(let loop ((chars '())) (let ((c (read-char p))) "
        "(if (eof-object? c) "
        "(begin (close-input-port p) (list->string (reverse chars))) "
        "(loop (cons c chars))))))"
    )
    result = solver.scheme.eval(expression)
    if not isinstance(result, str):
        raise RuntimeError(f"Fluent returned non-text content for {path!r}")
    return result


def ascii_write_expression(path: str, text: str) -> str:
    """Encode content as character codes, preserving C/Scheme escape sequences.

    Do not interpolate program text into nested quoted Scheme strings. Fluent's
    scheme.exec path can transform literal backslash sequences during transport.
    This expression is sent with scheme.eval and contains numeric content only.
    """
    payload = text.encode("ascii", errors="strict")
    if any(code < 32 and code not in (9, 10, 13) for code in payload) or 127 in payload:
        raise ValueError("Expected printable ASCII text, tabs and line endings")
    quoted = quote_scheme_string(path.replace("\\", "/"))
    codes = " ".join(str(code) for code in payload)
    return (
        f'(with-output-to-file "{quoted}" '
        f"(lambda () (for-each (lambda (c) (write-char (integer->char c))) '({codes}))))"
    )


def write_ascii_text_new(solver: Any, path: str, text: str) -> None:
    """Create one uniquely named file and require exact readback before return.

    Callers must use a unique destination: the existence check is not a remote
    atomic exclusive-create guarantee. A failed readback retains the artifact
    for diagnosis and must never be treated as an accepted source upload.
    """
    expression = ascii_write_expression(path, text)
    if remote_file_exists(solver, path):
        raise FileExistsError(f"Refusing to overwrite remote file: {path}")
    solver.scheme.eval(expression)
    if read_text(solver, path) != text:
        raise RuntimeError(f"Fluent ASCII text round-trip mismatch: {path}")
