#include "optimizer.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_TOKENS 8
#define MAX_ITERATIONS 10

/* ---------- small text helpers (TAC lines are plain strings) ---------- */

static int is_numeric_literal(const char *text)
{
    int index = 0;
    int saw_digit = 0;
    int saw_dot = 0;

    if (text[0] == '\0')
        return 0;

    if (text[index] == '-')
        index++;

    for (; text[index] != '\0'; index++)
    {
        if (isdigit((unsigned char)text[index]))
        {
            saw_digit = 1;
        }
        else if (text[index] == '.' && !saw_dot)
        {
            saw_dot = 1;
        }
        else
        {
            return 0;
        }
    }

    return saw_digit;
}

static int is_temp_name(const char *text)
{
    if (text[0] != 't' || !isdigit((unsigned char)text[1]))
        return 0;

    for (int index = 1; text[index] != '\0'; index++)
    {
        if (!isdigit((unsigned char)text[index]))
            return 0;
    }

    return 1;
}

/*
 * Splits a TAC line on single spaces (the format every emit_tac()
 * call in tac.c consistently uses), but never splits inside a
 * double-quoted string literal (so a print of a multi-word string
 * stays a single token instead of being torn apart on its spaces).
 */
static int split_line(char *mutable_copy, char *tokens[MAX_TOKENS])
{
    int count = 0;
    char *cursor = mutable_copy;

    while (*cursor == ' ')
        cursor++;

    while (*cursor != '\0' && count < MAX_TOKENS)
    {
        tokens[count++] = cursor;

        int in_quotes = 0;

        while (*cursor != '\0' && (in_quotes || *cursor != ' '))
        {
            if (*cursor == '"')
                in_quotes = !in_quotes;
            else if (*cursor == '\\' && in_quotes && *(cursor + 1) != '\0')
                cursor++;

            cursor++;
        }

        if (*cursor == ' ')
        {
            *cursor = '\0';
            cursor++;

            while (*cursor == ' ')
                cursor++;
        }
    }

    return count;
}

static int is_foldable_line(int token_count, char *tokens[MAX_TOKENS])
{
    if (token_count != 5)
        return 0;

    if (strcmp(tokens[1], "=") != 0)
        return 0;

    const char *op = tokens[3];

    if (strlen(op) != 1 || strchr("+-*/%", op[0]) == NULL)
        return 0;

    return is_numeric_literal(tokens[2]) && is_numeric_literal(tokens[4]);
}

static int fold_arithmetic(
    const char *left_text,
    char op,
    const char *right_text,
    char *result,
    size_t result_size
)
{
    int integer_mode =
        strchr(left_text, '.') == NULL &&
        strchr(right_text, '.') == NULL;

    double left = atof(left_text);
    double right = atof(right_text);

    if ((op == '/' || op == '%') && right == 0.0)
    {
        /* Never silently resolve a division by zero. */
        return 0;
    }

    if (integer_mode)
    {
        long long a = (long long)left;
        long long b = (long long)right;
        long long value;

        switch (op)
        {
            case '+': value = a + b; break;
            case '-': value = a - b; break;
            case '*': value = a * b; break;
            case '/': value = a / b; break;
            case '%': value = a % b; break;
            default: return 0;
        }

        snprintf(result, result_size, "%lld", value);
    }
    else
    {
        if (op == '%')
        {
            /* '%' is not defined on float operands in this language. */
            return 0;
        }

        double value;

        switch (op)
        {
            case '+': value = left + right; break;
            case '-': value = left - right; break;
            case '*': value = left * right; break;
            case '/': value = left / right; break;
            default: return 0;
        }

        snprintf(result, result_size, "%f", value);
    }

    return 1;
}

/* ---------- pass 1: constant folding ---------- */

static TACList fold_pass(const TACList *input)
{
    TACList output;
    output.lines = (char **)malloc(sizeof(char *) * (size_t)input->count);
    output.count = 0;
    output.capacity = input->count;

    for (int i = 0; i < input->count; i++)
    {
        char buffer[256];
        strncpy(buffer, input->lines[i], sizeof(buffer) - 1);
        buffer[sizeof(buffer) - 1] = '\0';

        char *tokens[MAX_TOKENS];
        int token_count = split_line(buffer, tokens);

        if (is_foldable_line(token_count, tokens))
        {
            char folded[64];

            if (fold_arithmetic(tokens[2], tokens[3][0], tokens[4], folded, sizeof(folded)))
            {
                char new_line[256];
                snprintf(new_line, sizeof(new_line), "%s = %s", tokens[0], folded);
                output.lines[output.count++] = strdup(new_line);
                continue;
            }
        }

        output.lines[output.count++] = strdup(input->lines[i]);
    }

    return output;
}

