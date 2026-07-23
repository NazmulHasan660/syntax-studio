%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../ast/ast.h"
#include "parser.tab.h"

int line_number = 1;
%}

DIGIT           [0-9]
LETTER          [a-zA-Z_]

ID              {LETTER}({LETTER}|{DIGIT})*
INT_CONST       {DIGIT}+
FLOAT_CONST     {DIGIT}+"."{DIGIT}+

WHITESPACE      [ \t\r]+
NEWLINE         \n

%%

"int"           { return INT; }
"float"         { return FLOAT; }
"bool"          { return BOOL; }

"if"            { return IF; }
"else"          { return ELSE; }
"while"         { return WHILE; }

"print"         { return PRINT; }

"true"          { return TRUE; }
"false"         { return FALSE; }

"=="            { return EQ; }
"!="            { return NEQ; }
"<="            { return LE; }
">="            { return GE; }
"&&"            { return AND; }
"||"            { return OR; }

"<"             { return LT; }
">"             { return GT; }

"+"             { return PLUS; }
"-"             { return MINUS; }
"*"             { return MUL; }
"/"             { return DIV; }
"%"             { return MOD; }

"!"             { return NOT; }
"="             { return ASSIGN; }

";"             { return SEMICOLON; }
","             { return COMMA; }

"("             { return LPAREN; }
")"             { return RPAREN; }

"{"             { return LBRACE; }
"}"             { return RBRACE; }

{FLOAT_CONST}   {
                    yylval.fval = atof(yytext);
                    return FLOAT_CONST;
                }

{INT_CONST}     {
                    yylval.ival = atoi(yytext);
                    return INT_CONST;
                }

{ID}            {
                    yylval.sval = strdup(yytext);
                    return ID;
                }

{WHITESPACE}    { }

{NEWLINE}       {
                    line_number++;
                }

"//".*          { }

.               {
                    printf("Lexical Error at line %d: Invalid character '%c'\n",
                           line_number,
                           yytext[0]);
                }

%%

int yywrap(void)
{
    return 1;
}