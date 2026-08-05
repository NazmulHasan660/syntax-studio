# PROJECT REPORT: Syntax Studio
## A Mini Programming Language Compiler using Flex and Bison

---

## Course Information

**Course:** Compiler Construction Lab  
**Department:** Department of Computer Science and Engineering  
**Institution:** Metropolitan University, Sylhet, Bangladesh  

---

## Project Information

**Project Title:** Design and Implement a Mini Programming Language Compiler using Flex and Bison  
**Project Repository:** Syntax Studio  

---

## Team Members

| Name | Student ID |
|------|------------|
| Nazmul Hasan | 231-115-164 |
| Mahdi Hasan Mehedi | 222-115-139 |

---

# 5. Introduction

Compilers form the foundational bridge between human-readable source code and high-level execution models. The Compiler Construction Laboratory course concludes with a comprehensive group project requiring the implementation of a functional compiler front-end and intermediate code generator.

**Syntax Studio** is a mini compiler constructed using **GNU Flex** (Lexical Analyzer Generator) and **GNU Bison** (Parser Generator). It translates a statically-typed imperative custom language—alongside supporting standard C, C++, and Java surface syntax—into **Three-Address Code (TAC)**, optimized TAC, and illustrative x86-style pseudo-assembly.

Rather than studying compiler phases in isolation, Syntax Studio integrates a complete software pipeline comprising:

- Lexical Analysis
- Syntax Analysis
- Abstract Syntax Tree (AST) Construction
- Symbol Table Management
- Semantic Analysis
- Intermediate Code Generation
- Optimization
- Target Assembly Generation

Additionally, the project includes a **Python/Tkinter GUI** capable of visualizing:

- Tokens
- AST
- Symbol Table
- TAC
- Optimized TAC
- Assembly Output
- Diagnostic Errors

---

# 6. Objectives

The primary objectives of this project are:

- **Phase Integration**
  - Demonstrate how compiler phases communicate and interact.

- **Formal Grammar Implementation**
  - Implement an unambiguous CFG handling precedence, associativity, and dangling-else ambiguity.

- **AST & Scope Management**
  - Construct a clean AST and implement nested block-scoped symbol tables.

- **Error Detection**
  - Detect lexical, syntax, and semantic errors with informative diagnostics.

- **Multi-language Support**
  - Accept standard C, C++, and Java outer syntax such as:
    - `#include`
    - `using namespace`
    - `import`
    - `package`
    - Access modifiers
    - `main()` definitions

- **Intermediate Code Generation**
  - Produce TAC, optimize it, and generate pseudo-x86 assembly.

---

# 7. Language Specification

## 7.1 Custom Language Core

The language is a statically typed imperative language supporting:

- Integer
- Float
- Boolean
- Conditional Statements
- Loops
- Print Statements

### Data Types

| Type | Description |
|------|-------------|
| `int` | Signed Integer |
| `float`, `double` | Floating-point |
| `bool`, `boolean` | Boolean |
| `void` | Function return type |

---

## Operators

### Arithmetic

```text
+  -  *  /  %
```

### Relational

```text
<  >  <=  >=  ==  !=
```

### Logical

```text
&&  ||  !
```

### Unary

```text
-   ++   --
```

---

## 7.2 Context-Free Grammar (BNF)

```bnf
Program ::= OuterDeclarations

OuterDeclarations ::= OuterDeclarations TopLevelItem
                    | ε

TopLevelItem ::= ClassDeclaration
               | FunctionDefinition
               | Statement

ClassDeclaration ::= 'class' ID '{' OuterDeclarations '}'

FunctionDefinition ::= Type ID '(' ParamList ')' Block

ParamList ::= ParamListItems | ε

ParamListItems ::= ParamItem
                 | ParamListItems ',' ParamItem

ParamItem ::= Type ID
            | Type ID '[' ']'
            | 'String' '[' ']' ID
            | 'char' '*' ID
            | 'char' '*' '*' ID
            | 'void'

StatementList ::= StatementList Statement
                | ε

Statement ::= Declaration
            | Assignment
            | IfStatement
            | WhileStatement
            | ForStatement
            | DoWhileStatement
            | ReturnStatement
            | PrintStatement
            | Block
            | ';'
            | error ';'

Block ::= '{' StatementList '}'

Declaration ::= Type DeclList ';'

Type ::= 'int'
       | 'float'
       | 'bool'
       | 'void'

Assignment ::= ID '=' Expression ';'
             | ID '++' ';'
             | ID '--' ';'

IfStatement ::= 'if' '(' Expression ')' Statement
              | 'if' '(' Expression ')' Statement 'else' Statement

WhileStatement ::= 'while' '(' Expression ')' Statement

ForStatement ::= 'for' '(' ForInit ';' Expression ';' ForUpdate ')' Statement

DoWhileStatement ::= 'do' Statement 'while' '(' Expression ')' ';'

ReturnStatement ::= 'return' Expression ';'
                  | 'return' ';'

PrintStatement ::= 'print' Expression ';'
                 | 'cout' '<<' Expression ';'
                 | 'printf' '(' ExpressionList ')' ';'

Expression ::= Expression '||' Expression
             | Expression '&&' Expression
             | Expression '==' Expression
             | Expression '!=' Expression
             | Expression '<' Expression
             | Expression '>' Expression
             | Expression '<=' Expression
             | Expression '>=' Expression
             | Expression '+' Expression
             | Expression '-' Expression
             | Expression '*' Expression
             | Expression '/' Expression
             | Expression '%' Expression
             | '!' Expression
             | '-' Expression
             | '(' Expression ')'
             | ID
             | INT_CONST
             | FLOAT_CONST
             | STRING_LITERAL
             | 'true'
             | 'false'
```

