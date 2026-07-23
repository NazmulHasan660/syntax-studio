#include "ast.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int line_number;

static void print_indent(int level);

ASTNode *create_node(NodeType type, char *text)
{
    ASTNode *node = (ASTNode *)malloc(sizeof(ASTNode));

    if (node == NULL)
    {
        fprintf(stderr, "Memory allocation failed.\n");
        exit(EXIT_FAILURE);
    }

    node->type = type;

    if (text != NULL)
        node->text = strdup(text);
    else
        node->text = NULL;

    node->line = line_number;

    node->left = NULL;
    node->right = NULL;
    node->third = NULL;
    node->next = NULL;

    return node;
}

static void print_indent(int level)
{
    for (int i = 0; i < level; i++)
        printf("    ");
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
                printf("DECLARATION (%s)\n",
                       node->text ? node->text : "");
                break;

            case NODE_ASSIGNMENT:
                printf("ASSIGNMENT (%s)\n",
                       node->text ? node->text : "");
                break;

            case NODE_IF:
                printf("IF\n");
                break;

            case NODE_WHILE:
                printf("WHILE\n");
                break;

            case NODE_PRINT:
                printf("PRINT\n");
                break;

            case NODE_BINARY_OP:
                printf("BINARY OP (%s)\n",
                       node->text ? node->text : "");
                break;

            case NODE_UNARY_OP:
                printf("UNARY OP (%s)\n",
                       node->text ? node->text : "");
                break;

            case NODE_IDENTIFIER:
                printf("IDENTIFIER (%s)\n",
                       node->text ? node->text : "");
                break;

            case NODE_INT_LITERAL:
                printf("INT (%s)\n",
                       node->text ? node->text : "");
                break;

            case NODE_FLOAT_LITERAL:
                printf("FLOAT (%s)\n",
                       node->text ? node->text : "");
                break;

            case NODE_BOOL_LITERAL:
                printf("BOOL (%s)\n",
                       node->text ? node->text : "");
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
    {
        free(node->text);
    }

    free(node);
}