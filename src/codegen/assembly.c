#include "assembly.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

#define MAX_TOKENS 8

/* ---------- growable output buffer ---------- */

typedef struct
{
    char *text;
    size_t length;
    size_t capacity;
} StrBuf;

static void strbuf_init(StrBuf *buf)
{
    buf->capacity = 1024;
    buf->length = 0;
    buf->text = (char *)malloc(buf->capacity);
    buf->text[0] = '\0';
}

static void strbuf_append(StrBuf *buf, const char *text)
{
    size_t add_length = strlen(text);

    while (buf->length + add_length + 1 > buf->capacity)
    {
        buf->capacity *= 2;
        buf->text = (char *)realloc(buf->text, buf->capacity);
    }

    memcpy(buf->text + buf->length, text, add_length + 1);
    buf->length += add_length;
}

static void emit_asm(StrBuf *buf, const char *format, ...)
{
    char line[256];
    va_list arguments;

    va_start(arguments, format);
    vsnprintf(line, sizeof(line), format, arguments);
    va_end(arguments);

    strbuf_append(buf, line);
    strbuf_append(buf, "\n");
}

/* ---------- tokenizing (same convention as optimizer.c) ---------- */

/*
 * Splits a TAC line on single spaces, but never splits inside a
 * double-quoted string literal (same convention as optimizer.c).
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

static int is_string_literal(const char *text)
{
    return text[0] == '"';
}

/*
 * The language's bool literals are the words "true"/"false"; x86
 * has no such immediate, so translate them to the numeric form (the
 * same 1/0 convention the rest of this generator already uses for
 * relational results via SETcc).
 */
static const char *translate_operand(const char *text)
{
    if (strcmp(text, "true") == 0)
        return "1";

    if (strcmp(text, "false") == 0)
        return "0";

    return text;
}

/* ---------- per-operator translation ---------- */

static void emit_binary_op(StrBuf *buf, const char *dest, const char *left, const char *op, const char *right)
{
    if (strcmp(op, "+") == 0)
    {
        emit_asm(buf, "    MOV EAX, %s", left);
        emit_asm(buf, "    ADD EAX, %s", right);
        emit_asm(buf, "    MOV [%s], EAX", dest);
    }
    else if (strcmp(op, "-") == 0)
    {
        emit_asm(buf, "    MOV EAX, %s", left);
        emit_asm(buf, "    SUB EAX, %s", right);
        emit_asm(buf, "    MOV [%s], EAX", dest);
    }
    else if (strcmp(op, "*") == 0)
    {
        emit_asm(buf, "    MOV EAX, %s", left);
        emit_asm(buf, "    IMUL EAX, %s", right);
        emit_asm(buf, "    MOV [%s], EAX", dest);
    }
    else if (strcmp(op, "/") == 0)
    {
        emit_asm(buf, "    MOV EAX, %s", left);
        emit_asm(buf, "    CDQ");
        emit_asm(buf, "    IDIV %s", right);
        emit_asm(buf, "    MOV [%s], EAX", dest);
    }
    else if (strcmp(op, "%") == 0)
    {
        emit_asm(buf, "    MOV EAX, %s", left);
        emit_asm(buf, "    CDQ");
        emit_asm(buf, "    IDIV %s", right);
        emit_asm(buf, "    MOV [%s], EDX", dest);
    }
    else if (strcmp(op, "&&") == 0)
    {
        emit_asm(buf, "    MOV EAX, %s", left);
        emit_asm(buf, "    AND EAX, %s", right);
        emit_asm(buf, "    MOV [%s], EAX", dest);
    }
    else if (strcmp(op, "||") == 0)
    {
        emit_asm(buf, "    MOV EAX, %s", left);
        emit_asm(buf, "    OR EAX, %s", right);
        emit_asm(buf, "    MOV [%s], EAX", dest);
    }
    else
    {
        const char *set_instruction = NULL;

        if (strcmp(op, "==") == 0) set_instruction = "SETE";
        else if (strcmp(op, "!=") == 0) set_instruction = "SETNE";
        else if (strcmp(op, "<") == 0) set_instruction = "SETL";
        else if (strcmp(op, ">") == 0) set_instruction = "SETG";
        else if (strcmp(op, "<=") == 0) set_instruction = "SETLE";
        else if (strcmp(op, ">=") == 0) set_instruction = "SETGE";

        if (set_instruction != NULL)
        {
            emit_asm(buf, "    MOV EAX, %s", left);
            emit_asm(buf, "    CMP EAX, %s", right);
            emit_asm(buf, "    %s AL", set_instruction);
            emit_asm(buf, "    MOV [%s], AL", dest);
        }
        else
        {
            emit_asm(buf, "    ; unrecognized operator '%s', skipped", op);
        }
    }
}

