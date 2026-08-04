# Project Report -- Outline

Section numbers/titles match Section 12 of the Project Manual, with
two chapters added (Code Optimization, Target Code Generation) to
match the instructor-confirmed six-phase pipeline: Lexer -> Parser ->
Semantic Analysis -> Intermediate Code -> Code Optimization -> Target
Code Generation.

This file only has headers and a short prompt under each one --
you and Mahdi need to write the actual content yourselves. Per
Section 10 of the manual, you have to be able to explain anything
in the report (and the code) in the individual viva, so don't
paste in anything you can't defend on the spot.

IMPORTANT: get the instructor's six-phase + multi-language
requirement in writing somewhere (announcement screenshot, email,
slide) and reference/attach it here. It overrides the written
project manual's "do not generate assembly" line, and you want that
on record before grading, not just remembered from a class comment.

## 1. Introduction
Why does a compiler course end in a project like this instead of a
written final? What does Syntax Studio do, one paragraph. Mention
up front that the compiler targets a fixed core language but also
accepts common C/C++/Java surface syntax (per the instructor's
six-phase + multi-language clarification), so the reader isn't
surprised later by `cout`/`printf`/`System.out.println` all working.

## 2. Objectives
What was each of you trying to demonstrate you understood by
building this? Tie back to all six phases now required: lexer,
parser, semantic analysis, intermediate code, code optimization,
target code generation -- plus the multi-language front-end.

## 3. Language Specification
Restate the language from Section 5 of the manual in your own
words: data types, statements, operators. Include the formal CFG --
see docs/grammar.md, already derived from your actual parser.y.
Also describe the multi-language surface syntax explicitly as a
required feature (not a bonus): which C/C++/Java constructs are
recognized (`#include`, `using namespace`, `import`, `package`,
access modifiers, `cout`, `printf`, `System.out.println`, `boolean`/
`double` aliases) and which are deliberately NOT supported (classes,
functions, a `main` wrapper) -- state this as a scoping decision.

## 4. Compiler Architecture
State the six phases explicitly and keep the count at six: (1) Lexer,
(2) Parser, (3) Semantic Analysis, (4) Intermediate Code, (5) Code
Optimization, (6) Target Code Generation. AST construction and symbol
table management are NOT separate phases -- they are artifacts/work
done inside the Parser phase (AST) and the Semantic Analysis phase
(symbol table), so don't count them as extra pipeline stages even
though they get their own report chapters below for depth. Update
any diagram you reuse from the manual's Section 2 template to include
the last two phases, since the manual's own diagram stops at TAC.

## 5. Lexer Design
Which token categories, which regexes, why keywords are listed
before the generic identifier rule in lexer.l (longest-match +
ordering -- see the manual's Tip in 4.1). Cover the multi-language
token handling here too: how `#include`/`using namespace`/`import`/
`package`/modifiers are recognized and silently discarded, and how
`printf`/`cout`/`System.out.println` all map to print behavior.

## 6. Parser Design
Grammar, precedence/associativity table (see docs/grammar.md),
and -- important, since the manual asks for it explicitly -- explain
the error-recovery rule: why it's there, what it does, what its
limits are (it only resyncs on a semicolon, so an unbalanced brace
won't recover cleanly). Also cover `for`/`do-while`/`++`/`--`/unary
minus grammar rules here as required language constructs.

## 7. Abstract Syntax Tree
How ASTNode is structured (type tag + left/right/third/next), why a
single tagged-union-style struct was chosen instead of one C struct
per node kind.

## 8. Semantic Analysis
Go through each rule in Section 4.5 of the manual and point at
where in semantic.c it's enforced -- undeclared variable,
redeclaration, scope violation, type mismatch, invalid assignment,
invalid expression. tests/invalid/semantic/ has one example program
per rule if you want a concrete case to walk through. Document the
type-widening rule (int assignable to float) explicitly here, since
it's implemented but not written down anywhere yet.

## 9. Symbol Table
Nested-scope design (linked list of scopes, each holding a linked
list of symbols), and the four fields recorded per entry: name,
type, scope (nesting depth), line declared.

## 10. Intermediate Code
TAC generation strategy -- temporaries (t0, t1, ...), labels for
control flow, how if/if-else/while lower to conditional and
unconditional jumps. Walk through one example (the manual's own
"c = a + b * 2;" example, or the one in
tests/valid/valid_arithmetic_and_control_flow.src).

## 11. Code Optimization
Which optimizations are implemented (constant folding, constant
propagation), how they operate on the generated TAC text, and why
this phase runs after TAC and before target code generation. Walk
through one concrete before/after example with real numbers (e.g. a
program with `x = 2 + 3 * 4;` folding down to `x = 14`) -- show the
actual TAC line count change the compiler prints. State plainly
what is NOT implemented (dead-code elimination, common subexpression
elimination, loop optimizations) so the scope is clear.

## 12. Target Code Generation
What target the assembly output models (a simplified x86-style
pseudo-assembly, not a real assemblable ISA), why register
allocation/linking/real hardware output are explicitly out of scope,
and how each TAC construct (assignment, arithmetic, conditional
jump, print) maps to the emitted instructions. Be upfront that this
is illustrative code generation for learning purposes, not a
production backend.

## 13. Challenges
Actual problems you two ran into and how you solved them. (If it's
useful: this codebase's own history is a source of real examples --
e.g. an early version reported lexical errors on stdout instead of
stderr, which meant the GUI silently swallowed them.)

## 14. Testing
Summarize tests/ -- one paragraph on the valid/ cases (including the
C/C++/Java multi-language examples), one on each invalid/ category
(lexical, syntax, semantic), and one on the optimization/target-code
examples. Mention tests/run_all.sh and how it pairs each .src with a
generated .out.txt.

## 15. Conclusion
What you'd do differently, what you'd add next. Note that for-loops,
do-while, increment/decrement, and constant folding are already
implemented (don't list them as future work anymore) -- future work
is genuinely-unimplemented items like arrays, user-defined functions,
dead-code elimination, or a real assemblable backend.

## 16. References
Anything you actually consulted -- Flex/Bison manuals, textbook,
Stack Overflow threads, etc.