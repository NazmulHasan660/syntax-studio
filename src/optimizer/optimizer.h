#ifndef OPTIMIZER_H
#define OPTIMIZER_H

#include "../codegen/tac.h"

/*
 * Optimization phase (bonus, Section 14: "Constant folding").
 *
 * Runs two safe, well-defined peephole passes over the generated TAC,
 * repeated to a fixed point so that chained constant expressions
 * collapse completely:
 *
 *   1. Constant folding:
 *          tN = LITERAL <op> LITERAL   -->   tN = RESULT
 *      for the arithmetic operators + - * / %. Division/modulo by
 *      a literal zero is left unfolded (it is a runtime concern,
 *      not something the optimizer should silently resolve).
 *
 *   2. Constant propagation + dead-line elimination:
 *      once a temporary is known (from step 1, or from being a
 *      direct copy of a literal) to hold a constant, every later
 *      use of that temporary is replaced by the literal itself, and
 *      the now-unused "tN = LITERAL" defining line is dropped.
 *
 * This does not change program behaviour -- it only removes
 * redundant computation that a human would also simplify by hand.
 * It operates purely on the textual TAC (no re-parsing of the AST),
 * which keeps it decoupled from, and safe for, every existing phase.
 *
 * Returns a new TACList; the caller owns it and must free it with
 * free_tac(). The input list is left unmodified.
 */
TACList optimize_tac(const TACList *input);

#endif
