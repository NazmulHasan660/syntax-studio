%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../ast/ast.h"

extern int yylex(void);
extern int line_number;

void yyerror(const char *s);

ASTNode *root = NULL;
int syntax_error_count = 0;
%}

%code requires {
#include "../ast/ast.h"
}

%define parse.error verbose

%union {
    int ival;
    float fval;
    char *sval;
    ASTNode *node;
}

%type <node> Program
%type <node> OuterDeclarations
%type <node> StatementList
%type <node> Statement
%type <node> Block
%type <node> Declaration
%type <node> DeclarationNoSemi
%type <node> DeclList
%type <node> DeclItem
%type <node> Assignment
%type <node> IfStatement
%type <node> WhileStatement
%type <node> ForStatement
%type <node> DoWhileStatement
%type <node> ForInit
%type <node> ForUpdate
%type <node> ReturnStatement
%type <node> PrintStatement
%type <node> Expression
%type <node> ExpressionList
%type <sval> Type

%token INT FLOAT BOOL
%token IF ELSE WHILE FOR DO PRINT PRINT_CALL COUT RETURN
%token TRUE FALSE

%token <sval> ID STRING_LITERAL
%token <ival> INT_CONST
%token <fval> FLOAT_CONST

%token PLUS MINUS MUL DIV MOD INC DEC
%token LT GT LE GE EQ NEQ LSHIFT RSHIFT
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
%precedence NOT
%precedence UMINUS

%destructor { free($$); } <sval>

%precedence LOWER_THAN_ELSE
%precedence ELSE

%start Program

%%

Program
    : OuterDeclarations
    {
        root = create_node(NODE_PROGRAM, "PROGRAM");
        root->left = $1;
        $$ = root;
    }
    ;

