#include "semantic.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

#include "../symbol_table/symbol_table.h"

static int error_count = 0;

static void semantic_error(int line, const char *fmt, ...)
{
    va_list args;

    fprintf(stderr, "Semantic Error at line %d: ", line);

    va_start(args, fmt);
    vfprintf(stderr, fmt, args);
    va_end(args);

    fprintf(stderr, "\n");

    error_count++;
}

static int is_numeric(const char *t)
{
    return strcmp(t, "int") == 0 || strcmp(t, "float") == 0;
}

static int is_arithmetic_op(const char *op)
{
    return strcmp(op, "+") == 0 || strcmp(op, "-") == 0 ||
           strcmp(op, "*") == 0 || strcmp(op, "/") == 0 ||
           strcmp(op, "%") == 0;
}

static int is_equality_op(const char *op)
{
    return strcmp(op, "==") == 0 || strcmp(op, "!=") == 0;
}

static int is_relational_op(const char *op)
{
    return strcmp(op, "<") == 0 || strcmp(op, ">") == 0 ||
           strcmp(op, "<=") == 0 || strcmp(op, ">=") == 0;
}

static int is_logical_op(const char *op)
{
    return strcmp(op, "&&") == 0 || strcmp(op, "||") == 0;
}

static void analyze_stmt(ASTNode *stmt);
static void analyze_stmt_list(ASTNode *list);

/*
 * Infers (and records into node->data_type) the type of an
 * expression subtree. Returns a pointer to a static type string:
 * "int", "float", "bool", or "error".
 */
static const char *analyze_expr(ASTNode *expr)
{
    const char *t = "error";

    if (expr == NULL)
        return "error";

    switch (expr->type)
    {
        case NODE_INT_LITERAL:
            t = "int";
            break;

        case NODE_FLOAT_LITERAL:
            t = "float";
            break;

        case NODE_BOOL_LITERAL:
            t = "bool";
            break;

        case NODE_IDENTIFIER:
        {
            Symbol *sym = symtab_lookup(expr->text);

            if (sym == NULL)
            {
                semantic_error(expr->line,
                                "Undeclared variable '%s'",
                                expr->text);
                t = "error";
            }
            else
            {
                t = sym->type;
            }

            break;
        }

        case NODE_UNARY_OP: /* "!" (logical not) or "-" (unary minus) */
        {
            const char *operand_t = analyze_expr(expr->left);
            const char *op = expr->text;

            if (strcmp(operand_t, "error") == 0)
            {
                t = "error";
            }
            else if (strcmp(op, "!") == 0)
            {
                if (strcmp(operand_t, "bool") != 0)
                {
                    semantic_error(expr->line,
                                    "Operator '!' requires a bool operand, got '%s'",
                                    operand_t);
                    t = "error";
                }
                else
                {
                    t = "bool";
                }
            }
            else /* unary "-" */
            {
                if (!is_numeric(operand_t))
                {
                    semantic_error(expr->line,
                                    "Unary '-' requires a numeric operand, got '%s'",
                                    operand_t);
                    t = "error";
                }
                else
                {
                    t = operand_t; /* -int -> int, -float -> float */
                }
            }

            break;
        }

        case NODE_BINARY_OP:
        {
            const char *lt = analyze_expr(expr->left);
            const char *rt = analyze_expr(expr->right);
            const char *op = expr->text;

            int has_error = (strcmp(lt, "error") == 0) ||
                             (strcmp(rt, "error") == 0);

            if (is_arithmetic_op(op))
            {
                if (has_error)
                {
                    t = "error";
                }
                else if (strcmp(lt, "bool") == 0 || strcmp(rt, "bool") == 0)
                {
                    semantic_error(expr->line,
                                    "Operator '%s' cannot be applied to bool operands",
                                    op);
                    t = "error";
                }
                else if (strcmp(lt, "float") == 0 || strcmp(rt, "float") == 0)
                {
                    t = "float"; /* int + float -> float */
                }
                else
                {
                    t = "int";
                }
            }
            else if (is_equality_op(op))
            {
                if (!has_error)
                {
                    int compatible = (strcmp(lt, rt) == 0) ||
                                      (is_numeric(lt) && is_numeric(rt));

                    if (!compatible)
                    {
                        semantic_error(expr->line,
                                        "Cannot compare '%s' with '%s' using '%s'",
                                        lt, rt, op);
                    }
                }

                t = "bool";
            }
            else if (is_relational_op(op))
            {
                if (!has_error && !(is_numeric(lt) && is_numeric(rt)))
                {
                    semantic_error(expr->line,
                                    "Operator '%s' requires numeric operands, got '%s' and '%s'",
                                    op, lt, rt);
                }

                t = "bool";
            }
            else if (is_logical_op(op))
            {
                if (!has_error)
                {
                    if (strcmp(lt, "bool") != 0)
                    {
                        semantic_error(expr->line,
                                        "Operator '%s' requires bool operands, got '%s'",
                                        op, lt);
                    }
                    else if (strcmp(rt, "bool") != 0)
                    {
                        semantic_error(expr->line,
                                        "Operator '%s' requires bool operands, got '%s'",
                                        op, rt);
                    }
                }

                t = "bool";
            }
            else
            {
                t = "error";
            }

            break;
        }

        default:
            t = "error";
            break;
    }

    expr->data_type = strdup(t);
    return expr->data_type;
}

