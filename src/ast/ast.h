#ifndef AST_H
#define AST_H

typedef enum
{
    /* Program */
    NODE_PROGRAM,

    /* Statements */
    NODE_BLOCK,
    NODE_DECLARATION,
    NODE_ASSIGNMENT,
    NODE_IF,
    NODE_WHILE,
    NODE_PRINT,

    /* Expressions */
    NODE_BINARY_OP,
    NODE_UNARY_OP,

    /* Values */
    NODE_IDENTIFIER,
    NODE_INT_LITERAL,
    NODE_FLOAT_LITERAL,
    NODE_BOOL_LITERAL

} NodeType;

typedef struct ASTNode
{
    NodeType type;

    /* Identifier / Operator / Literal */
    char *text;

    /* Source Line Number */
    int line;

    /* Tree Children */
    struct ASTNode *left;
    struct ASTNode *right;
    struct ASTNode *third;

    /* Linked Statement List */
    struct ASTNode *next;

} ASTNode;


/* Constructors */
ASTNode *create_node(NodeType type, char *text);

/* Utilities */
void print_ast(ASTNode *node, int level);
void free_ast(ASTNode *node);

#endif