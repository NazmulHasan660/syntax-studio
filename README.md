# Syntax Studio — Mini Compiler with Multi-Language Surface Support

A **6-phase mini compiler** developed using **GNU Flex** and **GNU Bison** for the **Compiler Construction Lab** course at **Metropolitan University, Sylhet**.

---

# 👥 Team Members & Responsibilities

## Nazmul Hasan
- Project Foundation, Architecture & Pipeline Integration (`main.c`)
- Lexical Analyzer (Flex)
- Syntax Analyzer (Bison)
- Abstract Syntax Tree (AST) Construction

## Mahdi Hasan Mehedi
- Symbol Table Design & Scope Management
- Semantic Analysis & Type Checking
- Intermediate Code Generation (Three-Address Code)
- Code Optimization & Pseudo-x86 Assembly Generator

## Both (Jointly Implemented)
- Graphical User Interface (GUI)
- Test Design, Documentation, Report, Slides, Demo & Viva Preparation

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

# 📝 Supported Languages & Example Programs

Syntax Studio compiles its own custom **Mini/C** language, and also reads C, C++, and Java source files by recognizing their surface syntax (function wrapper, `#include`, `cout`, `printf`, `System.out.println`, `for`, `do-while`, `++`/`--`).

**Mini/C** (`examples/sample.src`):

```c
int a;
int b;
bool valid;

a = 12;
b = 5;
valid = true;

int total;
total = a + b * 2;

if (total > 15 && valid) {
    print total;
} else {
    print a;
}
```

**C** (`examples/c_with_main.c`):

```c
#include <stdio.h>

int main(int argc, char** argv) {
    int x = 10;
    int y = 20;
    int sum = x + y;

    if (sum > 20) {
        printf(sum);
    } else {
        printf(x);
    }

    return 0;
}
```

**C++** (`examples/cpp_with_main.cpp`):

```cpp
#include <iostream>
using namespace std;

int main() {
    int count = 0;

    while (count < 3) {
        cout << count;
        count++;
    }

    return 0;
}
```

**Java** (`examples/java_with_main.java`):

```java
public class JavaMainTest {
    public static void main(String[] args) {
        int total = 0;

        for (int i = 1; i <= 3; i++) {
            total = total + i;
            System.out.println(total);
        }
    }
}
```

Run any of these with `./compiler <file>` — the language is auto-detected from the file extension.

---

# ✅ What It Accepts / ❌ What It Doesn't

**Accepts**
- `int`, `float`, `bool` variable declarations and assignment
- Arithmetic (`+ - * / %`), relational (`< > <= >= == !=`), and logical (`&& || !`) expressions with correct precedence
- `if`, `if-else`, `while`, nested `{ }` blocks with proper scoping
- `for` and `do-while` loops, `++` / `--` on identifiers (C/C++/Java surface syntax)
- `print`, `cout <<`, and single-argument `printf(...)` / `System.out.println(...)`
- A single `main()`-style function wrapper and a single `class` wrapper, so real-looking C/C++/Java files parse
- `#include` directives and `using namespace` lines (recognized and ignored, not processed)
- Single-line `//` comments

**Does not accept**
- Arrays or indexing
- Strings as an assignable data type (string literals only work as a single `print`/`cout`/`printf` argument)
- User-defined functions beyond the single `main()` wrapper — no function calls, parameters, or return values
- Multiple classes, class fields/methods, inheritance, or object creation
- `switch`/`case`
- Multiple chained outputs in one statement (`cout << a << b`, `printf` with several arguments)
- Pointers (`char*` is only recognized as a parameter type, not usable as a real pointer)
- Running the generated assembly — the pseudo-x86 output is text only; it is not assembled or executed

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
./compiler examples/sample.src
./compiler examples/c_with_main.c
./compiler examples/cpp_with_main.cpp
./compiler examples/java_with_main.java
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
│   ├── grammar.md              # Formal CFG (BNF), precedence & associativity
│   ├── architecture.md         # Pipeline diagram & module map
│   ├── images/                 # Screenshots: builds, runs, error handling
│   └── report/
│       └── PROJECT_REPORT.md   # Full written project report
│
├── src/
│   ├── lexer/lexer.l           # Flex rules — tokenizes source, tracks lines
│   ├── parser/parser.y         # Bison grammar — builds the AST
│   ├── ast/                    # AST node types, construction, pretty-print
│   ├── semantic/                # Type checking & semantic error detection
│   ├── symbol_table/           # Scoped symbol table (insert/lookup/scope)
│   ├── codegen/                # TAC generator + pseudo-x86 assembly generator
│   └── optimizer/              # Constant folding & constant propagation
│
├── tests/
│   ├── valid/                  # Programs expected to compile through to TAC
│   ├── invalid/lexical/        # Programs with bad tokens (expect failure)
│   ├── invalid/syntax/         # Grammar-violating programs (expect failure)
│   ├── invalid/semantic/       # One test per required semantic rule
│   └── run_all.sh              # Runs every test, prints a pass/fail summary
│
├── examples/                   # Sample Mini/C, C, C++, and Java programs
│
├── gui/                        # Python/Tkinter GUI for visualizing all phases
│
├── Makefile                    # `make` builds the compiler binary
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

# 🔮 Future Scope

- **Real function definitions** — parameters, return values, and actual call/return semantics instead of a single `main()` wrapper
- **Function calls** — invoke a defined function and use its returned value in an expression
- **Execution, not just generation** — assemble and run the pseudo-x86 output (or interpret the TAC directly) so the compiler shows real program output, not just generated code
- **Arrays and indexing**
- **String as a first-class type** — declarable and assignable, not just a print argument
- **Multi-argument output** — `printf` with multiple arguments, chained `cout << a << b`
- **switch/case statements**

---

# 📄 License

This project was developed as part of the **Compiler Construction Lab** course at **Metropolitan University, Sylhet**.