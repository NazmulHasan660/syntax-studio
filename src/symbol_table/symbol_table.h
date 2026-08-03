#ifndef SYMBOL_TABLE_H
#define SYMBOL_TABLE_H

typedef struct Symbol
{
    char *name;
    char *type;

    /* Declaration information */
    int line;
    int scope;

    struct Symbol *next;

} Symbol;

typedef struct Scope
{
    Symbol *symbols;

    /* 0 = global, 1+ = nested scope */
    int level;

    struct Scope *parent;

} Scope;

/* Initialize symbol table with global scope */
void symtab_init(void);

/* Scope management */
void symtab_enter_scope(void);
void symtab_exit_scope(void);

/* Insert and lookup variables */
int symtab_insert(
    const char *name,
    const char *type,
    int line
);

Symbol *symtab_lookup(const char *name);

/* Print all declarations */
void symtab_print(void);

/* Free all allocated memory */
void symtab_free(void);

#endif