### A Mini Compiler for a Simplified Statically-Typed Language using Flex & Bison

**Course:** Compiler Construction Lab  
**Department:** Computer Science and Engineering  
**University:** Metropolitan University, Sylhet, Bangladesh

---

# Project Goal

Syntax Studio is a mini compiler developed using Flex and Bison. It implements all six required compiler phases end to end: lexical analysis, syntax analysis, semantic analysis, intermediate code generation (Three Address Code), code optimization (constant folding and constant propagation), and target code generation (simplified x86-style assembly). Abstract syntax tree (AST) construction and symbol table management happen inside the parser and semantic-analysis phases respectively.

Per the instructor's clarified project scope, the compiler also accepts common C/C++/Java surface syntax (`#include`/`using namespace`/`import`/`package`, access modifiers, `cout <<`, `printf(...)`, `System.out.println(...)`, `boolean`/`double` aliases) in addition to the core fixed language, and supports `for`, `do-while`, `while`, `++`/`--`, and unary minus alongside the base statement/operator set.

The project follows the compiler design principles taught in the Compiler Construction Lab course.

---

# Team

## Nazmul Hasan

Primary Responsibilities

- Project Foundation & Architecture
- Build System (Makefile)
- Lexical Analyzer (Flex)
- Syntax Analyzer (Bison)
- Abstract Syntax Tree (AST)
- Module Integration

---

## Mahdi Hasan Mehedi

Primary Responsibilities

- Symbol Table
- Semantic Analysis
- Type Checking
- Three Address Code (TAC) Generation
- Code Optimization (constant folding / propagation)
- Target Code Generation (assembly)

---

# Compiler Pipeline

Six required phases, per the course specification:

```
Source Program
      │
      ▼
1. Lexical Analyzer (Flex)
      │
      ▼
2. Syntax Analyzer (Bison)
      │   (builds the AST as it parses)
      ▼
3. Semantic Analysis
      │   (builds/queries the symbol table as it walks the AST)
      ▼
4. Intermediate Code (Three Address Code)
      │
      ▼
5. Code Optimization (constant folding + constant propagation)
      │
      ▼
6. Target Code Generation (simplified x86-style assembly)
```

AST construction and symbol table management are not separate
pipeline phases -- the AST is built as a side effect of phase 2
(Parser), and the symbol table is built/queried as a side effect of
phase 3 (Semantic Analysis). They get their own chapters in the
project report for depth, but the phase count stays at six.

Each later phase only runs if the one before it succeeded: a
lexical error stops the pipeline before parsing, a syntax error
stops it before semantic analysis, and a semantic error stops it
before TAC/optimization/target code generation.

---

# Supported Language Features

## Data Types

- int
- float
- bool (`boolean` is accepted as a Java-style alias, `double` as a C/C++-style alias for float)

## Statements

- Variable Declaration (including `int x = 5;` initialized form)
- Assignment
- Arithmetic Expressions
- Relational Expressions
- Logical Expressions
- if
- if-else
- while
- for
- do-while
- print (three forms: `print expr;`, `cout << expr;`, `printf(expr, expr, ...);`)

## Operators

### Arithmetic

```
+  -  *  /  %
```

### Relational

```
<  >  <=  >=  ==  !=
```

### Logical

```
&&  ||  !
```

### Unary / Increment

```
-x   (unary minus)
x++  x--
```

## Multi-Language Surface Syntax

The lexer recognizes and accepts common C/C++/Java surface syntax on
top of the core fixed language, per the instructor's confirmed
project scope:

- Directives/imports, silently ignored: `#include ...`, `using namespace ...`, `import ...`, `package ...`
- Access/storage modifiers, silently ignored: `public`, `private`, `protected`, `static`, `final`, `const`
- Print forms: `printf(...)` (C), `cout << ...` / `std::cout << ...` (C++), `System.out.println(...)` / `System.out.print(...)` (Java)
- Type aliases: `double` for `float`, `boolean` for `bool`

