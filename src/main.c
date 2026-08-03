#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ast/ast.h"
#include "semantic/semantic.h"
#include "symbol_table/symbol_table.h"
#include "codegen/tac.h"
#include "optimizer/optimizer.h"
#include "codegen/assembly.h"


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
    print_section("Parser (AST)");

    printf(
        "Status: NOT EXECUTED\n"
        "Reason: Lexical analysis failed.\n"
    );

    print_section("Semantic Analysis");

    printf(
        "Status: NOT EXECUTED\n"
        "Reason: No valid AST was produced.\n"
    );

    print_section("Intermediate Code (TAC)");

    printf(
        "Status: NOT GENERATED\n"
        "Reason: Compilation stopped after lexical analysis.\n"
    );

    print_section("Code Optimization");

    printf(
        "Status: NOT EXECUTED\n"
        "Reason: No TAC was generated.\n"
    );

    print_section("Target Code Generation (Assembly)");

    printf(
        "Status: NOT GENERATED\n"
        "Reason: No optimized TAC was available.\n"
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
    print_section("Semantic Analysis");

    printf(
        "Status: NOT EXECUTED\n"
        "Reason: No valid AST was produced.\n"
    );

    print_section("Intermediate Code (TAC)");

    printf(
        "Status: NOT GENERATED\n"
        "Reason: Compilation stopped after parsing.\n"
    );

    print_section("Code Optimization");

    printf(
        "Status: NOT EXECUTED\n"
        "Reason: No TAC was generated.\n"
    );

    print_section("Target Code Generation (Assembly)");

    printf(
        "Status: NOT GENERATED\n"
        "Reason: No optimized TAC was available.\n"
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
     * Phase 2: Parser (AST)
     * ===================================================
     */
    print_section(
        "Parser (AST)"
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
        "Parsing successful.\n\n"
        "Abstract Syntax Tree:\n"
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
     * Phase 3: Semantic Analysis (Symbol Table)
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

    printf(
        "\nSymbol Table:\n"
    );

    symtab_print();

    /*
     * ===================================================
     * Phase 4: Intermediate Code (TAC)
     * ===================================================
     */
    print_section(
        "Intermediate Code (TAC)"
    );

    TACList tac;
    tac.lines = NULL;
    tac.count = 0;
    tac.capacity = 0;

    int tac_generated = 0;

    if (semantic_errors == 0)
    {
        tac = generate_tac(root);
        tac_generated = 1;

        print_tac(&tac);

        if (tac.count == 0)
        {
            printf(
                "(no TAC instructions generated)\n"
            );
        }
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
     * ===================================================
     * Phase 5: Code Optimization (bonus, Section 14)
     * ===================================================
     */
    print_section(
        "Code Optimization"
    );

    TACList optimized_tac;
    optimized_tac.lines = NULL;
    optimized_tac.count = 0;
    optimized_tac.capacity = 0;

    int optimized = 0;

    if (tac_generated)
    {
        optimized_tac = optimize_tac(&tac);
        optimized = 1;

        printf(
            "Constant folding + constant propagation "
            "applied (%d -> %d TAC lines):\n\n",
            tac.count,
            optimized_tac.count
        );

        print_tac(&optimized_tac);
    }
    else
    {
        printf(
            "Status: NOT EXECUTED\n"
        );

        printf(
            "Reason: No TAC was generated.\n"
        );
    }

    /*
     * ===================================================
     * Phase 6: Target Code Generation (Assembly, bonus)
     * ===================================================
     */
    print_section(
        "Target Code Generation (Assembly)"
    );

    if (optimized)
    {
        char *assembly =
            generate_assembly(&optimized_tac);

        printf(
            "%s",
            assembly
        );

        free(assembly);
    }
    else
    {
        printf(
            "Status: NOT GENERATED\n"
        );

        printf(
            "Reason: No optimized TAC was available.\n"
        );
    }

    if (optimized)
        free_tac(&optimized_tac);

    if (tac_generated)
        free_tac(&tac);

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