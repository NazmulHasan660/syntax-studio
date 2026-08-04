# Formal Grammar (CFG)

This is the context-free grammar actually implemented in
src/parser/parser.y, written out in BNF for the project report
(Section 12 of the manual requires this).

    Program          -> OuterDeclarations

    OuterDeclarations -> OuterDeclarations Statement
                      |  (empty)

    StatementList    -> StatementList Statement
                      |  (empty)

    Statement        -> Declaration
                      |  Assignment
                      |  IfStatement
                      |  WhileStatement
                      |  ForStatement
                      |  DoWhileStatement
                      |  ReturnStatement
                      |  PrintStatement
                      |  Block
                      |  ';'
                      |  error ';'          (error recovery)

    Block            -> '{' StatementList '}'

    Declaration      -> Type DeclList ';'

    Type             -> 'int' | 'float' | 'bool'

    Assignment       -> ID '=' Expression ';'
                      |  ID '++' ';'
                      |  ID '--' ';'

    IfStatement      -> 'if' '(' Expression ')' Statement
                      |  'if' '(' Expression ')' Statement 'else' Statement

    WhileStatement   -> 'while' '(' Expression ')' Statement

    ForStatement     -> 'for' '(' ForInit ';' Expression ';' ForUpdate ')' Statement

    DoWhileStatement -> 'do' Statement 'while' '(' Expression ')' ';'

    ReturnStatement  -> 'return' Expression ';'
                      |  'return' ';'

    PrintStatement   -> 'print' Expression ';'
                      |  'cout' '<<' Expression ';'
                      |  'printf' '(' ExpressionList ')' ';'

    Expression       -> Expression '||' Expression
                      |  Expression '&&' Expression
                      |  Expression '==' Expression
                      |  Expression '!=' Expression
                      |  Expression '<'  Expression
                      |  Expression '>'  Expression
                      |  Expression '<=' Expression
                      |  Expression '>=' Expression
                      |  Expression '+'  Expression
                      |  Expression '-'  Expression
                      |  Expression '*'  Expression
                      |  Expression '/'  Expression
                      |  Expression '%'  Expression
                      |  '!' Expression
                      |  '-' Expression            (unary minus)
                      |  '(' Expression ')'
                      |  ID
                      |  INT_CONST
                      |  FLOAT_CONST
                      |  STRING_LITERAL
                      |  'true'
                      |  'false'

## Operator precedence & associativity

Lowest to highest (matches the %left / %precedence declarations in
parser.y):

    Level 1 (lowest)   : OR   (||)              -- left
    Level 2            : AND  (&&)               -- left
    Level 3            : EQ NEQ (== !=)          -- left
    Level 4            : LT GT LE GE (< > <= >=) -- left
    Level 5            : PLUS MINUS (+ -, binary)-- left
    Level 6            : MUL DIV MOD             -- left
    Level 7            : NOT (!)                 -- right (%precedence)
    Level 8 (highest)  : UMINUS (unary -)         -- right (%precedence)

    dangling-else      : resolved by LOWER_THAN_ELSE / ELSE
                          precedence, so 'if (a) if (b) s1; else s2;'
                          attaches the 'else' to the nearest 'if',
                          matching every mainstream language.

Unary minus (`-x`) is required per the instructor's confirmed
six-phase + multi-language specification (previously treated as an
optional Section 14 bonus in an earlier draft of this document; the
instructor has since clarified it is part of the required language).
It is
implemented with a dedicated `%prec UMINUS` rule so that `a - -b`
parses unambiguously as `a - (-b)` and `-a * b` parses as `(-a) * b`,
matching standard C-family precedence. Semantically it requires a
numeric (`int` or `float`) operand and preserves that operand's type;
applying it to a `bool` is a semantic error, symmetric with how `!`
requires a `bool` operand.

## Notes for the report

- This grammar is unambiguous: `bison -d src/parser/parser.y`
  produces zero shift/reduce and zero reduce/reduce conflicts as
  currently written. Every binary operator has an explicit
  precedence/associativity declaration, and the one classic ambiguity
  in the language (dangling else) is resolved with the
  LOWER_THAN_ELSE / ELSE precedence trick above instead of being left
  as an unresolved conflict.
- The error-recovery rule (`error ';'`) is Bison's built-in
  error-recovery mechanism: on a malformed statement, the parser
  discards tokens up to the next semicolon and resumes with
  `yyerrok`, so later errors in the same file are still detected
  instead of the compiler stopping at the first one. See
  `tests/invalid/syntax/multiple_errors_recovery.src`, which
  intentionally contains two separate syntax errors and gets both
  reported in a single run.
- `for`, `do-while`, `++`/`--`, and the `cout <<` / `printf(...)`
  print forms are required per the instructor's confirmed six-phase
  + multi-language specification (an earlier draft of this document
  called them optional Section 14 extras; that framing is outdated
  now that the instructor has confirmed multi-language C/C++/Java
  surface support, loops, and unary/increment operators are part of
  the required scope, not bonus work).
  `return` is accepted syntactically but is a documented no-op in
  semantic analysis and TAC generation (see the comments in
  `semantic.c` and `tac.c`) -- this project intentionally does not
  implement user-defined functions or function calls, so `return`
  never appears inside a real call frame.
- The lexer additionally tolerates (and silently ignores) a handful
  of real C++/Java tokens that a pasted-in C++/Java snippet would
  contain but that this language subset does not itself use:
  `#include ...`, `using namespace ...`, `import ...`, `package ...`,
  and access/storage modifiers (`public`, `private`, `protected`,
  `static`, `final`, `const`). This is why
  `tests/valid/loops.cpp` and `tests/valid/loops.java` -- real
  C++-flavored and Java-flavored source -- lex and parse successfully
  even though this is not a C++ or Java compiler. It does not,
  however, understand `class`/`void`/function declarations, so a
  full real C++/Java file with a `main` wrapper (`int main() {...}`,
  `class Main { public static void main(...) {...} }`) will still be
  rejected -- only the statement bodies are supported, not function
  or class syntax.
- `printf(ExpressionList)` accepts more than one comma-separated
  expression (e.g. `printf("Result:", sum);`), matching the grammar
  above. Each expression in the list becomes its own `print` line in
  the generated TAC, in source order -- there is no printf-style
  format-string substitution (`%d` etc. is not interpreted; a string
  literal argument is just printed as a literal string). An earlier
  build only evaluated the first expression in the list and silently
  dropped the rest; this is fixed as of the current `semantic.c` /
  `tac.c`.