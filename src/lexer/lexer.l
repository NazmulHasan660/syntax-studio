%option noinput nounput

%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../ast/ast.h"
#include "parser.tab.h"

int line_number = 1;
int lexical_error_count = 0;
extern int dump_tokens;
%}

DIGIT           [0-9]
LETTER          [a-zA-Z_]

ID              {LETTER}({LETTER}|{DIGIT})*
INT_CONST       {DIGIT}+
FLOAT_CONST     {DIGIT}+"."{DIGIT}+
STRING_LITERAL  \"([^\\\"]|\\.)*\"

WHITESPACE      [ \t\r]+
NEWLINE         \n

%%

"#include".*        { if (dump_tokens) printf("[%03d] TOKEN: DIRECTIVE            LEXEME: '%s' (ignored)\n", line_number, yytext); }
"using namespace".* { if (dump_tokens) printf("[%03d] TOKEN: NAMESPACE            LEXEME: '%s' (ignored)\n", line_number, yytext); }
"import".*          { if (dump_tokens) printf("[%03d] TOKEN: IMPORT               LEXEME: '%s' (ignored)\n", line_number, yytext); }
"package".*         { if (dump_tokens) printf("[%03d] TOKEN: PACKAGE              LEXEME: '%s' (ignored)\n", line_number, yytext); }

"public"    { if (dump_tokens) printf("[%03d] TOKEN: MODIFIER             LEXEME: '%s' (ignored)\n", line_number, yytext); }
"private"   { if (dump_tokens) printf("[%03d] TOKEN: MODIFIER             LEXEME: '%s' (ignored)\n", line_number, yytext); }
"protected" { if (dump_tokens) printf("[%03d] TOKEN: MODIFIER             LEXEME: '%s' (ignored)\n", line_number, yytext); }
"static"    { if (dump_tokens) printf("[%03d] TOKEN: MODIFIER             LEXEME: '%s' (ignored)\n", line_number, yytext); }
"final"     { if (dump_tokens) printf("[%03d] TOKEN: MODIFIER             LEXEME: '%s' (ignored)\n", line_number, yytext); }
"const"     { if (dump_tokens) printf("[%03d] TOKEN: MODIFIER             LEXEME: '%s' (ignored)\n", line_number, yytext); }

"int"     { if (dump_tokens) printf("[%03d] TOKEN: INT                  LEXEME: '%s'\n", line_number, yytext); return INT; }
"float"   { if (dump_tokens) printf("[%03d] TOKEN: FLOAT                LEXEME: '%s'\n", line_number, yytext); return FLOAT; }
"double"  { if (dump_tokens) printf("[%03d] TOKEN: FLOAT                LEXEME: '%s'\n", line_number, yytext); return FLOAT; }
"bool"    { if (dump_tokens) printf("[%03d] TOKEN: BOOL                 LEXEME: '%s'\n", line_number, yytext); return BOOL; }
"boolean" { if (dump_tokens) printf("[%03d] TOKEN: BOOL                 LEXEME: '%s'\n", line_number, yytext); return BOOL; }

"return" { if (dump_tokens) printf("[%03d] TOKEN: RETURN               LEXEME: '%s'\n", line_number, yytext); return RETURN; }

"if"    { if (dump_tokens) printf("[%03d] TOKEN: IF                   LEXEME: '%s'\n", line_number, yytext); return IF; }
"else"  { if (dump_tokens) printf("[%03d] TOKEN: ELSE                 LEXEME: '%s'\n", line_number, yytext); return ELSE; }
"while" { if (dump_tokens) printf("[%03d] TOKEN: WHILE                LEXEME: '%s'\n", line_number, yytext); return WHILE; }
"for"   { if (dump_tokens) printf("[%03d] TOKEN: FOR                  LEXEME: '%s'\n", line_number, yytext); return FOR; }
"do"    { if (dump_tokens) printf("[%03d] TOKEN: DO                   LEXEME: '%s'\n", line_number, yytext); return DO; }

"printf"             { if (dump_tokens) printf("[%03d] TOKEN: PRINT_CALL           LEXEME: '%s'\n", line_number, yytext); return PRINT_CALL; }
"System.out.println" { if (dump_tokens) printf("[%03d] TOKEN: PRINT_CALL           LEXEME: '%s'\n", line_number, yytext); return PRINT_CALL; }
"System.out.print"   { if (dump_tokens) printf("[%03d] TOKEN: PRINT_CALL           LEXEME: '%s'\n", line_number, yytext); return PRINT_CALL; }
"std::cout"          { if (dump_tokens) printf("[%03d] TOKEN: COUT                 LEXEME: '%s'\n", line_number, yytext); return COUT; }
"std::endl"          { }
"endl"               { }
"cout"               { if (dump_tokens) printf("[%03d] TOKEN: COUT                 LEXEME: '%s'\n", line_number, yytext); return COUT; }
"print"              { if (dump_tokens) printf("[%03d] TOKEN: PRINT                LEXEME: '%s'\n", line_number, yytext); return PRINT; }

"true"  { if (dump_tokens) printf("[%03d] TOKEN: TRUE                 LEXEME: '%s'\n", line_number, yytext); return TRUE; }
"false" { if (dump_tokens) printf("[%03d] TOKEN: FALSE                LEXEME: '%s'\n", line_number, yytext); return FALSE; }

