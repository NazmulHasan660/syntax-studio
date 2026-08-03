#ifndef TAC_H
#define TAC_H

#include "../ast/ast.h"

typedef struct TACList
{
    char **lines;
    int count;
    int capacity;

} TACList;

/* Generate TAC from a valid AST */
TACList generate_tac(ASTNode *root);

/* Print generated TAC */
void print_tac(const TACList *list);

/* Free TAC memory */
void free_tac(TACList *list);

#endif