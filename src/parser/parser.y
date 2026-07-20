%{
#include <stdio.h>
#include <stdlib.h>

extern int yylex(void);
extern int line_number;

void yyerror(const char *s);
%}

%token INT FLOAT BOOL
%token IF ELSE WHILE PRINT
%token TRUE FALSE

%token ID
%token INT_CONST FLOAT_CONST

%token PLUS MINUS MUL DIV MOD
%token LT GT LE GE EQ NEQ
%token AND OR NOT
%token ASSIGN

%token LPAREN RPAREN
%token LBRACE RBRACE
%token SEMICOLON COMMA

%start Program

%%

Program
    :
    ;

%%

void yyerror(const char *s)
{
    fprintf(stderr, "Syntax Error at line %d: %s\n", line_number, s);
}