#include <stdio.h>
#include <stdlib.h>

#include "ast/ast.h"

extern FILE *yyin;
extern int yyparse();

extern ASTNode *root;

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        printf("Usage: %s <source_file>\n", argv[0]);
        return EXIT_FAILURE;
    }

    yyin = fopen(argv[1], "r");

    if (yyin == NULL)
    {
        perror("Cannot open input file");
        return EXIT_FAILURE;
    }

    if (yyparse() == 0)
    {
        printf("\n====================================\n");
        printf("Parsing Successful\n");
        printf("====================================\n\n");

        printf("Abstract Syntax Tree\n");
        printf("--------------------\n");

        if (root != NULL)
        {
            print_ast(root, 0);
            free_ast(root);
        }
    }

    fclose(yyin);

    return EXIT_SUCCESS;
}