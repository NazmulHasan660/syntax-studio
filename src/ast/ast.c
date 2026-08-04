#include "ast.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int line_number;

static void print_indent(int level)
{
    for (int i = 0; i < level; i++)
        printf("    ");
}

ASTNode *create_node(NodeType type, char *text)
{
    ASTNode *node = (ASTNode *)malloc(sizeof(ASTNode));

    if (node == NULL)
    {
        fprintf(stderr, "Memory allocation failed for AST node.\n");
        exit(EXIT_FAILURE);
    }

    node->type = type;
    node->text = (text != NULL) ? strdup(text) : NULL;
    node->data_type = NULL;
    node->line = line_number;

    node->left = NULL;
    node->right = NULL;
    node->third = NULL;
    node->next = NULL;

    return node;
}

void print_ast(ASTNode *node, int level)
{
    while (node != NULL)
    {
        print_indent(level);

        switch (node->type)
        {
            case NODE_PROGRAM:
                printf("PROGRAM\n");
                break;

            case NODE_BLOCK:
                printf("BLOCK\n");
                break;

            case NODE_DECLARATION:
                printf(
                    "DECLARATION (%s : %s)\n",
                    node->text ? node->text : "",
                    node->data_type ? node->data_type : "?"
                );
                break;

            case NODE_ASSIGNMENT:
                printf(
                    "ASSIGNMENT (%s)\n",
                    node->text ? node->text : ""
                );
                break;

            case NODE_IF:
                printf("IF\n");
                break;

            case NODE_WHILE:
                printf("WHILE\n");
                break;

            case NODE_FOR:
                printf("FOR\n");
                break;

            case NODE_DO_WHILE:
                printf("DO-WHILE\n");
                break;

            case NODE_PRINT:
                printf("PRINT\n");
                break;

            case NODE_BINARY_OP:
                printf(
                    "BINARY OP (%s)\n",
                    node->text ? node->text : ""
                );
                break;

            case NODE_UNARY_OP:
                printf(
                    "UNARY OP (%s)\n",
                    node->text ? node->text : ""
                );
                break;

            case NODE_IDENTIFIER:
                printf(
                    "IDENTIFIER (%s)\n",
                    node->text ? node->text : ""
                );
                break;

            case NODE_INT_LITERAL:
                printf(
                    "INT (%s)\n",
                    node->text ? node->text : ""
                );
                break;

            case NODE_FLOAT_LITERAL:
                printf(
                    "FLOAT (%s)\n",
                    node->text ? node->text : ""
                );
                break;

            case NODE_STRING_LITERAL:
                printf(
                    "STRING (%s)\n",
                    node->text ? node->text : ""
                );
                break;

            case NODE_BOOL_LITERAL:
                printf(
                    "BOOL (%s)\n",
                    node->text ? node->text : ""
                );
                break;

            default:
                printf("UNKNOWN NODE\n");
                break;
        }

        print_ast(node->left, level + 1);
        print_ast(node->right, level + 1);
        print_ast(node->third, level + 1);

        node = node->next;
    }
}

void free_ast(ASTNode *node)
{
    if (node == NULL)
        return;

    free_ast(node->left);
    free_ast(node->right);
    free_ast(node->third);
    free_ast(node->next);

    if (node->text != NULL)
        free(node->text);

    if (node->data_type != NULL)
        free(node->data_type);

    free(node);
}