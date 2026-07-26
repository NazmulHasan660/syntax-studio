# Project Report -- Outline

Section numbers/titles match Section 12 of the Project Manual.
This file only has headers and a short prompt under each one --
you and Mahdi need to write the actual content yourselves. Per
Section 10 of the manual, you have to be able to explain anything
in the report (and the code) in the individual viva, so don't
paste in anything you can't defend on the spot.

## 1. Introduction
Why does a compiler course end in a project like this instead of a
written final? What does Syntax Studio do, one paragraph.

## 2. Objectives
What was each of you trying to demonstrate you understood by
building this? (Tie back to the six required modules in Section 4
of the manual.)

## 3. Language Specification
Restate the language from Section 5 of the manual in your own
words: data types, statements, operators. Include the formal CFG --
see docs/grammar.md, already derived from your actual parser.y.

## 4. Compiler Architecture
Walk through the pipeline: source -> lexer -> parser -> AST ->
symbol table -> semantic analysis -> TAC. A diagram helps (the
manual's own pipeline diagram in Section 2 is a fine template).

## 5. Lexer Design
Which token categories, which regexes, why keywords are listed
before the generic identifier rule in lexer.l (longest-match +
ordering -- see the manual's Tip in 4.1).

## 6. Parser Design
Grammar, precedence/associativity table (see docs/grammar.md),
and -- important, since the manual asks for it explicitly -- explain
the error-recovery rule: why it's there, what it does, what its
limits are (it only resyncs on a semicolon, so an unbalanced brace
won't recover cleanly).

## 7. Abstract Syntax Tree
How ASTNode is structured (type tag + left/right/third/next), why a
single tagged-union-style struct was chosen instead of one C struct
per node kind.

## 8. Semantic Analysis
Go through each rule in Section 4.5 of the manual and point at
where in semantic.c it's enforced -- undeclared variable,
redeclaration, scope violation, type mismatch, invalid assignment,
invalid expression. tests/invalid/semantic/ has one example program
per rule if you want a concrete case to walk through.

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

## 11. Challenges
Actual problems you two ran into and how you solved them. (If it's
useful: this codebase's own history is a source of real examples --
e.g. an early version reported lexical errors on stdout instead of
stderr, which meant the GUI silently swallowed them.)

## 12. Testing
Summarize tests/ -- one paragraph on the valid/ cases, one on each
invalid/ category (lexical, syntax, semantic). Mention
tests/run_all.sh and how it pairs each .src with a generated
.out.txt.

## 13. Conclusion
What you'd do differently, what you'd add next (Section 14's bonus
list is a fine source of ideas: arrays, functions, for-loops,
constant folding, ...).

## 14. References
Anything you actually consulted -- Flex/Bison manuals, textbook,
Stack Overflow threads, etc.
