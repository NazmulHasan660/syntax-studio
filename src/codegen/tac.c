#include "tac.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

static int temporary_count = 0;
static int label_count = 0;

static void emit_tac(
    TACList *list,
    const char *format,
    ...
)
{
    char buffer[256];
    va_list arguments;

    va_start(arguments, format);
    vsnprintf(
        buffer,
        sizeof(buffer),
        format,
        arguments
    );
    va_end(arguments);

    if (list->count == list->capacity)
    {
        if (list->capacity == 0)
            list->capacity = 32;
        else
            list->capacity *= 2;

        list->lines = (char **)realloc(
            list->lines,
            list->capacity * sizeof(char *)
        );

        if (list->lines == NULL)
        {
            fprintf(
                stderr,
                "Memory allocation failed for TAC.\n"
            );
            exit(EXIT_FAILURE);
        }
    }

    list->lines[list->count] = strdup(buffer);
    list->count++;
}

static char *create_temporary(void)
{
    char buffer[16];

    snprintf(
        buffer,
        sizeof(buffer),
        "t%d",
        temporary_count++
    );

    return strdup(buffer);
}

static char *create_label(void)
{
    char buffer[16];

    snprintf(
        buffer,
        sizeof(buffer),
        "L%d",
        label_count++
    );

    return strdup(buffer);
}

static char *generate_expression(
    ASTNode *expression,
    TACList *list
)
{
    if (expression == NULL)
        return strdup("?");

    switch (expression->type)
    {
        case NODE_IDENTIFIER:
        case NODE_INT_LITERAL:
        case NODE_FLOAT_LITERAL:
        case NODE_BOOL_LITERAL:
        case NODE_STRING_LITERAL:
            return strdup(expression->text);

        case NODE_UNARY_OP:
        {
            char *operand =
                generate_expression(
                    expression->left,
                    list
                );

            char *temporary =
                create_temporary();

            emit_tac(
                list,
                "%s = %s%s",
                temporary,
                expression->text,
                operand
            );

            free(operand);

            return temporary;
        }

        case NODE_BINARY_OP:
        {
            char *left =
                generate_expression(
                    expression->left,
                    list
                );

            char *right =
                generate_expression(
                    expression->right,
                    list
                );

            char *temporary =
                create_temporary();

            emit_tac(
                list,
                "%s = %s %s %s",
                temporary,
                left,
                expression->text,
                right
            );

            free(left);
            free(right);

            return temporary;
        }

        default:
            return strdup("?");
    }
}

static void generate_statement(
    ASTNode *statement,
    TACList *list
);

static void generate_statement_list(
    ASTNode *statement_list,
    TACList *list
)
{
    for (
        ASTNode *statement = statement_list;
        statement != NULL;
        statement = statement->next
    )
    {
        generate_statement(
            statement,
            list
        );
    }
}

