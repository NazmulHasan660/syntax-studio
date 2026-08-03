#ifndef SEMANTIC_H
#define SEMANTIC_H

#include "../ast/ast.h"

/*
 * Performs symbol-table construction and type checking.
 * Returns the total number of semantic errors.
 */
int analyze_semantics(ASTNode *root);

#endif