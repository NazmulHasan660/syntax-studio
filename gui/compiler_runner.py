"""
Runs the Syntax Studio compiler and separates
the terminal output for the Tkinter GUI.

Supports both the old and new compiler
output formats.
"""

import os
import re
import subprocess
import tempfile


LEX_MARKER = "===== Lexical Analysis ====="

OLD_PARSE_MARKER = "===== Parsing ====="
OLD_AST_MARKER = "===== Abstract Syntax Tree ====="
OLD_SYMBOL_MARKER = "===== Symbol Table ====="
OLD_TAC_MARKER = "===== Three Address Code (TAC) ====="

NEW_PARSE_MARKER = "===== Parser (AST) ====="
NEW_TAC_MARKER = "===== Intermediate Code (TAC) ====="

SEMANTIC_MARKER = "===== Semantic Analysis ====="
OPTIMIZER_MARKER = "===== Code Optimization ====="
ASSEMBLY_MARKER = (
    "===== Target Code Generation (Assembly) ====="
)


DIAGNOSTIC_RE = re.compile(
    r"^(Lexical|Syntax|Semantic) Error at line \d+",
    re.IGNORECASE
)


def extract_section(
    output,
    start_marker,
    end_marker=None
):
    """
    Extracts the text between two compiler markers.
    """

    start = output.find(start_marker)

    if start == -1:
        return ""

    start += len(start_marker)

    if end_marker is None:
        end = len(output)
    else:
        end = output.find(
            end_marker,
            start
        )

        if end == -1:
            end = len(output)

    return output[start:end].strip()


def split_subsection(
    output,
    heading
):
    """
    Splits AST or Symbol Table from its parent phase.
    """

    before, found, after = output.partition(
        heading
    )

    if found:
        return (
            before.strip(),
            after.strip()
        )

    return (
        output.strip(),
        ""
    )


def collect_diagnostics(stderr):
    """
    Collects lexical, syntax and semantic errors.
    """

    diagnostics = []

    for line in stderr.splitlines():
        clean_line = line.strip()

        if DIAGNOSTIC_RE.match(clean_line):
            diagnostics.append(clean_line)

    return diagnostics


def filter_errors(
    diagnostics,
    error_type
):
    """
    Returns errors belonging to one compiler phase.
    """

    return [
        error
        for error in diagnostics
        if error.lower().startswith(
            error_type.lower()
        )
    ]


def parse_new_output(
    stdout
):
    """
    Parses the new six-phase compiler output.
    """

    tokens = extract_section(
        stdout,
        LEX_MARKER,
        NEW_PARSE_MARKER
    )

    parser_phase = extract_section(
        stdout,
        NEW_PARSE_MARKER,
        SEMANTIC_MARKER
    )

    parsing, ast = split_subsection(
        parser_phase,
        "Abstract Syntax Tree:"
    )

    semantic_phase = extract_section(
        stdout,
        SEMANTIC_MARKER,
        NEW_TAC_MARKER
    )

    semantic_summary, symbol_table = (
        split_subsection(
            semantic_phase,
            "Symbol Table:"
        )
    )

    tac = extract_section(
        stdout,
        NEW_TAC_MARKER,
        OPTIMIZER_MARKER
    )

    return {
        "tokens": tokens,
        "parsing": parsing,
        "ast": ast,
        "semantic_summary": semantic_summary,
        "symbol_table": symbol_table,
        "tac": tac,
    }


def parse_old_output(
    stdout
):
    """
    Parses the previous compiler output format.
    """

    return {
        "tokens": extract_section(
            stdout,
            LEX_MARKER,
            OLD_PARSE_MARKER
        ),

        "parsing": extract_section(
            stdout,
            OLD_PARSE_MARKER,
            OLD_AST_MARKER
        ),

        "ast": extract_section(
            stdout,
            OLD_AST_MARKER,
            SEMANTIC_MARKER
        ),

        "semantic_summary": extract_section(
            stdout,
            SEMANTIC_MARKER,
            OLD_SYMBOL_MARKER
        ),

        "symbol_table": extract_section(
            stdout,
            OLD_SYMBOL_MARKER,
            OLD_TAC_MARKER
        ),

        "tac": extract_section(
            stdout,
            OLD_TAC_MARKER,
            OPTIMIZER_MARKER
        ),
    }


def parse_output(
    stdout,
    stderr
):
    """
    Converts compiler output into GUI sections.
    """

    if NEW_PARSE_MARKER in stdout:
        result = parse_new_output(
            stdout
        )
    else:
        result = parse_old_output(
            stdout
        )

    diagnostics = collect_diagnostics(
        stderr
    )

    result.update({
        "parsed":
            "Parsing successful."
            in result["parsing"],

        "optimizer": extract_section(
            stdout,
            OPTIMIZER_MARKER,
            ASSEMBLY_MARKER
        ),

        "assembly": extract_section(
            stdout,
            ASSEMBLY_MARKER
        ),

        "lexical_errors": filter_errors(
            diagnostics,
            "lexical"
        ),

        "syntax_errors": filter_errors(
            diagnostics,
            "syntax"
        ),

        "semantic_errors": filter_errors(
            diagnostics,
            "semantic"
        ),

        "diagnostics": diagnostics,
        "raw_stdout": stdout,
        "raw_stderr": stderr,
    })

    return result


def run_compiler(
    source_path,
    compiler_path="./compiler",
    timeout=5,
    language="C"
):
    """
    Runs the compiled Syntax Studio compiler.
    """

    if not os.path.isfile(compiler_path):
        return {
            "error":
                "Compiler binary not found at '{}'. "
                "Run 'make' first."
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

    result["returncode"] = (
        process.returncode
    )

    return result


def run_source(
    source_text,
    compiler_path="./compiler",
    timeout=5,
    language="C"
):
    """
    Saves GUI editor text temporarily,
    runs the compiler and deletes the file.
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

            temporary_file.write(
                source_text
            )

            temporary_path = (
                temporary_file.name
            )

        return run_compiler(
            temporary_path,
            compiler_path,
            timeout,
            language
        )

    finally:
        if (
            temporary_path
            and os.path.exists(temporary_path)
        ):
            try:
                os.remove(
                    temporary_path
                )
            except OSError:
                pass