static void generate_statement(
    ASTNode *statement,
    TACList *list
)
{
    if (statement == NULL)
        return;

    switch (statement->type)
    {
      
        case NODE_CLASS:
        {
            generate_statement_list(
                statement->left,
                list
            );
            break;
        }

        case NODE_FUNCTION:
        {
            emit_tac(
                list,
                "%s:",
                statement->text
            );

            if (statement->left != NULL)
            {
                generate_statement(
                    statement->left,
                    list
                );
            }
            break;
        }
     

        case NODE_DECLARATION:
        {
            emit_tac(
                list,
                "// declare %s : %s",
                statement->text,
                statement->data_type
                    ? statement->data_type
                    : "unknown"
            );

            break;
        }

        case NODE_ASSIGNMENT:
        {
            char *right =
                generate_expression(
                    statement->left,
                    list
                );

            emit_tac(
                list,
                "%s = %s",
                statement->text,
                right
            );

            free(right);
            break;
        }

        case NODE_PRINT:
        {
            ASTNode *argument = statement->left;

            while (argument != NULL)
            {
                char *value =
                    generate_expression(
                        argument,
                        list
                    );

                emit_tac(
                    list,
                    "print %s",
                    value
                );

                free(value);

                argument = argument->next;
            }

            break;
        }

        case NODE_IF:
        {
            char *condition =
                generate_expression(
                    statement->left,
                    list
                );

            if (statement->third == NULL)
            {
                char *end_label =
                    create_label();

                emit_tac(
                    list,
                    "ifFalse %s goto %s",
                    condition,
                    end_label
                );

                generate_statement(
                    statement->right,
                    list
                );

                emit_tac(
                    list,
                    "%s:",
                    end_label
                );

                free(end_label);
            }
            else
            {
                char *else_label =
                    create_label();

                char *end_label =
                    create_label();

                emit_tac(
                    list,
                    "ifFalse %s goto %s",
                    condition,
                    else_label
                );

                generate_statement(
                    statement->right,
                    list
                );

                emit_tac(
                    list,
                    "goto %s",
                    end_label
                );

                emit_tac(
                    list,
                    "%s:",
                    else_label
                );

                generate_statement(
                    statement->third,
                    list
                );

                emit_tac(
                    list,
                    "%s:",
                    end_label
                );

                free(else_label);
                free(end_label);
            }

            free(condition);
            break;
        }

        case NODE_WHILE:
        {
            char *start_label =
                create_label();

            char *end_label =
                create_label();

            emit_tac(
                list,
                "%s:",
                start_label
            );

            char *condition =
                generate_expression(
                    statement->left,
                    list
                );

            emit_tac(
                list,
                "ifFalse %s goto %s",
                condition,
                end_label
            );

            free(condition);

            generate_statement(
                statement->right,
                list
            );

            emit_tac(
                list,
                "goto %s",
                start_label
            );

            emit_tac(
                list,
                "%s:",
                end_label
            );

            free(start_label);
            free(end_label);
            break;
        }

        case NODE_FOR:
        {
            char *start_label =
                create_label();

            char *end_label =
                create_label();

            emit_tac(
                list,
                "%s:",
                start_label
            );

            char *condition =
                generate_expression(
                    statement->left,
                    list
                );

            emit_tac(
                list,
                "ifFalse %s goto %s",
                condition,
                end_label
            );

            free(condition);

            generate_statement(
                statement->right,
                list
            );

            if (statement->third != NULL)
            {
                generate_statement(
                    statement->third,
                    list
                );
            }

            emit_tac(
                list,
                "goto %s",
                start_label
            );

            emit_tac(
                list,
                "%s:",
                end_label
            );

            free(start_label);
            free(end_label);
            break;
        }

        case NODE_DO_WHILE:
        {
            char *start_label =
                create_label();

            char *end_label =
                create_label();

            emit_tac(
                list,
                "%s:",
                start_label
            );

            generate_statement(
                statement->right,
                list
            );

            char *condition =
                generate_expression(
                    statement->left,
                    list
                );

            emit_tac(
                list,
                "ifFalse %s goto %s",
                condition,
                end_label
            );

            emit_tac(
                list,
                "goto %s",
                start_label
            );

            emit_tac(
                list,
                "%s:",
                end_label
            );

            free(condition);
            free(start_label);
            free(end_label);
            break;
        }

        case NODE_BLOCK:
        {
            generate_statement_list(
                statement->left,
                list
            );

            break;
        }

        case NODE_UNARY_OP:
        default:
            break;
    }
}

TACList generate_tac(ASTNode *root)
{
    TACList list;

    list.lines = NULL;
    list.count = 0;
    list.capacity = 0;

    temporary_count = 0;
    label_count = 0;

    if (
        root != NULL &&
        root->type == NODE_PROGRAM
    )
    {
        generate_statement_list(
            root->left,
            &list
        );
    }

    return list;
}

void print_tac(const TACList *list)
{
    if (
        list == NULL ||
        list->lines == NULL
    )
    {
        return;
    }

    for (int i = 0; i < list->count; i++)
    {
        size_t length = strlen(list->lines[i]);

        int is_label =
            length > 0 &&
            list->lines[i][length - 1] == ':' &&
            strncmp(list->lines[i], "//", 2) != 0;

        if (is_label)
        {
            printf(
                "%s\n",
                list->lines[i]
            );
        }
        else
        {
            printf(
                "    %s\n",
                list->lines[i]
            );
        }
    }
}

void free_tac(TACList *list)
{
    if (
        list == NULL ||
        list->lines == NULL
    )
    {
        return;
    }

    for (int i = 0; i < list->count; i++)
        free(list->lines[i]);

    free(list->lines);

    list->lines = NULL;
    list->count = 0;
    list->capacity = 0;
}