#!/usr/bin/env bash

set -u

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

if [ ! -x ./compiler ]; then
    echo "compiler binary not found -- running 'make' first..."
    make || { echo "Build failed."; exit 1; }
fi

pass=0
fail=0

run_one () {
    local src="$1"
    local expect_success="$2"

    local out="${src}.out.txt"
    if [[ "$src" == *.src || "$src" == *.c ]]; then
        out="${src%.*}.out.txt"
    fi

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
for f in tests/valid/*.src tests/valid/*.cpp tests/valid/*.java tests/valid/*.c; do
    [ -f "$f" ] && run_one "$f" "yes"
done

echo
echo "=== examples/ (expect exit 0) ==="
for f in examples/*.c examples/*.cpp examples/*.java examples/*.src; do
    [ -f "$f" ] && run_one "$f" "yes"
done

echo
echo "=== invalid/ (expect non-zero exit) ==="
for f in tests/invalid/lexical/*.src tests/invalid/syntax/*.src tests/invalid/semantic/*.src; do
    [ -f "$f" ] && run_one "$f" "no"
done

echo
echo "=== Summary: $pass passed, $fail failed ==="
[ "$fail" -eq 0 ]