This lets a pasted-in C/C++/Java-flavored statement body lex and
parse successfully (see `tests/valid/valid_c_style.c`, `loops.cpp`,
`loops.java`). It is not a real C/C++/Java compiler: a full source
file with `class`/`void`/function declarations and a `main` wrapper
is not supported, only statement bodies are.

## Code Optimization

- Constant folding (e.g. `2 + 3 * 4` folds to `14` at compile time)
- Constant propagation on the generated TAC

See `tests/valid/valid_constant_folding.src` for a before/after example.

## Target Code Generation

- Simplified x86-style pseudo-assembly emitted from the optimized TAC
- Illustrative/educational only: no register allocation, linking, or a real assemblable backend

## Other Features

- Nested Blocks `{ ... }`
- Proper Scope Handling
- Single-line Comments (`//`)


---

# Project Structure

```
syntax-studio/
│
├── src/
│   ├── lexer/
│   ├── parser/
│   ├── ast/
│   ├── symbol_table/
│   ├── semantic/
│   ├── codegen/
│   └── main.c
│
├── tests/
│   ├── valid/
│   └── invalid/
│
├── examples/
│
├── docs/
│   ├── report/
│   └── images/
│
├── Makefile
├── README.md
└── LICENSE
```

---

# Requirements

- Ubuntu / Linux / WSL2
- GCC
- Flex
- Bison
- Make
- Git

Install dependencies:

```bash
sudo apt update
sudo apt install -y build-essential flex bison make git
```

---

# Build

```bash
make
```

Clean and rebuild:

```bash
make clean
make
```

---

# Run

Run the compiler with a source program:

```bash
./compiler tests/valid/valid_arithmetic_and_control_flow.src
```

A few more programs worth trying, each exercising a different part
of the pipeline:

```bash
./compiler tests/valid/valid_c_style.c              # C-flavored: #include, printf, for
./compiler tests/valid/loops.cpp                    # C++-flavored: cout, for, do-while
./compiler tests/valid/loops.java                   # Java-flavored: System.out.println
./compiler tests/valid/valid_constant_folding.src   # shows constant folding in the Optimization phase
./compiler tests/valid/valid_printf_multi_arg.src   # printf(...) with several arguments
```

`examples/` is reserved for a small curated set of demo programs
(work in progress); until it's populated, the commands above under
`tests/valid/` are the copy-pasteable working examples.

When the input is valid, the compiler prints the token stream, the parsed AST, the semantic analysis result, the TAC, the optimized TAC, and the generated assembly, in that order. When it's invalid, the pipeline stops at whichever phase failed and reports why the later phases didn't run.

## GUI

Syntax Studio also includes a Tkinter GUI for loading or typing a `.src` program and viewing the AST, semantic analysis result, TAC, and compiler errors in separate tabs.

Build the compiler first:

```bash
make
```

Then launch the GUI from the project root:

```bash
python3 gui/app.py
```

If the compiler binary is missing, the GUI will warn you and ask you to run `make` first.

# Development Status

| Module | Status |
|---------|--------|
| Project Structure | ✅ Completed |
| Build System | ✅ Completed |
| Lexer (incl. multi-language tokens) | ✅ Completed |
| Parser | ✅ Completed |
| AST | ✅ Completed |
| Symbol Table | ✅ Completed |
| Semantic Analysis | ✅ Completed |
| TAC Generation | ✅ Completed |
| Code Optimization | ✅ Completed |
| Target Code Generation | ✅ Completed |
| Example Tests | 🔄 In Progress |
| Documentation | 🔄 In Progress |

---

# Technologies Used

- C
- Flex
- GNU Bison
- GCC
- Make
- Git
- Ubuntu (WSL2)

---

# Learning Objectives

This project demonstrates the implementation of all six required phases of a compiler:

1. Lexical Analysis
2. Syntax Analysis (building the AST)
3. Semantic Analysis (building/querying the symbol table)
4. Intermediate Code Generation (Three Address Code)
5. Code Optimization (constant folding + constant propagation)
6. Target Code Generation (assembly)

The current implementation covers all six phases, plus a multi-language (C/C++/Java) front-end, for the supported language subset.

---

# License

This project was developed as part of the **Compiler Construction Lab** course at **Metropolitan University, Sylhet**.