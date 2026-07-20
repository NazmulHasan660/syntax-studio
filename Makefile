CC = gcc
LEX = flex
YACC = bison

CFLAGS = -Wall -I./src/ast

TARGET = compiler

LEX_SRC = src/lexer/lexer.l
YACC_SRC = src/parser/parser.y

LEX_OUT = lex.yy.c
YACC_OUT_C = parser.tab.c
YACC_OUT_H = parser.tab.h

all: $(TARGET)

$(TARGET): $(YACC_OUT_C) $(LEX_OUT) src/main.c
	$(CC) $(CFLAGS) -o $(TARGET) $(YACC_OUT_C) $(LEX_OUT) src/main.c

$(YACC_OUT_C) $(YACC_OUT_H): $(YACC_SRC)
	$(YACC) -d $(YACC_SRC)

$(LEX_OUT): $(LEX_SRC) $(YACC_OUT_H)
	$(LEX) $(LEX_SRC)

clean:
	rm -f $(TARGET) $(LEX_OUT) $(YACC_OUT_C) $(YACC_OUT_H)