OuterDeclarations
    : %empty
    {
        $$ = NULL;
    }
    | OuterDeclarations Statement
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
    | %empty
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
    | ForStatement
    {
        $$ = $1;
    }
    | DoWhileStatement
    {
        $$ = $1;
    }
    | ReturnStatement
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
    | SEMICOLON
    {
        $$ = NULL;
    }
    | error SEMICOLON
    {
        $$ = NULL;
        yyerrok;
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
    : DeclarationNoSemi SEMICOLON
    {
        $$ = $1;
    }
    ;

DeclarationNoSemi
    : Type DeclList
    {
        ASTNode *head = NULL;
        ASTNode *curr = NULL;

        ASTNode *item = $2;

        while (item != NULL)
        {
            ASTNode *next_item = item->next;
            item->next = NULL;

            if (item->type == NODE_IDENTIFIER)
            {
                ASTNode *decl =
                    create_node(NODE_DECLARATION, item->text);

                decl->data_type = strdup($1);

                if (head == NULL)
                {
                    head = decl;
                    curr = decl;
                }
                else
                {
                    curr->next = decl;
                    curr = decl;
                }
            }
            else if (item->type == NODE_ASSIGNMENT)
            {
                ASTNode *decl =
                    create_node(NODE_DECLARATION, item->text);

                decl->data_type = strdup($1);

                if (head == NULL)
                {
                    head = decl;
                    curr = decl;
                }
                else
                {
                    curr->next = decl;
                    curr = decl;
                }

                curr->next = item;
                curr = item;
            }

            item = next_item;
        }

        free($1);
        $$ = head;
    }
    ;

DeclList
    : DeclList COMMA DeclItem
    {
        ASTNode *temp = $1;

        while (temp->next != NULL)
            temp = temp->next;

        temp->next = $3;
        $$ = $1;
    }
    | DeclItem
    {
        $$ = $1;
    }
    ;

DeclItem
    : ID
    {
        $$ = create_node(NODE_IDENTIFIER, $1);
        free($1);
    }
    | ID ASSIGN Expression
    {
        $$ = create_node(NODE_ASSIGNMENT, $1);
        $$->left = $3;
        free($1);
    }
    ;

Type
    : INT
    {
        $$ = strdup("int");
    }
    | FLOAT
    {
        $$ = strdup("float");
    }
    | BOOL
    {
        $$ = strdup("bool");
    }
    ;

Assignment
    : ID ASSIGN Expression SEMICOLON
    {
        $$ = create_node(NODE_ASSIGNMENT, $1);
        $$->left = $3;
        free($1);
    }
    | ID INC SEMICOLON
    {
        $$ = create_node(NODE_ASSIGNMENT, $1);

        ASTNode *add = create_node(NODE_BINARY_OP, "+");
        add->left = create_node(NODE_IDENTIFIER, $1);
        add->right = create_node(NODE_INT_LITERAL, "1");

        $$->left = add;
        free($1);
    }
    | ID DEC SEMICOLON
    {
        $$ = create_node(NODE_ASSIGNMENT, $1);

        ASTNode *sub = create_node(NODE_BINARY_OP, "-");
        sub->left = create_node(NODE_IDENTIFIER, $1);
        sub->right = create_node(NODE_INT_LITERAL, "1");

        $$->left = sub;
        free($1);
    }
    ;

IfStatement
    : IF LPAREN Expression RPAREN Statement %prec LOWER_THAN_ELSE
    {
        $$ = create_node(NODE_IF, NULL);
        $$->left = $3;
        $$->right = $5;
    }
    | IF LPAREN Expression RPAREN Statement ELSE Statement
    {
        $$ = create_node(NODE_IF, NULL);
        $$->left = $3;
        $$->right = $5;
        $$->third = $7;
    }
    ;

WhileStatement
    : WHILE LPAREN Expression RPAREN Statement
    {
        $$ = create_node(NODE_WHILE, NULL);
        $$->left = $3;
        $$->right = $5;
    }
    ;

ForStatement
    : FOR LPAREN ForInit SEMICOLON Expression SEMICOLON ForUpdate RPAREN Statement
    {
        ASTNode *for_node = create_node(NODE_FOR, NULL);
        for_node->left = $5;
        for_node->right = $9;
        for_node->third = $7;

        if ($3 != NULL)
        {
            ASTNode *tail = $3;

            while (tail->next != NULL)
                tail = tail->next;

            tail->next = for_node;

            $$ = create_node(NODE_BLOCK, NULL);
            $$->left = $3;
        }
        else
        {
            $$ = for_node;
        }
    }
    ;

DoWhileStatement
    : DO Statement WHILE LPAREN Expression RPAREN SEMICOLON
    {
        $$ = create_node(NODE_DO_WHILE, NULL);
        $$->left = $5;
        $$->right = $2;
    }
    ;

ForInit
    : DeclarationNoSemi
    {
        $$ = $1;
    }
    | ID ASSIGN Expression
    {
        $$ = create_node(NODE_ASSIGNMENT, $1);
        $$->left = $3;
        free($1);
    }
    | %empty
    {
        $$ = NULL;
    }
    ;

ForUpdate
    : ID ASSIGN Expression
    {
        $$ = create_node(NODE_ASSIGNMENT, $1);
        $$->left = $3;
        free($1);
    }
    | ID INC
    {
        $$ = create_node(NODE_ASSIGNMENT, $1);

        ASTNode *add = create_node(NODE_BINARY_OP, "+");
        add->left = create_node(NODE_IDENTIFIER, $1);
        add->right = create_node(NODE_INT_LITERAL, "1");

        $$->left = add;
        free($1);
    }
    | ID DEC
    {
        $$ = create_node(NODE_ASSIGNMENT, $1);

        ASTNode *sub = create_node(NODE_BINARY_OP, "-");
        sub->left = create_node(NODE_IDENTIFIER, $1);
        sub->right = create_node(NODE_INT_LITERAL, "1");

        $$->left = sub;
        free($1);
    }
    | %empty
    {
        $$ = NULL;
    }
    ;

ReturnStatement
    : RETURN Expression SEMICOLON
    {
        $$ = create_node(NODE_UNARY_OP, "return");
        $$->left = $2;
    }
    | RETURN SEMICOLON
    {
        $$ = create_node(NODE_UNARY_OP, "return");
    }
    ;

PrintStatement
    : PRINT Expression SEMICOLON
    {
        $$ = create_node(NODE_PRINT, NULL);
        $$->left = $2;
    }
    | COUT LSHIFT Expression SEMICOLON
    {
        $$ = create_node(NODE_PRINT, NULL);
        $$->left = $3;
    }
    | PRINT_CALL LPAREN ExpressionList RPAREN SEMICOLON
    {
        $$ = create_node(NODE_PRINT, NULL);
        $$->left = $3;
    }
    ;

ExpressionList
    : ExpressionList COMMA Expression
    {
        ASTNode *temp = $1;

        while (temp->next != NULL)
            temp = temp->next;

        temp->next = $3;
        $$ = $1;
    }
    | Expression
    {
        $$ = $1;
    }
    | %empty
    {
        $$ = NULL;
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
    | MINUS Expression %prec UMINUS
    {
        $$ = create_node(NODE_UNARY_OP, "-");
        $$->left = $2;
    }
    | LPAREN Expression RPAREN
    {
        $$ = $2;
    }
    | ID
    {
        $$ = create_node(NODE_IDENTIFIER, $1);
        free($1);
    }
    | INT_CONST
    {
        char buffer[64];
        snprintf(buffer, sizeof(buffer), "%d", $1);

        $$ = create_node(NODE_INT_LITERAL, buffer);
    }
    | FLOAT_CONST
    {
        char buffer[64];
        snprintf(buffer, sizeof(buffer), "%f", $1);

        $$ = create_node(NODE_FLOAT_LITERAL, buffer);
    }
    | STRING_LITERAL
    {
        $$ = create_node(NODE_INT_LITERAL, $1);
        free($1);
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
    syntax_error_count++;

    fprintf(stderr, "\n=========================================\n");
    fprintf(
        stderr,
        "Syntax Error at line %d: %s\n",
        line_number,
        s
    );
    fprintf(stderr, "=========================================\n");
}