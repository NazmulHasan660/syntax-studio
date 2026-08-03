#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ast/ast.h"
#include "semantic/semantic.h"
#include "symbol_table/symbol_table.h"
#include "codegen/tac.h"


extern FILE *yyin;

extern int yyparse(void);
extern int yylex(void);

extern void yyrestart(
    FILE *input_file
);

extern ASTNode *root;

extern int line_number;
extern int lexical_error_count;
extern int syntax_error_count;


/*
 * When dump_tokens is 1, the lexer prints
 * every generated token.
 */
int dump_tokens = 0;


static void print_section(
    const char *title
)
{
    printf(
        "\n===== %s =====\n",
        title
    );
}


static const char *detect_language(
    const char *file_path,
    const char *requested_language
)
{
    /*
     * The GUI explicitly passes C, C++ or Java.
     */
    if (
        requested_language != NULL &&
        requested_language[0] != '\0'
    )
    {
        return requested_language;
    }

    /*
     * Terminal execution detects the language
     * from the source file extension.
     */
    const char *extension =
        strrchr(file_path, '.');

    if (extension == NULL)
        return "Mini/C";

    if (
        strcmp(extension, ".cpp") == 0 ||
        strcmp(extension, ".cc") == 0 ||
        strcmp(extension, ".cxx") == 0
    )
    {
        return "C++";
    }

    if (strcmp(extension, ".java") == 0)
        return "Java";

    if (strcmp(extension, ".c") == 0)
        return "C";

    return "Mini/C";
}


static FILE *open_source(
    const char *file_path
)
{
    FILE *source_file =
        fopen(file_path, "r");

    if (source_file == NULL)
    {
        perror("Cannot open input file");
    }

    return source_file;
}


/*
 * Print the remaining phase statuses when
 * lexical analysis fails.
 */
static void print_not_executed_after_lexical(void)
{
    print_section("Parsing");

    printf(
        "Status: NOT EXECUTED\n"
        "Reason: Lexical analysis failed.\n"
    );

    print_section("Abstract Syntax Tree");

    printf(
        "Status: NOT GENERATED\n"
        "Reason: Parsing was not completed.\n"
    );

    print_section("Semantic Analysis");

    printf(
        "Status: NOT EXECUTED\n"
        "Reason: No valid AST was produced.\n"
    );

    print_section("Symbol Table");

    printf(
        "Status: NOT GENERATED\n"
        "Reason: Semantic analysis was not executed.\n"
    );

    print_section("Three Address Code (TAC)");

    printf(
        "Status: NOT GENERATED\n"
        "Reason: Compilation stopped after lexical analysis.\n"
    );

    printf(
        "\nCompilation halted after Phase 1 because "
        "%d lexical error(s) were found.\n",
        lexical_error_count
    );
}


/*
 * Print the remaining phase statuses when
 * parsing fails.
 */
static void print_not_executed_after_parsing(void)
{
    print_section("Abstract Syntax Tree");

    printf(
        "Status: NOT GENERATED\n"
        "Reason: Parsing failed.\n"
    );

    print_section("Semantic Analysis");

    printf(
        "Status: NOT EXECUTED\n"
        "Reason: No valid AST was produced.\n"
    );

    print_section("Symbol Table");

    printf(
        "Status: NOT GENERATED\n"
        "Reason: Semantic analysis was not executed.\n"
    );

    print_section("Three Address Code (TAC)");

    printf(
        "Status: NOT GENERATED\n"
        "Reason: Compilation stopped after parsing.\n"
    );

    printf(
        "\nCompilation halted after Phase 2 "
        "because parsing failed.\n"
    );
}