static void analyze_stmt(ASTNode *stmt)
{
    if (stmt == NULL)
        return;

    switch (stmt->type)
    {
        case NODE_DECLARATION:
        {
            if (!symtab_insert(stmt->text, stmt->data_type, stmt->line))
            {
                semantic_error(stmt->line,
                                "Redeclaration of variable '%s'",
                                stmt->text);
            }

            break;
        }

        case NODE_ASSIGNMENT:
        {
            Symbol *sym = symtab_lookup(stmt->text);
            const char *rhs_t = analyze_expr(stmt->left);

            if (sym == NULL)
            {
                semantic_error(stmt->line,
                                "Assignment to undeclared variable '%s'",
                                stmt->text);
            }
            else if (strcmp(rhs_t, "error") != 0 &&
                     strcmp(sym->type, rhs_t) != 0)
            {
                /* Allow the usual int -> float widening. */
                int is_widening = strcmp(sym->type, "float") == 0 &&
                                   strcmp(rhs_t, "int") == 0;

                if (!is_widening)
                {
                    semantic_error(stmt->line,
                                    "Type mismatch: cannot assign '%s' to variable '%s' of type '%s'",
                                    rhs_t, stmt->text, sym->type);
                }
            }

            break;
        }

        case NODE_IF:
        {
            const char *cond_t = analyze_expr(stmt->left);

            if (strcmp(cond_t, "bool") != 0 && strcmp(cond_t, "error") != 0)
            {
                semantic_error(stmt->line,
                                "Condition of 'if' must be bool, got '%s'",
                                cond_t);
            }

            analyze_stmt(stmt->right); /* then-block */

            if (stmt->third != NULL)
                analyze_stmt(stmt->third); /* else-block */

            break;
        }

        case NODE_WHILE:
        {
            const char *cond_t = analyze_expr(stmt->left);

            if (strcmp(cond_t, "bool") != 0 && strcmp(cond_t, "error") != 0)
            {
                semantic_error(stmt->line,
                                "Condition of 'while' must be bool, got '%s'",
                                cond_t);
            }

            analyze_stmt(stmt->right); /* body block */

            break;
        }

        case NODE_PRINT:
        {
            analyze_expr(stmt->left);
            break;
        }

        case NODE_BLOCK:
        {
            symtab_enter_scope();
            analyze_stmt_list(stmt->left);
            symtab_exit_scope();
            break;
        }

        default:
            break;
    }
}

static void analyze_stmt_list(ASTNode *list)
{
    for (ASTNode *s = list; s != NULL; s = s->next)
        analyze_stmt(s);
}

int analyze_semantics(ASTNode *root)
{
    error_count = 0;

    symtab_init(); /* global scope */

    if (root != NULL && root->type == NODE_PROGRAM)
        analyze_stmt_list(root->left);

    symtab_free();

    return error_count;
}