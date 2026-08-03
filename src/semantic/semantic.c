#include "semantic.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

#include "../symbol_table/symbol_table.h"

static int error_count = 0;

static void semantic_error(
    int line,
    const char *format,
    ...
)
{
    va_list arguments;

    fprintf(
        stderr,
        "Semantic Error at line %d: ",
        line
    );

    va_start(arguments, format);
    vfprintf(stderr, format, arguments);
    va_end(arguments);

    fprintf(stderr, "\n");

    error_count++;
}

static int is_numeric(const char *type)
{
    return strcmp(type, "int") == 0 ||
           strcmp(type, "float") == 0;
}

static int is_arithmetic_operator(const char *operator)
{
    return strcmp(operator, "+") == 0 ||
           strcmp(operator, "-") == 0 ||
           strcmp(operator, "*") == 0 ||
           strcmp(operator, "/") == 0 ||
           strcmp(operator, "%") == 0;
}

static int is_equality_operator(const char *operator)
{
    return strcmp(operator, "==") == 0 ||
           strcmp(operator, "!=") == 0;
}

static int is_relational_operator(const char *operator)
{
    return strcmp(operator, "<") == 0 ||
           strcmp(operator, ">") == 0 ||
           strcmp(operator, "<=") == 0 ||
           strcmp(operator, ">=") == 0;
}

static int is_logical_operator(const char *operator)
{
    return strcmp(operator, "&&") == 0 ||
           strcmp(operator, "||") == 0;
}

static void analyze_statement(ASTNode *statement);
static void analyze_statement_list(ASTNode *list);

static const char *analyze_expression(ASTNode *expression)
{
    const char *result_type = "error";

    if (expression == NULL)
        return "error";

    switch (expression->type)
    {
        case NODE_INT_LITERAL:
            result_type = "int";
            break;

        case NODE_FLOAT_LITERAL:
            result_type = "float";
            break;

        case NODE_BOOL_LITERAL:
            result_type = "bool";
            break;

        case NODE_IDENTIFIER:
        {
            Symbol *symbol =
                symtab_lookup(expression->text);

            if (symbol == NULL)
            {
                semantic_error(
                    expression->line,
                    "Undeclared variable '%s'",
                    expression->text
                );

                result_type = "error";
            }
            else
            {
                result_type = symbol->type;
            }

            break;
        }

        case NODE_UNARY_OP:
        {
            const char *operand_type =
                analyze_expression(expression->left);

            if (strcmp(operand_type, "error") == 0)
            {
                result_type = "error";
            }
            else if (strcmp(expression->text, "!") == 0)
            {
                if (strcmp(operand_type, "bool") != 0)
                {
                    semantic_error(
                        expression->line,
                        "Operator '!' requires bool operand, got '%s'",
                        operand_type
                    );

                    result_type = "error";
                }
                else
                {
                    result_type = "bool";
                }
            }
            else if (strcmp(expression->text, "-") == 0)
            {
                if (!is_numeric(operand_type))
                {
                    semantic_error(
                        expression->line,
                        "Unary '-' requires a numeric operand, got '%s'",
                        operand_type
                    );

                    result_type = "error";
                }
                else
                {
                    result_type = operand_type;
                }
            }
            else
            {
                result_type = "error";
            }

            break;
        }

        case NODE_BINARY_OP:
        {
            const char *left_type =
                analyze_expression(expression->left);

            const char *right_type =
                analyze_expression(expression->right);

            const char *operator = expression->text;

            int has_error =
                strcmp(left_type, "error") == 0 ||
                strcmp(right_type, "error") == 0;

            if (is_arithmetic_operator(operator))
            {
                if (has_error)
                {
                    result_type = "error";
                }
                else if (
                    strcmp(left_type, "bool") == 0 ||
                    strcmp(right_type, "bool") == 0
                )
                {
                    semantic_error(
                        expression->line,
                        "Operator '%s' cannot be applied to bool operands",
                        operator
                    );

                    result_type = "error";
                }
                else if (
                    strcmp(left_type, "float") == 0 ||
                    strcmp(right_type, "float") == 0
                )
                {
                    result_type = "float";
                }
                else
                {
                    result_type = "int";
                }
            }
            else if (is_equality_operator(operator))
            {
                if (!has_error)
                {
                    int compatible =
                        strcmp(left_type, right_type) == 0 ||
                        (
                            is_numeric(left_type) &&
                            is_numeric(right_type)
                        );

                    if (!compatible)
                    {
                        semantic_error(
                            expression->line,
                            "Cannot compare '%s' with '%s' using '%s'",
                            left_type,
                            right_type,
                            operator
                        );
                    }
                }

                result_type = "bool";
            }
            else if (is_relational_operator(operator))
            {
                if (
                    !has_error &&
                    !(
                        is_numeric(left_type) &&
                        is_numeric(right_type)
                    )
                )
                {
                    semantic_error(
                        expression->line,
                        "Operator '%s' requires numeric operands, got '%s' and '%s'",
                        operator,
                        left_type,
                        right_type
                    );
                }

                result_type = "bool";
            }
            else if (is_logical_operator(operator))
            {
                if (
                    !has_error &&
                    (
                        strcmp(left_type, "bool") != 0 ||
                        strcmp(right_type, "bool") != 0
                    )
                )
                {
                    semantic_error(
                        expression->line,
                        "Logical operator '%s' requires bool operands",
                        operator
                    );
                }

                result_type = "bool";
            }
            else
            {
                result_type = "error";
            }

            break;
        }

        default:
            result_type = "error";
            break;
    }

    expression->data_type = strdup(result_type);

    return expression->data_type;
}