int main(
    int argc,
    char *argv[]
)
{
    if (
        argc < 2 ||
        argc > 3
    )
    {
        fprintf(
            stderr,
            "Usage: %s <source_file> [C|C++|Java]\n",
            argv[0]
        );

        return EXIT_FAILURE;
    }

    const char *language =
        detect_language(
            argv[1],
            argc == 3
                ? argv[2]
                : NULL
        );

    /*
     * ===================================================
     * Phase 1: Lexical Analysis
     * ===================================================
     */
    print_section(
        "Lexical Analysis"
    );

    printf(
        "Language: %s\n",
        language
    );

    printf(
        "Line  Token                 Lexeme\n"
    );

    printf(
        "------------------------------------------------------------\n"
    );

    yyin = open_source(
        argv[1]
    );

    if (yyin == NULL)
        return EXIT_FAILURE;

    yyrestart(yyin);

    line_number = 1;
    lexical_error_count = 0;
    dump_tokens = 1;

    int token_count = 0;

    while (yylex() != 0)
        token_count++;

    fclose(yyin);

    dump_tokens = 0;

    printf(
        "------------------------------------------------------------\n"
    );

    printf(
        "Total parser tokens: %d\n",
        token_count
    );

    if (lexical_error_count > 0)
    {
        printf(
            "Lexical Analysis: FAILED "
            "(%d error(s))\n",
            lexical_error_count
        );

        print_not_executed_after_lexical();

        return EXIT_FAILURE;
    }

    printf(
        "Lexical Analysis: SUCCESS "
        "(no lexical errors)\n"
    );

    /*
     * ===================================================
     * Phase 2: Parsing
     * ===================================================
     */
    print_section(
        "Parsing"
    );

    yyin = open_source(
        argv[1]
    );

    if (yyin == NULL)
        return EXIT_FAILURE;

    yyrestart(yyin);

    line_number = 1;
    syntax_error_count = 0;
    root = NULL;

    int parse_status =
        yyparse();

    fclose(yyin);

    if (
        parse_status != 0 ||
        syntax_error_count > 0
    )
    {
        printf(
            "Parsing: FAILED "
            "(%d syntax error(s))\n",
            syntax_error_count
        );

        if (root != NULL)
        {
            free_ast(root);
            root = NULL;
        }

        print_not_executed_after_parsing();

        return EXIT_FAILURE;
    }

    printf(
        "Parsing successful.\n"
    );

    /*
     * ===================================================
     * Phase 3: Abstract Syntax Tree
     * ===================================================
     */
    print_section(
        "Abstract Syntax Tree"
    );

    if (root != NULL)
    {
        print_ast(
            root,
            0
        );
    }
    else
    {
        printf(
            "(empty program)\n"
        );
    }

    /*
     * ===================================================
     * Phase 4: Semantic Analysis
     * ===================================================
     */
    print_section(
        "Semantic Analysis"
    );

    int semantic_errors =
        analyze_semantics(root);

    if (semantic_errors == 0)
    {
        printf(
            "Semantic analysis successful. "
            "No errors found.\n"
        );
    }
    else
    {
        printf(
            "Semantic Analysis: FAILED "
            "(%d error(s))\n",
            semantic_errors
        );
    }

    /*
     * ===================================================
     * Phase 5: Symbol Table
     * ===================================================
     */
    print_section(
        "Symbol Table"
    );

    symtab_print();

    /*
     * ===================================================
     * Phase 6: Three Address Code
     * ===================================================
     */
    print_section(
        "Three Address Code (TAC)"
    );

    if (semantic_errors == 0)
    {
        TACList tac =
            generate_tac(root);

        print_tac(&tac);

        if (tac.count == 0)
        {
            printf(
                "(no TAC instructions generated)\n"
            );
        }

        free_tac(&tac);
    }
    else
    {
        printf(
            "Status: NOT GENERATED\n"
        );

        printf(
            "Reason: Semantic analysis failed "
            "with %d error(s).\n",
            semantic_errors
        );
    }

    /*
     * Free all allocated compiler memory.
     */
    symtab_free();

    free_ast(root);
    root = NULL;

    if (semantic_errors == 0)
        return EXIT_SUCCESS;

    return EXIT_FAILURE;
}