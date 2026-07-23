"""
compiler_runner.py

Talks to the compiled Syntax Studio binary (the C program built from
src/) via subprocess, and parses its stdout/stderr into clean
sections (AST, Semantic Analysis, Three Address Code, Errors) that
the Tkinter GUI can display in separate panes.

This file does NOT depend on tkinter -- it can be imported and
tested on its own.
"""

import os
import re
import subprocess
import tempfile

# Exact markers printed by src/main.c -- keep these in sync if main.c
# ever changes its printf() headers.
AST_MARKER = "Abstract Syntax Tree\n--------------------\n"
SEM_MARKER = "Semantic Analysis\n====================================\n\n"
TAC_MARKER = "Three Address Code\n====================================\n\n"

# Matches a trailing "====...====" separator line (with surrounding
# blank lines) that main.c prints just before the NEXT section header.
_TRAILING_SEPARATOR = re.compile(r"(\n=+\s*)+$")


def _clean_section(text):
    """Strips a trailing '====' separator line left over from the
    next section's header, then trims surrounding whitespace."""
    return _TRAILING_SEPARATOR.sub("", text).strip()


def parse_output(stdout, stderr):
    """
    Splits the compiler's raw stdout/stderr into a dictionary with:
      parsed            -> bool, True if "Parsing Successful" was printed
      ast               -> str, the AST dump
      semantic_summary  -> str, e.g. "No semantic errors found." or
                            "2 semantic error(s) found. Skipping code generation."
      semantic_errors   -> list[str], one entry per "Semantic Error at line ..." line
      tac               -> str, the generated three-address code (empty if skipped)
      raw_stdout        -> str, unmodified stdout
      raw_stderr        -> str, unmodified stderr
    """
    result = {
        "parsed": "Parsing Successful" in stdout,
        "ast": "",
        "semantic_summary": "",
        "semantic_errors": [],
        "tac": "",
        "raw_stdout": stdout,
        "raw_stderr": stderr,
    }

    result["semantic_errors"] = [
        line.strip() for line in stderr.splitlines() if line.strip()
    ]

    if not result["parsed"]:
        # Syntax error: lexer/parser diagnostics land on stderr,
        # nothing structured to pull out of stdout.
        return result

    ast_start = stdout.find(AST_MARKER)
    sem_start = stdout.find(SEM_MARKER)
    tac_start = stdout.find(TAC_MARKER)

    if ast_start != -1:
        ast_end = sem_start if sem_start != -1 else len(stdout)
        result["ast"] = _clean_section(stdout[ast_start + len(AST_MARKER): ast_end])

    if sem_start != -1:
        sem_end = tac_start if tac_start != -1 else len(stdout)
        result["semantic_summary"] = _clean_section(stdout[sem_start + len(SEM_MARKER): sem_end])

    if tac_start != -1:
        result["tac"] = stdout[tac_start + len(TAC_MARKER):].strip()

    return result


def run_compiler(source_path, compiler_path="./compiler", timeout=5):
    """
    Runs the compiler binary on an existing .src file on disk.
    Returns the parsed dict from parse_output(), plus:
      returncode -> int
    or, on failure to even launch the binary:
      error -> str
    """
    if not os.path.isfile(compiler_path):
        return {"error": "Compiler binary not found at '{}'. "
                          "Build it first with 'make'.".format(compiler_path)}

    try:
        proc = subprocess.run(
            [compiler_path, source_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"error": "Compiler timed out after {}s "
                          "(check for an infinite 'while' loop in the source)."
                          .format(timeout)}
    except OSError as exc:
        return {"error": "Could not execute '{}': {}".format(compiler_path, exc)}

    result = parse_output(proc.stdout, proc.stderr)
    result["returncode"] = proc.returncode
    return result


def run_source(source_text, compiler_path="./compiler", timeout=5):
    """
    Convenience wrapper: writes source_text to a temp .src file,
    runs the compiler on it, then cleans up. Use this when the GUI
    only has in-editor text and no saved file yet.
    """
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".src", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(source_text)
            tmp_path = tmp.name

        return run_compiler(tmp_path, compiler_path, timeout)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass