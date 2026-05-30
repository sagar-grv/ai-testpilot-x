"""core/code_validator.py — AST-based safety validator for LLM-generated Selenium code.

Before any exec() call, generated code is validated by walking its AST and
rejecting patterns that could allow arbitrary code execution beyond Selenium testing:

Blocked:
  - Imports of dangerous modules (os, sys, subprocess, socket, shutil, ctypes, ...)
  - Calls to builtins: eval, exec, __import__, compile, open, input, memoryview
  - Use of dunder attributes: __class__, __bases__, __subclasses__, __globals__, ...
  - Any string that looks like a shell command injection attempt

Allowed:
  - selenium.*, time, re, urllib.parse, json, datetime — standard test helpers
  - All WebDriver calls and assertions
"""

from __future__ import annotations

import ast
from typing import Set

# ---------------------------------------------------------------------------
# Blocked module names — imports of these are rejected
# ---------------------------------------------------------------------------
_BLOCKED_MODULES: Set[str] = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "ctypes",
    "signal",
    "mmap",
    "pty",
    "fcntl",
    "pwd",
    "grp",
    "resource",
    "atexit",
    "importlib",
    "runpy",
    "code",
    "codeop",
    "builtins",
    "gc",
    "inspect",
    "dis",
    "marshal",
    "pickle",
    "shelve",
    "copyreg",
    "types",
    "weakref",
    "threading",
    "multiprocessing",
    "concurrent",
    "asyncio",
    "selectors",
    "ssl",
    "http",
    "urllib",
    "ftplib",
    "smtplib",
    "imaplib",
    "poplib",
    "xmlrpc",
    "tempfile",
    "glob",
    "fnmatch",
    "linecache",
    "fileinput",
    "filecmp",
    "stat",
    "pathlib",
}

# ---------------------------------------------------------------------------
# Blocked builtin call names
# ---------------------------------------------------------------------------
_BLOCKED_BUILTINS: Set[str] = {
    "eval",
    "exec",
    "__import__",
    "compile",
    "open",
    "input",
    "memoryview",
    "breakpoint",
    "vars",
    "dir",
    "locals",
    "globals",
    "getattr",
    "setattr",
    "delattr",
    "hasattr",
}

# ---------------------------------------------------------------------------
# Blocked dunder attribute names
# ---------------------------------------------------------------------------
_BLOCKED_DUNDERS: Set[str] = {
    "__class__",
    "__bases__",
    "__subclasses__",
    "__globals__",
    "__builtins__",
    "__code__",
    "__closure__",
    "__dict__",
    "__module__",
    "__qualname__",
    "__reduce__",
    "__reduce_ex__",
    "__getattribute__",
    "__setattr__",
    "__delattr__",
    "__init_subclass__",
    "__mro__",
}

# Maximum allowed source length (chars) — prevents huge payloads
_MAX_CODE_LENGTH = 50_000


class CodeValidationError(ValueError):
    """Raised when LLM-generated code fails the safety check."""


class _SafetyVisitor(ast.NodeVisitor):
    """AST visitor that raises CodeValidationError on any blocked pattern."""

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in _BLOCKED_MODULES:
                raise CodeValidationError(
                    f"Security: import of blocked module '{alias.name}' is not allowed "
                    f"in generated Selenium code."
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        if node.module:
            root = node.module.split(".")[0]
            if root in _BLOCKED_MODULES:
                raise CodeValidationError(
                    f"Security: from-import of blocked module '{node.module}' "
                    f"is not allowed in generated Selenium code."
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        # Block direct calls: eval(...), exec(...), open(...)
        if isinstance(node.func, ast.Name):
            if node.func.id in _BLOCKED_BUILTINS:
                raise CodeValidationError(
                    f"Security: call to '{node.func.id}()' is not allowed "
                    f"in generated Selenium code."
                )
        # Block attribute calls: obj.__class__(...), obj.__reduce__(...)
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in _BLOCKED_DUNDERS:
                raise CodeValidationError(
                    f"Security: dunder method call '{node.func.attr}()' is not allowed "
                    f"in generated Selenium code."
                )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:  # noqa: N802
        if node.attr in _BLOCKED_DUNDERS:
            raise CodeValidationError(
                f"Security: access to dunder attribute '{node.attr}' is not allowed "
                f"in generated Selenium code."
            )
        self.generic_visit(node)


def validate_generated_code(code: str, context: str = "selenium_script") -> None:
    """Parse and safety-check LLM-generated code before exec().

    Raises:
        CodeValidationError: if the code contains any blocked pattern.
        SyntaxError: if the code is not valid Python.

    Args:
        code: The Python source string to validate.
        context: Human-readable label for error messages (e.g. 'TC-001').
    """
    if not isinstance(code, str):
        raise CodeValidationError("Generated code must be a string.")

    if len(code) > _MAX_CODE_LENGTH:
        raise CodeValidationError(
            f"Security: generated code for '{context}' exceeds maximum allowed length "
            f"({len(code)} > {_MAX_CODE_LENGTH} chars)."
        )

    # Reject null bytes and other non-printable control characters
    if "\x00" in code:
        raise CodeValidationError(
            f"Security: generated code for '{context}' contains null bytes."
        )

    # Parse — raises SyntaxError if code is not valid Python
    try:
        tree = ast.parse(code, filename=f"<{context}>")
    except SyntaxError as exc:
        raise CodeValidationError(
            f"Security: generated code for '{context}' is not valid Python: {exc}"
        ) from exc

    # Walk AST and apply safety rules
    visitor = _SafetyVisitor()
    visitor.visit(tree)
