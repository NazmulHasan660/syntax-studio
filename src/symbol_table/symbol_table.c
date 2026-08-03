#include "symbol_table.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static Scope *current_scope = NULL;

/*
 * Separate declaration history.
 * This allows variables from closed scopes, such as main(),
 * to remain visible in the final Symbol Table output.
 */
static Symbol *history_head = NULL;
static Symbol *history_tail = NULL;

void symtab_init(void)
{
    symtab_enter_scope();
}

void symtab_enter_scope(void)
{
    Scope *scope = (Scope *)malloc(sizeof(Scope));

    if (scope == NULL)
    {
        fprintf(
            stderr,
            "Memory allocation failed for Scope.\n"
        );
        exit(EXIT_FAILURE);
    }

    scope->symbols = NULL;
    scope->parent = current_scope;

    if (current_scope == NULL)
        scope->level = 0;
    else
        scope->level = current_scope->level + 1;

    current_scope = scope;
}

void symtab_exit_scope(void)
{
    if (current_scope == NULL)
        return;

    Scope *scope = current_scope;
    current_scope = scope->parent;

    Symbol *symbol = scope->symbols;

    while (symbol != NULL)
    {
        Symbol *next = symbol->next;

        free(symbol->name);
        free(symbol->type);
        free(symbol);

        symbol = next;
    }

    free(scope);
}

int symtab_insert(
    const char *name,
    const char *type,
    int line
)
{
    if (current_scope == NULL)
        return 0;

    /*
     * Redeclaration is checked only inside
     * the current scope.
     */
    for (
        Symbol *symbol = current_scope->symbols;
        symbol != NULL;
        symbol = symbol->next
    )
    {
        if (strcmp(symbol->name, name) == 0)
            return 0;
    }

    Symbol *symbol =
        (Symbol *)malloc(sizeof(Symbol));

    if (symbol == NULL)
    {
        fprintf(
            stderr,
            "Memory allocation failed for Symbol.\n"
        );
        exit(EXIT_FAILURE);
    }

    symbol->name = strdup(name);
    symbol->type = strdup(type);
    symbol->line = line;
    symbol->scope = current_scope->level;

    symbol->next = current_scope->symbols;
    current_scope->symbols = symbol;

    /*
     * Keep a separate copy in declaration history.
     * Therefore the final Symbol Table will not become
     * empty when a function or block scope closes.
     */
    Symbol *record =
        (Symbol *)malloc(sizeof(Symbol));

    if (record == NULL)
    {
        fprintf(
            stderr,
            "Memory allocation failed for Symbol.\n"
        );
        exit(EXIT_FAILURE);
    }

    record->name = strdup(name);
    record->type = strdup(type);
    record->line = line;
    record->scope = current_scope->level;
    record->next = NULL;

    if (history_tail == NULL)
    {
        history_head = record;
        history_tail = record;
    }
    else
    {
        history_tail->next = record;
        history_tail = record;
    }

    return 1;
}

Symbol *symtab_lookup(const char *name)
{
    for (
        Scope *scope = current_scope;
        scope != NULL;
        scope = scope->parent
    )
    {
        for (
            Symbol *symbol = scope->symbols;
            symbol != NULL;
            symbol = symbol->next
        )
        {
            if (strcmp(symbol->name, name) == 0)
                return symbol;
        }
    }

    return NULL;
}

void symtab_print(void)
{
    printf(
        "%-15s %-10s %-10s %-10s\n",
        "Name",
        "Type",
        "Scope",
        "Line"
    );

    printf(
        "--------------------------------------------------\n"
    );

    if (history_head == NULL)
    {
        printf("(no variables declared)\n");
        return;
    }

    for (
        Symbol *symbol = history_head;
        symbol != NULL;
        symbol = symbol->next
    )
    {
        printf(
            "%-15s %-10s %-10d %-10d\n",
            symbol->name,
            symbol->type,
            symbol->scope,
            symbol->line
        );
    }
}

void symtab_free(void)
{
    /*
     * Free all active scopes.
     */
    while (current_scope != NULL)
        symtab_exit_scope();

    /*
     * Free the declaration history.
     */
    while (history_head != NULL)
    {
        Symbol *next = history_head->next;

        free(history_head->name);
        free(history_head->type);
        free(history_head);

        history_head = next;
    }

    history_tail = NULL;
}