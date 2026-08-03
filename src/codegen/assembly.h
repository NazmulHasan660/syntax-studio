#ifndef ASSEMBLY_H
#define ASSEMBLY_H

#include "tac.h"

/*
 * Target Code Generation phase (Section "6" in the classical
 * six-phase compiler model: Lexical -> Syntax -> Semantic ->
 * Intermediate Code -> Optimization -> Target Code).
 *
 * Translates (optimized) TAC into a small, illustrative,
 * x86-style pseudo-assembly text. This is intentionally NOT a real,
 * runnable assembler: there is no register allocation, no linking,
 * no instruction scheduling, and it does not target real hardware --
 * none of that is required for this course. It exists purely to
 * demonstrate, concretely, how each TAC instruction *could* map onto
 * a target instruction set, which is the actual learning goal of
 * this phase.
 *
 * String operands (print of a string literal) are emitted as a
 * dedicated PRINT_STR pseudo-instruction rather than being treated
 * as a numeric operand -- this language has no real string type
 * (Section 5 defines only int/float/bool), so there is no correct
 * general-purpose numeric MOV to generate for one.
 *
 * Returns a newly allocated, NUL-terminated string that the caller
 * must free(). Returns NULL on allocation failure.
 */
char *generate_assembly(const TACList *tac);

#endif