---

# 8. Compiler Architecture

```text
           Source Program
   (.c / .cpp / .java / .src)
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
 Semantic Analyzer & Symbol Table
                 │
                 ▼
     TAC Code Generation
                 │
                 ▼
  Optimizer & Assembly Generator
                 │
                 ▼
     Pseudo-x86 Assembly Output
```

---

# 9. Lexer Design

Implemented in:

```
src/lexer/lexer.l
```

### Features

- Tokenization
- Ignores comments
- Ignores whitespace
- Ignores compiler directives
- Line number tracking
- Longest-match token recognition
- Lexical error reporting

---

# 10. Parser Design

Implemented in:

```
src/parser/parser.y
```

### Operator Precedence

| Level | Operators |
|---------|-----------|
| Lowest | `||` |
| | `&&` |
| | `== !=` |
| | `< > <= >=` |
| | `+ -` |
| | `* / %` |
| | `!` |
| Highest | Unary `-` |

### Ambiguity Resolution

- Dangling Else resolved using Bison precedence rules.
- Error recovery implemented via:

```text
Statement → error ';'
```

---

# 11. Abstract Syntax Tree

Implemented in:

```
src/ast/
```

### AST Node Structure

```c
typedef struct ASTNode {
    NodeType type;
    char *text;
    char *data_type;
    int line;
    struct ASTNode *left;
    struct ASTNode *right;
    struct ASTNode *third;
    struct ASTNode *next;
} ASTNode;
```

Features:

- Clean hierarchical tree
- NodeType enumeration
- Tree visualization support

---

# 12. Semantic Analysis

Implemented in:

```
src/semantic/
```

### Semantic Checks

- Undeclared variables
- Redeclaration
- Scope validation
- Type compatibility
- Implicit widening
- Boolean expression validation

---

# 13. Symbol Table

Implemented in:

```
src/symbol_table/
```

Stores:

- Variable Name
- Data Type
- Scope Level
- Declaration Line

Supports nested scopes through stack-based scope management.

---

# 14. Intermediate Code Generation

Implemented in:

```
src/codegen/
```

Produces:

- Three Address Code (TAC)
- Optimized TAC
- Pseudo-x86 Assembly

### Example

Source

```c
int a = 5;
int b = 10;
int c = a + b * 2;
```

Generated TAC

```text
a = 5
b = 10
t0 = b * 2
t1 = a + t0
c = t1
```

Optimizations

- Constant Folding
- Constant Propagation

---

# 15. Challenges

| Challenge | Solution |
|-----------|----------|
| Unknown tokens | Wildcard lexer rule |
| Dangling Else | Bison precedence |
| C/C++/Java parsing | Extended grammar |
| Empty Symbol Table | Scope history list |

---

# 16. Testing

The compiler was tested using **23 programs**.

## Valid Programs

- Arithmetic
- Conditions
- Nested Scope
- Loops
- C++
- Java

**Result**

```text
PASS
```

---

## Invalid Programs

- Lexical Errors
- Syntax Errors
- Semantic Errors
- Scope Errors
- Type Mismatch
- Undeclared Variables

**Result**

```text
PASS
```

---

### Final Summary

```text
23 Passed
0 Failed
```

---

# 17. Conclusion

Syntax Studio successfully demonstrates the complete compiler pipeline using Flex and Bison.

The project includes:

- Lexical Analysis
- Parsing
- AST Construction
- Semantic Analysis
- Symbol Table
- TAC Generation
- Optimization
- Assembly Generation
- GUI Visualization

---

## Lessons Learned

- Interaction between lexer and parser
- Nested scope management
- Intermediate code generation
- Compiler optimization techniques

---

# 18. References

1. Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley.

2. Levine, J. R., Mason, T., & Brown, D. (1992). *lex & yacc* (2nd ed.). O'Reilly.

3. GNU Flex Manual

   https://github.com/westes/flex

4. GNU Bison Manual

   https://www.gnu.org/software/bison/manual/

5. Compiler Construction Lab Manual, Department of CSE, Metropolitan University.