static void analyze_statement(ASTNode *statement)
{
    if (statement == NULL)
        return;

    switch (statement->type)
    {
        case NODE_DECLARATION:
        {
            int inserted = symtab_insert(
                statement->text,
                statement->data_type,
                statement->line
            );

            if (!inserted)
            {
                semantic_error(
                    statement->line,
                    "Redeclaration of variable '%s'",
                    statement->text
                );
            }

            break;
        }

        case NODE_ASSIGNMENT:
        {
            Symbol *symbol =
                symtab_lookup(statement->text);

            const char *right_type =
                analyze_expression(statement->left);

            if (symbol == NULL)
            {
                semantic_error(
                    statement->line,
                    "Assignment to undeclared variable '%s'",
                    statement->text
                );
            }
            else if (
                strcmp(right_type, "error") != 0 &&
                strcmp(symbol->type, right_type) != 0
            )
            {
                /*
                 * int value can be assigned to float.
                 */
                int is_widening =
                    strcmp(symbol->type, "float") == 0 &&
                    strcmp(right_type, "int") == 0;

                if (!is_widening)
                {
                    semantic_error(
                        statement->line,
                        "Type mismatch: cannot assign '%s' to variable '%s' of type '%s'",
                        right_type,
                        statement->text,
                        symbol->type
                    );
                }
            }

            break;
        }

        case NODE_IF:
        {
            const char *condition_type =
                analyze_expression(statement->left);

            if (
                strcmp(condition_type, "bool") != 0 &&
                strcmp(condition_type, "error") != 0
            )
            {
                semantic_error(
                    statement->line,
                    "Condition of 'if' must be bool, got '%s'",
                    condition_type
                );
            }

            analyze_statement(statement->right);

            if (statement->third != NULL)
                analyze_statement(statement->third);

            break;
        }

        case NODE_WHILE:
        {
            const char *condition_type =
                analyze_expression(statement->left);

            if (
                strcmp(condition_type, "bool") != 0 &&
                strcmp(condition_type, "error") != 0
            )
            {
                semantic_error(
                    statement->line,
                    "Condition of 'while' must be bool, got '%s'",
                    condition_type
                );
            }

            analyze_statement(statement->right);

            break;
        }

        case NODE_FOR:
        {
            const char *condition_type =
                analyze_expression(statement->left);

            if (
                strcmp(condition_type, "bool") != 0 &&
                strcmp(condition_type, "error") != 0
            )
            {
                semantic_error(
                    statement->line,
                    "Condition of 'for' must be bool, got '%s'",
                    condition_type
                );
            }

            analyze_statement(statement->right);

            if (statement->third != NULL)
                analyze_statement(statement->third);

            break;
        }

        case NODE_DO_WHILE:
        {
            analyze_statement(statement->right);

            const char *condition_type =
                analyze_expression(statement->left);

            if (
                strcmp(condition_type, "bool") != 0 &&
                strcmp(condition_type, "error") != 0
            )
            {
                semantic_error(
                    statement->line,
                    "Condition of 'do-while' must be bool, got '%s'",
                    condition_type
                );
            }

            break;
        }

        case NODE_PRINT:
        {
            analyze_expression(statement->left);
            break;
        }

        case NODE_BLOCK:
        {
            symtab_enter_scope();

            analyze_statement_list(statement->left);

            symtab_exit_scope();
            break;
        }

        /*
         * Return nodes are accepted by the educational parser.
         * Return-type checking is outside this compiler subset.
         */
        case NODE_UNARY_OP:
        default:
            break;
    }
}

static void analyze_statement_list(ASTNode *list)
{
    for (
        ASTNode *statement = list;
        statement != NULL;
        statement = statement->next
    )
    {
        analyze_statement(statement);
    }
}

int analyze_semantics(ASTNode *root)
{
    error_count = 0;

    symtab_init();

    if (
        root != NULL &&
        root->type == NODE_PROGRAM
    )
    {
        analyze_statement_list(root->left);
    }

    /*
     * Do not free the symbol table here.
     * main.c will print it as Phase 5 and then free it.
     */
    return error_count;
}