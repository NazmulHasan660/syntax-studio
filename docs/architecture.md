# Compiler Architecture & Data Flow

Syntax Studio is a single-pass-per-phase pipeline. A source file moves through six phases in order; a failure at any phase halts execution and skips the remaining phases (see `src/main.c`).

## Pipeline (6 Phases)

```text
        Source Program (.src / .c / .cpp / .java)
                       │
                       ▼
       1. Lexical Analyzer (Flex)
          tokens, line-numbered lexical errors
                       │
                       ▼
       2. Syntax Analyzer (Bison)
          parses grammar, error recovery
                       │
                       ▼
       3. Abstract Syntax Tree (AST)
          readable indented tree
                       │
                       ▼
       4. Semantic Analyzer & Symbol Table
          scoped checks, type checking, diagnostics
                       │
                       ▼
       5. Intermediate Code Generation
          Three-Address Code (TAC)
                       │
                       ▼
       6. Optimization & Target Assembly
          constant folding, constant propagation,
          pseudo-x86 assembly generation
```

Every phase runs by default for every file, `.src` or otherwise. The lexer/parser also accept C, C++, and Java surface syntax in addition to the custom Mini/C language (`Language: C|C++|Java|Mini/C` in the lexer report).

## Module map

| Phase | Source files |
|---|---|
| Lexer | `src/lexer/lexer.l` |
| Parser | `src/parser/parser.y` |
| AST | `src/ast/ast.c`, `src/ast/ast.h` |
| Symbol table | `src/symbol_table/symbol_table.c`, `.h` |
| Semantic analysis | `src/semantic/semantic.c`, `.h` |
| TAC generation | `src/codegen/tac.c`, `.h` |
| Optimizer | `src/optimizer/optimizer.c`, `.h` |
| Assembly generator | `src/codegen/assembly.c`, `.h` |
| Driver | `src/main.c` |

## Running the sample program

The official sample program is `examples/sample.src`. Build the compiler first, then run it directly on the file:

```bash
make
./compiler examples/sample.src
```

This prints every phase's output in order — tokens, AST, symbol table, semantic result, TAC, optimized TAC, and pseudo-x86 assembly — and exits with code `0` on success. To check the expected output without re-running it:

```bash
cat examples/sample.out.txt
```

To re-generate `sample.out.txt` after any change to the compiler:

```bash
./compiler examples/sample.src > examples/sample.out.txt 2>&1
echo "exit code: $?" >> examples/sample.out.txt
```