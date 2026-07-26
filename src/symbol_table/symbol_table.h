#ifndef SYMBOL_TABLE_H
#define SYMBOL_TABLE_H

/*
 * A single declared variable.
 */
typedef struct Symbol
{
    char *name;
    char *type;   /* "int" / "float" / "bool" */
    int line;     /* line of declaration */
    int scope;    /* nesting depth: 0 = global, 1 = one block deep, ... */

    struct Symbol *next; /* next symbol in the same scope */
} Symbol;

/*
 * A scope is a linked list of symbols plus a pointer to its
 * enclosing (parent) scope. Scopes are chained into a stack:
 * current_scope always points at the innermost/active scope.
 */
typedef struct Scope
{
    Symbol *symbols;
    int level;            /* 0 = global scope, increases with nesting */
    struct Scope *parent;
} Scope;

/* Initializes the symbol table and opens the global scope. */
void symtab_init(void);

/* Opens a new nested scope (e.g. on entering a block). */
void symtab_enter_scope(void);

/* Closes the current scope and returns to its parent. */
void symtab_exit_scope(void);

/*
 * Inserts a new symbol into the CURRENT scope only.
 * Returns 1 on success, 0 if a symbol with this name already
 * exists in the current scope (redeclaration).
 */
int symtab_insert(const char *name, const char *type, int line);

/*
 * Looks up a symbol by name, searching the current scope and then
 * every enclosing scope outward. Returns NULL if not found anywhere.
 */
Symbol *symtab_lookup(const char *name);

/* Frees all scopes and symbols. */
void symtab_free(void);

#endif