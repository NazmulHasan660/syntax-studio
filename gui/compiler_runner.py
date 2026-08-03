"""
Runs the Syntax Studio compiler and separates
the terminal output into six compiler phases.
"""

import os
import re
import subprocess
import tempfile


LEX_MARKER = "===== Lexical Analysis ====="
PARSE_MARKER = "===== Parsing ====="
AST_MARKER = "===== Abstract Syntax Tree ====="
SEMANTIC_MARKER = "===== Semantic Analysis ====="
SYMBOL_MARKER = "===== Symbol Table ====="
TAC_MARKER = "===== Three Address Code (TAC) ====="


MARKERS = [
    LEX_MARKER,
    PARSE_MARKER,
    AST_MARKER,
    SEMANTIC_MARKER,
    SYMBOL_MARKER,
    TAC_MARKER,
]


DIAGNOSTIC_RE = re.compile(
    r"^(Lexical|Syntax|Semantic) Error at line \d+",
    re.IGNORECASE
)


def extract_section(
    stdout,
    current_marker,
    next_marker=None
):
    """
    Extracts one compiler phase from stdout.
    """

    start = stdout.find(current_marker)

    if start == -1:
        return ""

    start += len(current_marker)

    if next_marker is None:
        end = len(stdout)
    else:
        end = stdout.find(
            next_marker,
            start
        )

        if end == -1:
            end = len(stdout)

    return stdout[start:end].strip()


def parse_output(stdout, stderr):
    """
    Converts raw compiler output into structured
    sections for the Tkinter GUI.
    """

    sections = []

    for index, marker in enumerate(MARKERS):
        if index + 1 < len(MARKERS):
            next_marker = MARKERS[index + 1]
        else:
            next_marker = None

        section = extract_section(
            stdout,
            marker,
            next_marker
        )

        sections.append(section)

    diagnostics = []

    for line in stderr.splitlines():
        clean_line = line.strip()

        if DIAGNOSTIC_RE.match(clean_line):
            diagnostics.append(clean_line)

    lexical_errors = [
        error
        for error in diagnostics
        if error.lower().startswith("lexical")
    ]

    syntax_errors = [
        error
        for error in diagnostics
        if error.lower().startswith("syntax")
    ]

    semantic_errors = [
        error
        for error in diagnostics
        if error.lower().startswith("semantic")
    ]

    return {
        "tokens": sections[0],
        "parsing": sections[1],

        "parsed":
            "Parsing successful." in sections[1],

        "ast": sections[2],
        "semantic_summary": sections[3],
        "symbol_table": sections[4],
        "tac": sections[5],

        "lexical_errors": lexical_errors,
        "syntax_errors": syntax_errors,
        "semantic_errors": semantic_errors,
        "diagnostics": diagnostics,

        "raw_stdout": stdout,
        "raw_stderr": stderr,
    }


def run_compiler(
    source_path,
    compiler_path="./compiler",
    timeout=5,
    language="C"
):
    """
    Runs the compiled C compiler binary on a
    source-code file.
    """

    if not os.path.isfile(compiler_path):
        return {
            "error":
                "Compiler binary not found at '{}'. "
                "Build it first with 'make'."
                .format(compiler_path)
        }

    try:
        process = subprocess.run(
            [
                compiler_path,
                source_path,
                language
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    except subprocess.TimeoutExpired:
        return {
            "error":
                "Compiler timed out after {} seconds."
                .format(timeout)
        }

    except OSError as error:
        return {
            "error":
                "Could not execute '{}': {}"
                .format(
                    compiler_path,
                    error
                )
        }

    result = parse_output(
        process.stdout,
        process.stderr
    )

    result["returncode"] = process.returncode

    return result


def run_source(
    source_text,
    compiler_path="./compiler",
    timeout=5,
    language="C"
):
    """
    Saves editor text into a temporary source file,
    runs the compiler and then deletes the file.
    """

    extension = {
        "C": ".c",
        "C++": ".cpp",
        "Java": ".java"
    }.get(
        language,
        ".src"
    )

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=extension,
            delete=False,
            encoding="utf-8"
        ) as temporary_file:

            temporary_file.write(source_text)
            temporary_path = temporary_file.name

        return run_compiler(
            temporary_path,
            compiler_path,
            timeout,
            language
        )

    finally:
        if (
            temporary_path and
            os.path.exists(temporary_path)
        ):
            try:
                os.remove(temporary_path)
            except OSError:
                pass