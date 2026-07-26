#include <stdio.h>
#include <stdlib.h>

#include "ast/ast.h"
#include "semantic/semantic.h"
#include "codegen/tac.h"

extern FILE *yyin;
extern int yyparse();

extern ASTNode *root;
extern int lexical_error_count;
extern int syntax_error_count;

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

    int exit_status = EXIT_SUCCESS;

    /* yyparse() can return 0 ("accepted") even when syntax errors were
     * found, because the grammar has basic error recovery (see the
     * `error SEMICOLON` rule in parser.y): it discards a broken
     * statement and keeps parsing so later errors are still reported.
     * So a clean run additionally requires zero counted errors. */
    if (yyparse() == 0 && lexical_error_count == 0 && syntax_error_count == 0)
    {
        printf("\n====================================\n");
        printf("Parsing Successful\n");
        printf("====================================\n\n");

        printf("Abstract Syntax Tree\n");
        printf("--------------------\n");

        if (root != NULL)
        {
            print_ast(root, 0);

            printf("\n====================================\n");
            printf("Semantic Analysis\n");
            printf("====================================\n\n");

            int errors = analyze_semantics(root);

            if (errors > 0)
            {
                printf("\n%d semantic error(s) found. Skipping code generation.\n",
                       errors);
                exit_status = EXIT_FAILURE;
            }
            else
            {
                printf("No semantic errors found.\n");

                printf("\n====================================\n");
                printf("Three Address Code\n");
                printf("====================================\n\n");

                generate_tac(root);
            }

            free_ast(root);
        }
    }
    else
    {
        /* Syntax and/or lexical errors were already reported to
         * stderr by yyerror()/the lexer as they were encountered. */
        exit_status = EXIT_FAILURE;

        if (lexical_error_count > 0)
        {
            fprintf(stderr, "\n%d lexical error(s) found.\n", lexical_error_count);
        }

        if (syntax_error_count > 0)
        {
            fprintf(stderr, "%d syntax error(s) found.\n", syntax_error_count);
        }

        if (root != NULL)
        {
            free_ast(root);
        }
    }

    fclose(yyin);

    return exit_status;
}