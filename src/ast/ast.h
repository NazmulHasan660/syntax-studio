#ifndef AST_H
#define AST_H

typedef enum
{
    /* Program Structure */
    NODE_PROGRAM,

    /* Statements */
    NODE_BLOCK,
    NODE_DECLARATION,
    NODE_ASSIGNMENT,
    NODE_IF,
    NODE_WHILE,
    NODE_FOR,
    NODE_DO_WHILE,
    NODE_PRINT,

    /* Expressions */
    NODE_BINARY_OP,
    NODE_UNARY_OP,

    /* Values */
    NODE_IDENTIFIER,
    NODE_INT_LITERAL,
    NODE_FLOAT_LITERAL,
    NODE_BOOL_LITERAL,
    NODE_STRING_LITERAL

} NodeType;

typedef struct ASTNode
{
    NodeType type;

    /* Identifier, operator or literal text */
    char *text;

    /* Declared or inferred type */
    char *data_type;

    /* Source line number */
    int line;

    /* Tree children */
    struct ASTNode *left;
    struct ASTNode *right;
    struct ASTNode *third;

    /* Linked statement list */
    struct ASTNode *next;

} ASTNode;

/* Constructor */
ASTNode *create_node(NodeType type, char *text);

/* Utilities */
void print_ast(ASTNode *node, int level);
void free_ast(ASTNode *node);

#endif