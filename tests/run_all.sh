#!/usr/bin/env bash
#
# Runs every .src file under tests/, saves its combined stdout+stderr
# (plus exit code) next to it as <name>.out.txt, and prints a summary.
#
# Usage:
#   ./tests/run_all.sh
#
# Run this from the project root (same folder as the Makefile).
# The generated *.out.txt files are what "Sample Output" /
# "expected vs actual output" in the project report should point to.

set -u

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

if [ ! -x ./compiler ]; then
    echo "compiler binary not found -- running 'make' first..."
    make || { echo "Build failed."; exit 1; }
fi

pass=0
fail=0

# tests/valid/*.src   -> must exit 0 (successful compilation)
# tests/invalid/**/*.src -> must exit non-zero (error correctly detected)
run_one () {
    local src="$1"
    local expect_success="$2"
    local out="${src%.src}.out.txt"

    ./compiler "$src" > "$out" 2>&1
    local rc=$?
    echo "exit code: $rc" >> "$out"

    if [ "$expect_success" = "yes" ] && [ "$rc" -eq 0 ]; then
        echo "PASS  (exit 0, as expected)  $src"
        pass=$((pass + 1))
    elif [ "$expect_success" = "no" ] && [ "$rc" -ne 0 ]; then
        echo "PASS  (error correctly detected)  $src"
        pass=$((pass + 1))
    else
        echo "FAIL  (unexpected exit code $rc)  $src"
        fail=$((fail + 1))
    fi
}

echo "=== valid/ (expect exit 0) ==="
for f in tests/valid/*.src; do
    run_one "$f" "yes"
done

echo
echo "=== invalid/ (expect non-zero exit) ==="
for f in tests/invalid/lexical/*.src tests/invalid/syntax/*.src tests/invalid/semantic/*.src; do
    run_one "$f" "no"
done

echo
echo "=== Summary: $pass passed, $fail failed ==="
[ "$fail" -eq 0 ]
