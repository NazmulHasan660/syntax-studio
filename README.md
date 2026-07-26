
### A Mini Compiler for a Simplified Statically-Typed Language using Flex & Bison

**Course:** Compiler Construction Lab  
**Department:** Computer Science and Engineering  
**University:** Metropolitan University, Sylhet, Bangladesh

---

# Project Goal

Syntax Studio is a mini compiler developed using Flex and Bison. It implements lexical analysis, syntax analysis, abstract syntax tree (AST) construction, symbol table management, semantic analysis, and intermediate code generation using Three Address Code (TAC).

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

---

# Compiler Pipeline

```
Source Program
      │
      ▼
Lexical Analyzer (Flex)
      │
      ▼
Syntax Analyzer (Bison)
      │
      ▼
Abstract Syntax Tree (AST)
      │
      ▼
Symbol Table Construction
      │
      ▼
Semantic Analysis
      │
      ▼
Three Address Code (TAC)
```

---

# Supported Language Features

## Data Types

- int
- float
- bool

## Statements

- Variable Declaration
- Assignment
- Arithmetic Expressions
- Relational Expressions
- Logical Expressions
- if
- if-else
- while
- print

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
./compiler examples/test1.src
```

You can also test other example programs:

```bash
./compiler examples/test2.src
./compiler examples/test3.src
```

When the input is valid, the compiler prints the parsed AST, runs semantic analysis, and then emits TAC.

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
| Lexer | ✅ Completed |
| Parser | ✅ Completed |
| AST | ✅ Completed |
| Symbol Table | ✅ Completed |
| Semantic Analysis | ✅ Completed |
| TAC Generation | ✅ Completed |
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

This project demonstrates the implementation of the major phases of a compiler:

- Lexical Analysis
- Syntax Analysis
- Abstract Syntax Tree Construction
- Symbol Table Management
- Semantic Analysis
- Intermediate Code Generation (Three Address Code)

The current implementation covers all of these stages for the supported language subset.

---

# License

This project was developed as part of the **Compiler Construction Lab** course at **Metropolitan University, Sylhet**.