/* ---------- pass 2: constant propagation + dead-line elimination ---------- */

typedef struct
{
    char name[16];
    char value[64];
} ConstBinding;

static TACList propagate_pass(const TACList *input, int *changed)
{
    ConstBinding bindings[256];
    int binding_count = 0;
    int drop_line[4096] = {0};

    *changed = 0;

    /* Find every "tN = LITERAL" line. */
    for (int i = 0; i < input->count && i < 4096; i++)
    {
        char buffer[256];
        strncpy(buffer, input->lines[i], sizeof(buffer) - 1);
        buffer[sizeof(buffer) - 1] = '\0';

        char *tokens[MAX_TOKENS];
        int token_count = split_line(buffer, tokens);

        if (
            token_count == 3 &&
            strcmp(tokens[1], "=") == 0 &&
            is_temp_name(tokens[0]) &&
            is_numeric_literal(tokens[2]) &&
            binding_count < 256
        )
        {
            strncpy(bindings[binding_count].name, tokens[0], sizeof(bindings[0].name) - 1);
            bindings[binding_count].name[sizeof(bindings[0].name) - 1] = '\0';
            strncpy(bindings[binding_count].value, tokens[2], sizeof(bindings[0].value) - 1);
            bindings[binding_count].value[sizeof(bindings[0].value) - 1] = '\0';
            binding_count++;
            drop_line[i] = 1;
        }
    }

    TACList output;
    output.lines = (char **)malloc(sizeof(char *) * (size_t)input->count);
    output.count = 0;
    output.capacity = input->count;

    for (int i = 0; i < input->count; i++)
    {
        if (i < 4096 && drop_line[i])
        {
            *changed = 1;
            continue;
        }

        char buffer[256];
        strncpy(buffer, input->lines[i], sizeof(buffer) - 1);
        buffer[sizeof(buffer) - 1] = '\0';

        char *tokens[MAX_TOKENS];
        int token_count = split_line(buffer, tokens);

        char rebuilt[256];
        rebuilt[0] = '\0';

        for (int t = 0; t < token_count; t++)
        {
            char substituted[80] = "";
            const char *to_write = tokens[t];

            if (t > 0)
            {
                const char *prefix = "";
                const char *bare = tokens[t];

                if (tokens[t][0] == '-' || tokens[t][0] == '!')
                {
                    prefix = (tokens[t][0] == '-') ? "-" : "!";
                    bare = tokens[t] + 1;
                }

                for (int b = 0; b < binding_count; b++)
                {
                    if (strcmp(bare, bindings[b].name) == 0)
                    {
                        snprintf(substituted, sizeof(substituted), "%s%s", prefix, bindings[b].value);
                        to_write = substituted;
                        *changed = 1;
                        break;
                    }
                }
            }

            strncat(rebuilt, to_write, sizeof(rebuilt) - strlen(rebuilt) - 1);

            if (t < token_count - 1)
                strncat(rebuilt, " ", sizeof(rebuilt) - strlen(rebuilt) - 1);
        }

        output.lines[output.count++] = strdup(token_count > 0 ? rebuilt : input->lines[i]);
    }

    return output;
}

/* ---------- driver ---------- */

TACList optimize_tac(const TACList *input)
{
    TACList current;
    current.lines = (char **)malloc(sizeof(char *) * (size_t)(input->count > 0 ? input->count : 1));
    current.count = input->count;
    current.capacity = input->count;

    for (int i = 0; i < input->count; i++)
        current.lines[i] = strdup(input->lines[i]);

    for (int iteration = 0; iteration < MAX_ITERATIONS; iteration++)
    {
        TACList folded = fold_pass(&current);
        free_tac(&current);

        int changed = 0;
        TACList propagated = propagate_pass(&folded, &changed);
        free_tac(&folded);

        current = propagated;

        if (!changed)
            break;
    }

    return current;
}
