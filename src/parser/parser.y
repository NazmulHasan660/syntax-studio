%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylex(void);
extern int yylineno;

void yyerror(const char *s);
%}

%define parse.error verbose

%union{
    int    ival;
    float  fval;
    char  *sval;
}

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
    ;

StatementList
    : StatementList Statement
    |
    ;

Statement
    : Declaration
    | Assignment
    | IfStatement
    | WhileStatement
    | PrintStatement
    | Block
    ;

Block
    : LBRACE StatementList RBRACE
    ;

Declaration
    : Type ID SEMICOLON
    ;

Type
    : INT
    | FLOAT
    | BOOL
    ;

Assignment
    : ID ASSIGN Expression SEMICOLON
    ;

IfStatement
    : IF LPAREN Expression RPAREN Block
    | IF LPAREN Expression RPAREN Block ELSE Block
    ;

WhileStatement
    : WHILE LPAREN Expression RPAREN Block
    ;

PrintStatement
    : PRINT Expression SEMICOLON
    ;

Expression
    : Expression OR Expression
    | Expression AND Expression

    | Expression EQ Expression
    | Expression NEQ Expression

    | Expression LT Expression
    | Expression GT Expression
    | Expression LE Expression
    | Expression GE Expression

    | Expression PLUS Expression
    | Expression MINUS Expression

    | Expression MUL Expression
    | Expression DIV Expression
    | Expression MOD Expression

    | NOT Expression

    | LPAREN Expression RPAREN

    | ID
    | INT_CONST
    | FLOAT_CONST
    | TRUE
    | FALSE
    ;
    %%

void yyerror(const char *s)
{
    fprintf(stderr,
            "Syntax Error at line %d: %s\n",
            yylineno,
            s);
}   