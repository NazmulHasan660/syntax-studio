%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../ast/ast.h"

extern int yylex(void);
extern int line_number;

void yyerror(const char *s);

ASTNode *root = NULL;
%}

%code requires {
#include "../ast/ast.h"
}

%define parse.error verbose

%union{
    int ival;
    float fval;
    char *sval;
    ASTNode *node;
}

%type <node> Program
%type <node> StatementList
%type <node> Statement
%type <node> Block
%type <node> Declaration
%type <node> Assignment
%type <node> IfStatement
%type <node> WhileStatement
%type <node> PrintStatement
%type <node> Expression

%token INT FLOAT BOOL
%token IF ELSE WHILE PRINT
%token TRUE FALSE

%token <sval> ID
%token <ival> INT_CONST
%token <fval> FLOAT_CONST

%token PLUS MINUS MUL DIV MOD
%token LT GT LE GE EQ NEQ
%token AND OR NOT
%token ASSIGN

%token LPAREN RPAREN
%token LBRACE RBRACE
%token SEMICOLON COMMA

%left OR
%left AND
%left EQ NEQ
%left LT GT LE GE
%left PLUS MINUS
%left MUL DIV MOD
%right NOT

%start Program

%%

Program
    : StatementList
    {
        root = create_node(NODE_PROGRAM, "PROGRAM");
        root->left = $1;
        $$ = root;
    }
    ;

StatementList
    : StatementList Statement
    {
        if ($1 == NULL)
        {
            $$ = $2;
        }
        else
        {
            ASTNode *temp = $1;

            while (temp->next != NULL)
                temp = temp->next;

            temp->next = $2;
            $$ = $1;
        }
    }
    |
    {
        $$ = NULL;
    }
    ;

Statement
    : Declaration
    {
        $$ = $1;
    }
    | Assignment
    {
        $$ = $1;
    }
    | IfStatement
    {
        $$ = $1;
    }
    | WhileStatement
    {
        $$ = $1;
    }
    | PrintStatement
    {
        $$ = $1;
    }
    | Block
    {
        $$ = $1;
    }
    ;
 

Block
    : LBRACE StatementList RBRACE
    {
        $$ = create_node(NODE_BLOCK, NULL);
        $$->left = $2;
    }
    ;

Declaration
    : Type ID SEMICOLON
    {
        $$ = create_node(NODE_DECLARATION, $2);
    }
    ;

Type
    : INT
    | FLOAT
    | BOOL
    ;

Assignment
    : ID ASSIGN Expression SEMICOLON
    {
        $$ = create_node(NODE_ASSIGNMENT, $1);
        $$->left = $3;
    }
    ;

IfStatement
    : IF LPAREN Expression RPAREN Block
    {
        $$ = create_node(NODE_IF, NULL);
        $$->left = $3;
        $$->right = $5;
    }
    | IF LPAREN Expression RPAREN Block ELSE Block
    {
        $$ = create_node(NODE_IF, NULL);
        $$->left = $3;
        $$->right = $5;
        $$->third = $7;
    }
    ;

WhileStatement
    : WHILE LPAREN Expression RPAREN Block
    {
        $$ = create_node(NODE_WHILE, NULL);
        $$->left = $3;
        $$->right = $5;
    }
    ;

PrintStatement
    : PRINT Expression SEMICOLON
    {
        $$ = create_node(NODE_PRINT, NULL);
        $$->left = $2;
    }
    ;
Expression
    : Expression OR Expression
    {
        $$ = create_node(NODE_BINARY_OP, "||");
        $$->left = $1;
        $$->right = $3;
    }
    | Expression AND Expression
    {
        $$ = create_node(NODE_BINARY_OP, "&&");
        $$->left = $1;
        $$->right = $3;
    }
    | Expression EQ Expression
    {
        $$ = create_node(NODE_BINARY_OP, "==");
        $$->left = $1;
        $$->right = $3;
    }
    | Expression NEQ Expression
    {
        $$ = create_node(NODE_BINARY_OP, "!=");
        $$->left = $1;
        $$->right = $3;
    }
    | Expression LT Expression
    {
        $$ = create_node(NODE_BINARY_OP, "<");
        $$->left = $1;
        $$->right = $3;
    }
    | Expression GT Expression
    {
        $$ = create_node(NODE_BINARY_OP, ">");
        $$->left = $1;
        $$->right = $3;
    }
    | Expression LE Expression
    {
        $$ = create_node(NODE_BINARY_OP, "<=");
        $$->left = $1;
        $$->right = $3;
    }
    | Expression GE Expression
    {
        $$ = create_node(NODE_BINARY_OP, ">=");
        $$->left = $1;
        $$->right = $3;
    }
    | Expression PLUS Expression
    {
        $$ = create_node(NODE_BINARY_OP, "+");
        $$->left = $1;
        $$->right = $3;
    }
    | Expression MINUS Expression
    {
        $$ = create_node(NODE_BINARY_OP, "-");
        $$->left = $1;
        $$->right = $3;
    }
    | Expression MUL Expression
    {
        $$ = create_node(NODE_BINARY_OP, "*");
        $$->left = $1;
        $$->right = $3;
    }
    | Expression DIV Expression
    {
        $$ = create_node(NODE_BINARY_OP, "/");
        $$->left = $1;
        $$->right = $3;
    }
    | Expression MOD Expression
    {
        $$ = create_node(NODE_BINARY_OP, "%");
        $$->left = $1;
        $$->right = $3;
    }
    | NOT Expression
    {
        $$ = create_node(NODE_UNARY_OP, "!");
        $$->left = $2;
    }
    | LPAREN Expression RPAREN
    {
        $$ = $2;
    }
    | ID
    {
        $$ = create_node(NODE_IDENTIFIER, $1);
    }
    | INT_CONST
    {
        char buffer[32];
        sprintf(buffer, "%d", $1);
        $$ = create_node(NODE_INT_LITERAL, buffer);
    }
    | FLOAT_CONST
    {
        char buffer[32];
        sprintf(buffer, "%f", $1);
        $$ = create_node(NODE_FLOAT_LITERAL, buffer);
    }
    | TRUE
    {
        $$ = create_node(NODE_BOOL_LITERAL, "true");
    }
    | FALSE
    {
        $$ = create_node(NODE_BOOL_LITERAL, "false");
    }
    ;

%%

void yyerror(const char *s)
{
    fprintf(stderr,
            "\n=========================================\n");
    fprintf(stderr,
            "Syntax Error at line %d\n",
            line_number);
    fprintf(stderr,
            "%s\n",
            s);
    fprintf(stderr,
            "=========================================\n");
}