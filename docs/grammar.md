# Formal Grammar (CFG) Specification

This document contains the formal Context-Free Grammar (CFG) implemented in `src/parser/parser.y` for **Syntax Studio** in Backus-Naur Form (BNF).

---

## Context-Free Grammar in BNF Notation

```bnf
Program          ::= OuterDeclarations

OuterDeclarations ::= OuterDeclarations TopLevelItem
                  |  ε

TopLevelItem     ::= ClassDeclaration
                  |  FunctionDefinition
                  |  Statement

ClassDeclaration ::= 'class' ID '{' OuterDeclarations '}'

FunctionDefinition ::= Type ID '(' ParamList ')' Block

ParamList        ::= ParamListItems
                  |  ε

ParamListItems   ::= ParamItem
                  |  ParamListItems ',' ParamItem

ParamItem        ::= Type ID
                  |  Type ID '[' ']'
                  |  'String' '[' ']' ID
                  |  'char' '*' ID
                  |  'char' '*' '*' ID
                  |  'void'
                  |  ID ID

StatementList    ::= StatementList Statement
                  |  ε

Statement        ::= Declaration
                  |  Assignment
                  |  IfStatement
                  |  WhileStatement
                  |  ForStatement
                  |  DoWhileStatement
                  |  ReturnStatement
                  |  PrintStatement
                  |  Block
                  |  ';'
                  |  error ';'

Block            ::= '{' StatementList '}'

Declaration      ::= Type DeclList ';'

Type             ::= 'int' | 'float' | 'bool' | 'void'

Assignment       ::= ID '=' Expression ';'
                  |  ID '++' ';'
                  |  ID '--' ';'

IfStatement      ::= 'if' '(' Expression ')' Statement
                  |  'if' '(' Expression ')' Statement 'else' Statement

WhileStatement   ::= 'while' '(' Expression ')' Statement

ForStatement     ::= 'for' '(' ForInit ';' Expression ';' ForUpdate ')' Statement

DoWhileStatement ::= 'do' Statement 'while' '(' Expression ')' ';'

ReturnStatement  ::= 'return' Expression ';'
                  |  'return' ';'

PrintStatement   ::= 'print' Expression ';'
                  |  'cout' '<<' Expression ';'
                  |  'printf' '(' ExpressionList ')' ';'

ExpressionList   ::= ExpressionList ',' Expression
                  |  Expression
                  |  ε

Expression       ::= Expression '||' Expression
                  |  Expression '&&' Expression
                  |  Expression '==' Expression | Expression '!=' Expression
                  |  Expression '<' Expression  | Expression '>' Expression
                  |  Expression '<=' Expression | Expression '>=' Expression
                  |  Expression '+' Expression  | Expression '-' Expression
                  |  Expression '*' Expression  | Expression '/' Expression | Expression '%' Expression
                  |  '!' Expression
                  |  '-' Expression
                  |  '(' Expression ')'
                  |  ID
                  |  INT_CONST
                  |  FLOAT_CONST
                  |  STRING_LITERAL
                  |  'true'
                  |  'false'
```

---

## Operator Precedence & Associativity Table

Lowest to highest precedence (matching `%left` and `%precedence` declarations in `src/parser/parser.y`):

| Precedence Level | Operators | Associativity | Description |
|------------------|-----------|---------------|-------------|
| Level 1 (Lowest) | `||` | Left | Logical OR |
| Level 2 | `&&` | Left | Logical AND |
| Level 3 | `==`, `!=` | Left | Equality & inequality comparison |
| Level 4 | `<`, `>`, `<=`, `>=` | Left | Relational comparison |
| Level 5 | `+`, `-` | Left | Binary addition and subtraction |
| Level 6 | `*`, `/`, `%` | Left | Multiplication, division, modulo |
| Level 7 | `!` | Right | Logical NOT |
| Level 8 (Highest) | `-` (unary) | Right | Unary minus (`%prec UMINUS`) |

---

## Dangling-Else Resolution

The classic "dangling-else" ambiguity (`if (a) if (b) s1; else s2;`) is resolved using Bison's `%precedence LOWER_THAN_ELSE` and `%precedence ELSE` declarations. This explicitly attaches the `else` clause to the nearest inner `if` statement, matching standard C, C++, and Java semantics.

---

## Design & Notes for Project Presentation

### Zero Ambiguities

Running `bison -d src/parser/parser.y` produces **0 shift/reduce** and **0 reduce/reduce** conflicts. Every operator has an explicit precedence and associativity declaration.

### Error Recovery (`error ';'`)

Uses Bison's built-in error recovery mechanism. On encountering a syntax error in a statement, the parser discards tokens up to the next semicolon (`;`), invokes `yyerrok`, and continues parsing subsequent statements rather than abruptly aborting compilation.

### Multi-Language Surface Syntax & Full Main Support

- Directives (`#include ...`, `using namespace ...`, `import ...`, `package ...`) and access modifiers (`public`, `private`, `protected`, `static`, `final`, `const`) are recognized and silently discarded by the lexer.
- Top-level constructs support class declarations and `main()` function signatures with parameters (such as `int main()`, `int main(int argc, char** argv)`, and `public static void main(String[] args)`).
- Multiple print forms are fully supported (`print expr;`, `cout << expr;`, `printf(expr1, expr2, ...);`, `System.out.println(expr);`).

### Unary Minus (`-x`)

Implemented with a dedicated `%prec UMINUS` rule so that `-a * b` parses unambiguously as `(-a) * b` and `a - -b` parses as `a - (-b)`.