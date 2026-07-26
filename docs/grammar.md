# Formal Grammar (CFG)

This is the context-free grammar actually implemented in
src/parser/parser.y, written out in BNF for the project report
(Section 12 of the manual requires this).

    Program        -> StatementList

    StatementList  -> StatementList Statement
                    |  (empty)

    Statement      -> Declaration
                    |  Assignment
                    |  IfStatement
                    |  WhileStatement
                    |  PrintStatement
                    |  Block
                    |  error ';'          (error recovery)

    Block          -> '{' StatementList '}'

    Declaration    -> Type ID ';'

    Type           -> 'int' | 'float' | 'bool'

    Assignment     -> ID '=' Expression ';'

    IfStatement    -> 'if' '(' Expression ')' Block
                    |  'if' '(' Expression ')' Block 'else' Block

    WhileStatement -> 'while' '(' Expression ')' Block

    PrintStatement -> 'print' Expression ';'

    Expression     -> Expression '||' Expression
                    |  Expression '&&' Expression
                    |  Expression '==' Expression
                    |  Expression '!=' Expression
                    |  Expression '<'  Expression
                    |  Expression '>'  Expression
                    |  Expression '<=' Expression
                    |  Expression '>=' Expression
                    |  Expression '+'  Expression
                    |  Expression '-'  Expression
                    |  Expression MUL_SYMBOL Expression
                    |  Expression '/'  Expression
                    |  Expression '%'  Expression
                    |  '!' Expression
                    |  '-' Expression     (unary minus -- bonus feature)
                    |  '(' Expression ')'
                    |  ID
                    |  INT_CONST
                    |  FLOAT_CONST
                    |  'true'
                    |  'false'

    (MUL_SYMBOL above is the multiplication operator, written as a
    single asterisk character between quotes in the actual grammar.)

## Operator precedence & associativity

Lowest to highest (matches the %left / %right declarations in parser.y):

    Level 1 (lowest)   : OR   (||)              -- left
    Level 2            : AND  (&&)               -- left
    Level 3            : EQ NEQ (== !=)          -- left
    Level 4            : LT GT LE GE (< > <= >=) -- left
    Level 5            : PLUS MINUS (+ -, binary)-- left
    Level 6            : MUL DIV MOD             -- left
    Level 7 (highest)  : NOT, unary MINUS (!, -) -- right

Unary minus is given its own precedence level (declared as UMINUS in
parser.y) so that "-a MUL b" parses as "(-a) MUL b" and not
"-(a MUL b)", and so that "x - -1" is unambiguous.

## Notes for the report

- This grammar is unambiguous: every binary operator has an explicit
  precedence/associativity declaration, so there are no
  shift/reduce conflicts on operator combinations (bison -d produces
  no conflict warnings for this grammar as written).
- The error-recovery rule (error token followed by a semicolon) is
  Bison's built-in error-recovery mechanism: on a malformed
  statement, the parser discards tokens up to the next semicolon
  and resumes, so later errors in the same file are still detected
  instead of the compiler stopping at the first one.
- Unary minus is not part of the mandatory language spec (Section 5
  of the manual only lists binary arithmetic operators) -- it is
  included as an optional bonus extension (Section 14: "Unary
  operators, increment/decrement").
