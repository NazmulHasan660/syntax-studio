# Syntax Studio — Mini Compiler with Multi-Language Surface Support

A **6-phase mini compiler** developed using **GNU Flex** and **GNU Bison** for the **Compiler Construction Lab** course at **Metropolitan University, Sylhet**.

---

# 👥 Team Members & Responsibilities

## Nazmul Hasan
- Project Foundation & Architecture
- Lexical Analyzer (Flex)
- Syntax Analyzer (Bison)
- Abstract Syntax Tree (AST) Construction

## Mahdi Hasan Mehedi
- Symbol Table Design & Scope Management
- Semantic Analysis & Type Checking
- Intermediate Code Generation (Three-Address Code)
- Code Optimization & Pseudo-x86 Assembly Generator
- Graphical User Interface (GUI)

---

# 🚀 Compiler Pipeline (6 Phases)

1. **Lexical Analysis (Flex)**
   - Tokenizes source code
   - Removes whitespace, comments, and directives

2. **Syntax Analysis (Bison)**
   - Parses grammar
   - Handles precedence and dangling-else ambiguity

3. **Abstract Syntax Tree (AST)**
   - Constructs a clean hierarchical AST

4. **Semantic Analysis & Symbol Table**
   - Type checking
   - Scope management
   - Undeclared/redeclaration detection

5. **Intermediate Code Generation**
   - Generates Three-Address Code (TAC)

6. **Optimization & Target Assembly**
   - Constant folding
   - Constant propagation
   - Generates pseudo-x86 assembly

---

# 🛠️ Build & Run Instructions

## Prerequisites

Install the required tools:

```bash
sudo apt update
sudo apt install -y build-essential flex bison make
```

---

## Build

```bash
make
```

---

## Run Compiler

Compile any supported source file:

```bash
./compiler examples/c_with_main.c
```

---

## Run Test Suite

```bash
./tests/run_all.sh
```

---

## Launch GUI

```bash
python3 gui/app.py
```

---

# 📂 Project Structure

```text
syntax-studio/
├── docs/
│   ├── grammar.md
│   ├── architecture.md
│   ├── images/
│   └── report/
│       └── PROJECT_REPORT.md
│
├── src/
│   ├── lexer/
│   ├── parser/
│   ├── ast/
│   ├── semantic/
│   ├── symbol_table/
│   ├── codegen/
│   └── optimizer/
│
├── tests/
│
├── examples/
│
├── gui/
│
├── Makefile
└── README.md
```

---

# 📚 Documentation

Detailed documentation is available in the **docs/** directory.

| Document | Description |
|----------|-------------|
| `grammar.md` | Formal Context-Free Grammar (CFG) |
| `architecture.md` | Compiler Architecture & Data Flow |
| `report/PROJECT_REPORT.md` | Complete Project Report |

---

# ✅ Features

- Flex-based Lexical Analyzer
- Bison-based LALR(1) Parser
- Abstract Syntax Tree (AST)
- Nested Scope Symbol Table
- Semantic Analysis
- Three-Address Code (TAC)
- Constant Folding & Propagation
- Pseudo-x86 Assembly Generation
- Python/Tkinter GUI
- Multi-language Surface Support (C, C++, Java)

---

# 🧪 Testing

The compiler has been tested using **23 test cases**.

| Category | Status |
|----------|--------|
| Valid Programs | ✅ Passed |
| Invalid Programs | ✅ Passed |

### Overall Result

```text
23 Passed
0 Failed
```

---

# 📄 License

This project was developed as part of the **Compiler Construction Lab** course at **Metropolitan University, Sylhet**.