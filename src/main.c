#include <stdio.h>

extern int yyparse(void);

int main(void)
{
    printf("=== Mini Compiler ===\n");

    if (yyparse() == 0)
    {
        printf("Parsing completed successfully.\n");
    }
    else
    {
        printf("Parsing failed.\n");
    }

    return 0;
}