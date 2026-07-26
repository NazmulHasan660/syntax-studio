#include "symbol_table.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static Scope *current_scope = NULL;

void symtab_init(void)
{
    symtab_enter_scope(); /* global scope */
}

void symtab_enter_scope(void)
{
    Scope *scope = (Scope *)malloc(sizeof(Scope));

    if (scope == NULL)
    {
        fprintf(stderr, "Memory allocation failed.\n");
        exit(EXIT_FAILURE);
    }

    scope->symbols = NULL;
    scope->parent = current_scope;
    scope->level = (current_scope == NULL) ? 0 : current_scope->level + 1;

    current_scope = scope;
}

void symtab_exit_scope(void)
{
    if (current_scope == NULL)
        return;

    Scope *scope = current_scope;
    current_scope = scope->parent;

    Symbol *sym = scope->symbols;
    while (sym != NULL)
    {
        Symbol *next = sym->next;
        free(sym->name);
        free(sym->type);
        free(sym);
        sym = next;
    }

    free(scope);
}

int symtab_insert(const char *name, const char *type, int line)
{
    if (current_scope == NULL)
        return 0;

    /* Redeclaration is only an error within the SAME scope. */
    for (Symbol *sym = current_scope->symbols; sym != NULL; sym = sym->next)
    {
        if (strcmp(sym->name, name) == 0)
            return 0;
    }

    Symbol *sym = (Symbol *)malloc(sizeof(Symbol));

    if (sym == NULL)
    {
        fprintf(stderr, "Memory allocation failed.\n");
        exit(EXIT_FAILURE);
    }

    sym->name = strdup(name);
    sym->type = strdup(type);
    sym->line = line;
    sym->scope = current_scope->level;

    /* Insert at the head of the current scope's list. */
    sym->next = current_scope->symbols;
    current_scope->symbols = sym;

    return 1;
}

Symbol *symtab_lookup(const char *name)
{
    for (Scope *scope = current_scope; scope != NULL; scope = scope->parent)
    {
        for (Symbol *sym = scope->symbols; sym != NULL; sym = sym->next)
        {
            if (strcmp(sym->name, name) == 0)
                return sym;
        }
    }

    return NULL;
}

void symtab_free(void)
{
    while (current_scope != NULL)
        symtab_exit_scope();
}