static void emit_unary_op(StrBuf *buf, const char *dest, char op, const char *operand)
{
    emit_asm(buf, "    MOV EAX, %s", operand);

    if (op == '-')
        emit_asm(buf, "    NEG EAX");
    else if (op == '!')
        emit_asm(buf, "    XOR EAX, 1");

    emit_asm(buf, "    MOV [%s], EAX", dest);
}

/* ---------- driver ---------- */

char *generate_assembly(const TACList *tac)
{
    StrBuf buf;
    strbuf_init(&buf);

    emit_asm(&buf, "SECTION .text");
    emit_asm(&buf, "GLOBAL _main");
    emit_asm(&buf, "");
    emit_asm(&buf, "_main:");
    emit_asm(&buf, "    PUSH EBP");
    emit_asm(&buf, "    MOV EBP, ESP");
    emit_asm(&buf, "");

    for (int i = 0; i < tac->count; i++)
    {
        const char *original = tac->lines[i];

        if (strncmp(original, "//", 2) == 0)
        {
            emit_asm(&buf, "    ;%s", original + 2);
            continue;
        }

        size_t length = strlen(original);

        if (length > 0 && original[length - 1] == ':')
        {
            emit_asm(&buf, "%s", original);
            continue;
        }

        char mutable_copy[256];
        strncpy(mutable_copy, original, sizeof(mutable_copy) - 1);
        mutable_copy[sizeof(mutable_copy) - 1] = '\0';

        char *tokens[MAX_TOKENS];
        int token_count = split_line(mutable_copy, tokens);

        if (token_count == 0)
            continue;

        if (strcmp(tokens[0], "print") == 0 && token_count == 2)
        {
            if (is_string_literal(tokens[1]))
                emit_asm(&buf, "    PRINT_STR %s", tokens[1]);
            else
            {
                emit_asm(&buf, "    MOV EAX, %s", translate_operand(tokens[1]));
                emit_asm(&buf, "    CALL PRINT_VALUE");
            }
        }
        else if (strcmp(tokens[0], "goto") == 0 && token_count == 2)
        {
            emit_asm(&buf, "    JMP %s", tokens[1]);
        }
        else if (strcmp(tokens[0], "ifFalse") == 0 && token_count == 4)
        {
            emit_asm(&buf, "    CMP %s, 0", translate_operand(tokens[1]));
            emit_asm(&buf, "    JE %s", tokens[3]);
        }
        else if (token_count == 5 && strcmp(tokens[1], "=") == 0)
        {
            emit_binary_op(&buf, tokens[0], translate_operand(tokens[2]), tokens[3], translate_operand(tokens[4]));
        }
        else if (token_count == 3 && strcmp(tokens[1], "=") == 0)
        {
            char first = tokens[2][0];

            if (first == '-' || first == '!')
            {
                emit_unary_op(&buf, tokens[0], first, translate_operand(tokens[2] + 1));
            }
            else
            {
                /*
                 * Route through EAX even for a plain copy: x86 has
                 * no memory-to-memory MOV, and the source here may
                 * be a variable (memory operand), not only a literal.
                 */
                emit_asm(&buf, "    MOV EAX, %s", translate_operand(tokens[2]));
                emit_asm(&buf, "    MOV [%s], EAX", tokens[0]);
            }
        }
        else
        {
            emit_asm(&buf, "    ; unrecognized TAC line, skipped: %s", original);
        }
    }

    emit_asm(&buf, "");
    emit_asm(&buf, "    MOV ESP, EBP");
    emit_asm(&buf, "    POP EBP");
    emit_asm(&buf, "    RET");

    return buf.text;
}