# Mini Programming Language Compiler

A compiler front-end for a custom programming language developed for the **Compiler Construction Lab** at **Metropolitan University, Bangladesh**.

The project implements the core stages of a compiler, including lexical analysis, syntax analysis, semantic analysis, Abstract Syntax Tree (AST) construction, symbol table management, and Three Address Code (TAC) generation. A lightweight Django-based web interface is included for interactive code compilation and testing.

## ✨ Features

- **Lexical Analysis (Flex):** Tokenizes source code into keywords, identifiers, constants, operators, and delimiters while ignoring comments and whitespace.
- **Syntax Analysis (Bison):** Validates program structure using a Context-Free Grammar (CFG).
- **Abstract Syntax Tree (AST):** Builds a hierarchical representation of the parsed program.
- **Symbol Table & Scope Management:** Supports nested scopes and tracks variable declarations and data types (`int`, `float`, `bool`).
- **Semantic Analysis:** Detects undeclared variables, redeclarations, and type mismatches.
- **Three Address Code (TAC):** Generates intermediate code for valid programs.
- **Django Web Interface:** Provides a browser-based editor to compile source code and display compiler output in real time.

## 🛠 Prerequisites

- GCC
- Flex
- Bison
- Make
- Python 3
- Django

## 🚀 Build & Run

### Compile the Compiler

```bash
make clean
make
```

### Run the Web Interface

```bash
cd webapp
python manage.py runserver
```

Open your browser and visit:

```text
http://localhost:8000
```

### Run from the Terminal

```bash
./my_compiler tests/sample_program.txt
```

## 📁 Project Structure

```text
project-root/
├── src/
│   ├── lexer/
│   ├── parser/
│   ├── ast/
│   ├── semantic/
│   └── symbol_table/
├── webapp/
├── docs/
├── tests/
├── examples/
├── Makefile
└── README.md
```