"==" { if (dump_tokens) printf("[%03d] TOKEN: EQ                   LEXEME: '%s'\n", line_number, yytext); return EQ; }
"!=" { if (dump_tokens) printf("[%03d] TOKEN: NEQ                  LEXEME: '%s'\n", line_number, yytext); return NEQ; }
"<=" { if (dump_tokens) printf("[%03d] TOKEN: LE                   LEXEME: '%s'\n", line_number, yytext); return LE; }
">=" { if (dump_tokens) printf("[%03d] TOKEN: GE                   LEXEME: '%s'\n", line_number, yytext); return GE; }
"&&" { if (dump_tokens) printf("[%03d] TOKEN: AND                  LEXEME: '%s'\n", line_number, yytext); return AND; }
"||" { if (dump_tokens) printf("[%03d] TOKEN: OR                   LEXEME: '%s'\n", line_number, yytext); return OR; }
"<<" { if (dump_tokens) printf("[%03d] TOKEN: LSHIFT               LEXEME: '%s'\n", line_number, yytext); return LSHIFT; }
">>" { if (dump_tokens) printf("[%03d] TOKEN: RSHIFT               LEXEME: '%s'\n", line_number, yytext); return RSHIFT; }

"<" { if (dump_tokens) printf("[%03d] TOKEN: LT                   LEXEME: '%s'\n", line_number, yytext); return LT; }
">" { if (dump_tokens) printf("[%03d] TOKEN: GT                   LEXEME: '%s'\n", line_number, yytext); return GT; }

"++" { if (dump_tokens) printf("[%03d] TOKEN: INC                  LEXEME: '%s'\n", line_number, yytext); return INC; }
"--" { if (dump_tokens) printf("[%03d] TOKEN: DEC                  LEXEME: '%s'\n", line_number, yytext); return DEC; }

"+" { if (dump_tokens) printf("[%03d] TOKEN: PLUS                 LEXEME: '%s'\n", line_number, yytext); return PLUS; }
"-" { if (dump_tokens) printf("[%03d] TOKEN: MINUS                LEXEME: '%s'\n", line_number, yytext); return MINUS; }
"*" { if (dump_tokens) printf("[%03d] TOKEN: MUL                  LEXEME: '%s'\n", line_number, yytext); return MUL; }
"/" { if (dump_tokens) printf("[%03d] TOKEN: DIV                  LEXEME: '%s'\n", line_number, yytext); return DIV; }
"%" { if (dump_tokens) printf("[%03d] TOKEN: MOD                  LEXEME: '%s'\n", line_number, yytext); return MOD; }

"!" { if (dump_tokens) printf("[%03d] TOKEN: NOT                  LEXEME: '%s'\n", line_number, yytext); return NOT; }
"=" { if (dump_tokens) printf("[%03d] TOKEN: ASSIGN               LEXEME: '%s'\n", line_number, yytext); return ASSIGN; }

";" { if (dump_tokens) printf("[%03d] TOKEN: SEMICOLON            LEXEME: '%s'\n", line_number, yytext); return SEMICOLON; }
"," { if (dump_tokens) printf("[%03d] TOKEN: COMMA                LEXEME: '%s'\n", line_number, yytext); return COMMA; }

"(" { if (dump_tokens) printf("[%03d] TOKEN: LPAREN               LEXEME: '%s'\n", line_number, yytext); return LPAREN; }
")" { if (dump_tokens) printf("[%03d] TOKEN: RPAREN               LEXEME: '%s'\n", line_number, yytext); return RPAREN; }
"{" { if (dump_tokens) printf("[%03d] TOKEN: LBRACE               LEXEME: '%s'\n", line_number, yytext); return LBRACE; }
"}" { if (dump_tokens) printf("[%03d] TOKEN: RBRACE               LEXEME: '%s'\n", line_number, yytext); return RBRACE; }

{STRING_LITERAL} {
    if (dump_tokens)
        printf("[%03d] TOKEN: STRING_LITERAL       LEXEME: %s\n", line_number, yytext);

    yylval.sval = strdup(yytext);
    return STRING_LITERAL;
}

{FLOAT_CONST} {
    if (dump_tokens)
        printf("[%03d] TOKEN: FLOAT_CONST          LEXEME: '%s'\n", line_number, yytext);

    yylval.fval = atof(yytext);
    return FLOAT_CONST;
}

{INT_CONST} {
    if (dump_tokens)
        printf("[%03d] TOKEN: INT_CONST            LEXEME: '%s'\n", line_number, yytext);

    yylval.ival = atoi(yytext);
    return INT_CONST;
}

{ID} {
    if (dump_tokens)
        printf("[%03d] TOKEN: ID                   LEXEME: '%s'\n", line_number, yytext);

    yylval.sval = strdup(yytext);
    return ID;
}

{WHITESPACE} { }

{NEWLINE} {
    line_number++;
}

"//".* { }

. {
    if (dump_tokens) {
        fprintf(
            stderr,
            "Lexical Error at line %d: Invalid character '%c'\n",
            line_number,
            yytext[0]
        );
        lexical_error_count++;
    }
}

%%

int yywrap(void)
{
    return 1;
}