#!/usr/bin/env python3
"""
app.py -- Syntax Studio GUI.

Run from the project root (compiler must already be built with `make`):
    python3 gui/app.py
"""

import os
import re
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox

import compiler_runner as cr

MAX_UPLOAD_BYTES = 10 * 1024
ALLOWED_EXTENSIONS = (".src", ".c", ".txt")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPILER_PATH = os.path.join(PROJECT_ROOT, "compiler")

MONO = ("Consolas", 12)
MONO_SM = ("Consolas", 10)
UI = ("Segoe UI", 10)
PILL_FONT = ("Segoe UI", 9, "bold")

BG = "#f7f8fa"
WHITE = "#ffffff"
BORDER = "#e3e5e8"
ACCENT = "#2f6fed"
KEYWORD = "#6c5ce7"
COMMENT = "#6a9955"
NUMBER = "#b5760c"
CURLINE = "#eef4ff"
ERRLINE = "#ffe0e0"
GREEN, RED, GRAY = "#16a34a", "#dc2626", "#9aa0a6"

KEYWORDS = ("int", "float", "bool", "if", "else", "while", "print", "true", "false")
KEYWORD_RE = re.compile(r"\b(?:" + "|".join(KEYWORDS) + r")\b")
COMMENT_RE = re.compile(r"//[^\n]*")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
ERR_RE = re.compile(r"(Lexical|Semantic) Error at line (\d+): (.*)")
SYNTAX_RE = re.compile(r"Syntax Error at line (\d+)")

SAMPLE = """// Sample program -- edit this or load your own .src file.
int x;
int y;
bool flag;

x = 10;
y = 0;
flag = true;

while (x > 0 && flag) {
    y = y + x;
    x = x - 1;

    if (x == 3) {
        flag = false;
    }
}

print y;
"""


def round_rect(c, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


def shade(hexcolor, factor):
    h = hexcolor.lstrip("#")
    r, g, b = (min(255, max(0, int(int(h[i:i + 2], 16) * factor))) for i in (0, 2, 4))
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def measure(font, text):
    """Text width/line-height via Tk's own font system -- reliable across
    platforms and display-scaling settings, unlike measuring an unmapped
    Canvas item's bbox()."""
    f = tkfont.Font(font=font)
    return f.measure(text), f.metrics("linespace")


class RoundedButton(tk.Canvas):
    """Flat rounded-corner button (ttk can't do true rounded corners)."""

    def __init__(self, parent, text, command=None, *, radius=8, bg=None, fg="white",
                 border_color=None, border_width=0, font=UI, padx=14, pady=7):
        bg = bg or ACCENT
        super().__init__(parent, highlightthickness=0, bd=0, bg=BG)
        self.command, self.radius = command, radius
        self.colors = {"n": bg, "h": shade(bg, 1.08), "p": shade(bg, 0.85)}
        tw, th = measure(font, text)
        w, h = tw + padx * 2, th + pady * 2
        self.configure(width=w, height=h)
        self.shape = round_rect(self, 1, 1, w - 1, h - 1, radius, fill=bg,
                                 outline=border_color or "", width=border_width)
        self.create_text(w / 2, h / 2, text=text, fill=fg, font=font)
        self.bind("<Enter>", lambda e: (self.itemconfig(self.shape, fill=self.colors["h"]),
                                         self.configure(cursor="hand2")))
        self.bind("<Leave>", lambda e: self.itemconfig(self.shape, fill=self.colors["n"]))
        self.bind("<ButtonPress-1>", lambda e: self.itemconfig(self.shape, fill=self.colors["p"]))
        self.bind("<ButtonRelease-1>", self._release)

    def _release(self, event):
        self.itemconfig(self.shape, fill=self.colors["h"])
        if 0 <= event.x <= int(self["width"]) and 0 <= event.y <= int(self["height"]) and self.command:
            self.command()


def make_pill(parent, text, status):
    bg, fg = {"ok": ("#e8f9ee", GREEN), "fail": ("#fdecea", RED), "skip": ("#f1f2f4", GRAY)}[status]
    icon = {"ok": "\u2713", "fail": "\u2715", "skip": "\u2013"}[status]
    label = f"{text}  {icon}"
    tw, th = measure(PILL_FONT, label)
    w, h = tw + 22, th + 12
    c = tk.Canvas(parent, highlightthickness=0, bd=0, bg=BG, width=w, height=h)
    round_rect(c, 1, 1, w - 1, h - 1, h / 2, fill=bg, outline="")
    c.create_text(w / 2, h / 2, text=label, fill=fg, font=PILL_FONT)
    return c


def make_connector(parent, w=22):
    c = tk.Canvas(parent, width=w, height=18, highlightthickness=0, bd=0, bg=BG)
    c.create_line(0, 9, w, 9, fill="#c7cad1", dash=(3, 2))
    return c


class SyntaxStudioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Syntax Studio")
        self.geometry("1300x860")
        self.minsize(1100, 700)
        self.configure(bg=BG)

        self.current_path = None
        self.is_dirty = False

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(14, 6), font=UI)
        style.configure("Treeview", rowheight=22, font=MONO_SM, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=(UI[0], 9, "bold"))
        style.configure("TPanedwindow", background=BG)
        style.configure("TFrame", background=BG)

        self._build_menu()
        self._build_toolbar()
        self.update_idletasks()
        self._build_pipeline()
        self.update_idletasks()
        self._build_body()
        self._build_statusbar()
        self._bind_shortcuts()

        self.editor.insert("1.0", SAMPLE)
        self._on_editor_change()

    # ---------------- menu / toolbar / pipeline ----------------
    def _build_menu(self):
        m = tk.Menu(self)
        f = tk.Menu(m, tearoff=0)
        f.add_command(label="Open...", accelerator="Ctrl+O", command=self.load_file)
        f.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        f.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_file_as)
        f.add_separator()
        f.add_command(label="Exit", command=self.destroy)
        m.add_cascade(label="File", menu=f)

        e = tk.Menu(m, tearoff=0)
        e.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: self._safe(self.editor.edit_undo))
        e.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: self._safe(self.editor.edit_redo))
        e.add_command(label="Select All", accelerator="Ctrl+A", command=self._select_all)
        m.add_cascade(label="Edit", menu=e)

        r = tk.Menu(m, tearoff=0)
        r.add_command(label="Run Compiler", accelerator="Ctrl+Enter", command=self.run_compiler)
        m.add_cascade(label="Run", menu=r)

        h = tk.Menu(m, tearoff=0)
        h.add_command(label="About", command=lambda: messagebox.showinfo(
            "About", "Syntax Studio -- GUI front-end for the Flex/Bison mini compiler."))
        m.add_cascade(label="Help", menu=h)
        self.config(menu=m)

    @staticmethod
    def _safe(fn):
        try:
            fn()
        except tk.TclError:
            pass

    def _select_all(self, *_a):
        self.editor.tag_add("sel", "1.0", "end-1c")
        return "break"

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        bar.pack(fill=tk.X)
        inner = tk.Frame(bar, bg=WHITE)
        inner.pack(fill=tk.X, padx=10, pady=8)

        sec = dict(bg=WHITE, fg="#333333", border_color="#d5d8dd", border_width=1, radius=8)
        pri = dict(bg=ACCENT, fg="white", radius=8, font=(UI[0], 10, "bold"))

        RoundedButton(inner, "\U0001F4C1 Load File", command=self.load_file, **sec).pack(side=tk.LEFT, padx=(0, 6))
        RoundedButton(inner, "\U0001F4BE Save", command=self.save_file, **sec).pack(side=tk.LEFT, padx=(0, 6))
        RoundedButton(inner, "\u25B6 Run Compiler  (Ctrl+Enter)", command=self.run_compiler, **pri).pack(
            side=tk.LEFT, padx=(0, 6))
        RoundedButton(inner, "\U0001F9F9 Clear", command=self.clear_all, **sec).pack(side=tk.LEFT, padx=(0, 14))

        info = tk.Frame(inner, bg=WHITE)
        info.pack(side=tk.LEFT)
        self.file_title = tk.Label(info, font=(UI[0], 10, "bold"), bg=WHITE, anchor="w")
        self.file_title.pack(anchor="w")
        self.file_sub = tk.Label(info, font=(UI[0], 8), fg="#8a8f98", bg=WHITE, anchor="w")
        self.file_sub.pack(anchor="w")

        ready = os.path.isfile(COMPILER_PATH)
        tk.Label(inner, text=("\u25CF  Compiler Ready" if ready else "\u25CF  Compiler Not Built (run make)"),
                 fg=(GREEN if ready else RED), bg=WHITE, font=(UI[0], 9)).pack(side=tk.RIGHT)
        self._update_file_label()

    def _build_pipeline(self):
        self.pipeline_row = tk.Frame(self, bg=BG)
        self.pipeline_row.pack(fill=tk.X, padx=14, pady=(12, 12))
        self._refresh_pipeline(["skip"] * 5)

    def _refresh_pipeline(self, statuses):
        for w in self.pipeline_row.winfo_children():
            w.destroy()
        names = ["Lexer", "Parser", "AST", "Semantic", "TAC"]
        for i, (name, status) in enumerate(zip(names, statuses)):
            make_pill(self.pipeline_row, name, status).pack(side=tk.LEFT)
            if i < len(names) - 1:
                make_connector(self.pipeline_row).pack(side=tk.LEFT)

    # ---------------- body: editor + output ----------------
    def _build_body(self):
        body = tk.Frame(self, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        left = tk.Frame(body, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        tk.Label(left, text="Source Code", font=(UI[0], 10, "bold"), bg=BG).pack(anchor="w", pady=(0, 4))
        ec = tk.Frame(left, bg=BORDER)
        ec.pack(fill=tk.BOTH, expand=True)

        self.linenumbers = tk.Text(ec, width=4, padx=6, wrap="none", font=MONO, bg="#eef0f2",
                                    fg="#8a8f98", bd=0, state="disabled", takefocus=0, cursor="arrow")
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)
        for seq, amt in (("<MouseWheel>", None), ("<Button-4>", -1), ("<Button-5>", 1)):
            if amt is None:
                self.linenumbers.bind(seq, lambda e: self.editor.yview_scroll(int(-e.delta / 120), "units"))
            else:
                self.linenumbers.bind(seq, lambda e, a=amt: self.editor.yview_scroll(a, "units"))

        self.editor = tk.Text(ec, wrap="none", font=MONO, undo=True, bg=WHITE, bd=0, padx=6,
                               insertbackground="black")
        yscroll = ttk.Scrollbar(ec, orient="vertical", command=self.editor.yview)
        xscroll = ttk.Scrollbar(left, orient="horizontal", command=self.editor.xview)
        self.editor.configure(yscrollcommand=self._on_editor_yview, xscrollcommand=xscroll.set)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.editor_yscroll = yscroll

        for tag, kw in (("kw", dict(foreground=KEYWORD)), ("comment", dict(foreground=COMMENT)),
                        ("number", dict(foreground=NUMBER)), ("curline", dict(background=CURLINE)),
                        ("error_line", dict(background=ERRLINE))):
            self.editor.tag_configure(tag, **kw)
        self.editor.tag_lower("curline")
        self.editor.tag_raise("error_line")

        for ev in ("<KeyRelease>", "<ButtonRelease-1>"):
            self.editor.bind(ev, self._on_editor_change)

        right = tk.Frame(body, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        head = tk.Frame(right, bg=BG)
        head.pack(fill=tk.X, pady=(0, 4))
        tk.Label(head, text="Compiler Output", font=(UI[0], 10, "bold"), bg=BG).pack(side=tk.LEFT)
        tk.Label(head, text="   Click an error to jump to the source.", font=(UI[0], 8),
                 fg="#8a8f98", bg=BG).pack(side=tk.LEFT)

        errors_panel = tk.Frame(right, bg=BG, height=210)
        errors_panel.pack(side=tk.BOTTOM, fill=tk.X, pady=(6, 0))
        errors_panel.pack_propagate(False)
        self._build_errors_table(errors_panel)

        self.notebook = ttk.Notebook(right)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._build_ast_tab()
        self.semantic_view = self._make_text_tab("Semantic")
        self.tac_view = self._make_text_tab("TAC")
        self.console_view = self._make_text_tab("Console")

    def _build_ast_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="AST")
        self.ast_tree = ttk.Treeview(frame, show="tree")
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=self.ast_tree.yview)
        self.ast_tree.configure(yscrollcommand=yscroll.set)
        self.ast_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _make_text_tab(self, title):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        text = tk.Text(frame, wrap="none", font=MONO_SM, state="disabled", bg=WHITE, bd=0, padx=6)
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=yscroll.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.tag_configure("error", foreground=RED)
        text.tag_configure("ok", foreground=GREEN)
        return text

    def _build_errors_table(self, parent):
        head = tk.Frame(parent, bg=BG)
        head.pack(fill=tk.X, pady=(4, 2))
        tk.Label(head, text="Errors / Raw", font=(UI[0], 10, "bold"), bg=BG).pack(side=tk.LEFT)
        self.error_badge = tk.Label(head, text="", bg=RED, fg="white", font=(UI[0], 8, "bold"), padx=6)
        self.error_badge.pack(side=tk.LEFT, padx=6)

        cols = ("line", "type", "message")
        self.errors_tree = ttk.Treeview(parent, columns=cols, show="headings", height=6)
        for c, w, anchor in (("line", 50, "center"), ("type", 80, "w"), ("message", 480, "w")):
            self.errors_tree.heading(c, text=c.capitalize())
            self.errors_tree.column(c, width=w, anchor=anchor)
        yscroll = ttk.Scrollbar(parent, orient="vertical", command=self.errors_tree.yview)
        self.errors_tree.configure(yscrollcommand=yscroll.set)
        self.errors_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.errors_tree.bind("<<TreeviewSelect>>", self._on_error_select)

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Ready.")
        self.status_label = tk.Label(self, textvariable=self.status_var, anchor="w", padx=8, pady=4, bg=BG)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def _bind_shortcuts(self):
        self.bind("<Control-o>", lambda e: self.load_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-Shift-S>", lambda e: self.save_file_as())
        self.bind("<Control-Return>", lambda e: self.run_compiler())
        self.bind("<Control-a>", self._select_all)

    # ---------------- editor helpers ----------------
    def _on_editor_change(self, event=None):
        self.is_dirty = True
        self._update_file_label()
        self._update_line_numbers()
        self._highlight_syntax()
        self._highlight_current_line()

    def _update_line_numbers(self):
        n = int(self.editor.index("end-1c").split(".")[0])
        self.linenumbers.configure(state="normal")
        self.linenumbers.delete("1.0", tk.END)
        self.linenumbers.insert("1.0", "\n".join(str(i) for i in range(1, n + 1)))
        self.linenumbers.configure(state="disabled")
        self.linenumbers.yview_moveto(self.editor.yview()[0])

    def _highlight_syntax(self):
        content = self.editor.get("1.0", "end-1c")
        for tag in ("kw", "number", "comment"):
            self.editor.tag_remove(tag, "1.0", tk.END)
        for pat, tag in ((KEYWORD_RE, "kw"), (NUMBER_RE, "number"), (COMMENT_RE, "comment")):
            for m in pat.finditer(content):
                self.editor.tag_add(tag, f"1.0+{m.start()}c", f"1.0+{m.end()}c")

    def _highlight_current_line(self):
        self.editor.tag_remove("curline", "1.0", tk.END)
        cur = self.editor.index("insert")
        self.editor.tag_add("curline", f"{cur} linestart", f"{cur} lineend+1c")

    def _on_editor_yview(self, first, last):
        self.editor_yscroll.set(first, last)
        self.linenumbers.yview_moveto(first)

    def _jump_to_editor_line(self, line_num):
        last_line = int(self.editor.index("end-1c").split(".")[0])
        line_num = max(1, min(line_num, last_line))
        self.editor.tag_remove("error_line", "1.0", tk.END)
        self.editor.tag_add("error_line", f"{line_num}.0", f"{line_num}.end+1c")
        self.editor.see(f"{line_num}.0")
        self.editor.mark_set("insert", f"{line_num}.0")
        self.editor.focus_set()

    def _on_error_select(self, _event=None):
        sel = self.errors_tree.selection()
        if not sel:
            return
        line = self.errors_tree.item(sel[0], "values")[0]
        if str(line).isdigit():
            self._jump_to_editor_line(int(line))

    def _update_file_label(self):
        name = os.path.basename(self.current_path) if self.current_path else "untitled.src"
        self.file_title.configure(text=name + (" *" if self.is_dirty else ""))
        self.file_sub.configure(text=self.current_path or "(unsaved)")

    # ---------------- file actions ----------------
    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Supported files", "*.src *.c *.txt"), ("All files", "*.*")])
        if not path:
            return
        if os.path.splitext(path)[1].lower() not in ALLOWED_EXTENSIONS:
            messagebox.showerror("Unsupported file type", "Please choose a .src, .c, or .txt file.")
            return
        if os.path.getsize(path) > MAX_UPLOAD_BYTES:
            messagebox.showerror("File too large", "Please choose a file under 10 KB.")
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as exc:
            messagebox.showerror("Could not read file", str(exc))
            return
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        self.current_path = path
        self.is_dirty = False
        self._on_editor_change()
        self.is_dirty = False
        self._update_file_label()
        self.status_var.set(f"Loaded '{path}'.")

    def save_file(self):
        self._write_to_path(self.current_path) if self.current_path else self.save_file_as()

    def save_file_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".src",
                                             filetypes=[("Source files", "*.src"), ("All files", "*.*")])
        if path:
            self._write_to_path(path)

    def _write_to_path(self, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", "end-1c"))
        except OSError as exc:
            messagebox.showerror("Could not save file", str(exc))
            return
        self.current_path = path
        self.is_dirty = False
        self._update_file_label()
        self.status_var.set(f"Saved '{path}'.")

    def clear_all(self):
        self.editor.delete("1.0", tk.END)
        self.current_path = None
        self._on_editor_change()
        self.is_dirty = False
        self._update_file_label()
        self._refresh_pipeline(["skip"] * 5)
        self.errors_tree.delete(*self.errors_tree.get_children())
        self.error_badge.configure(text="")
        for v in (self.semantic_view, self.tac_view, self.console_view):
            self._set_text(v, "")
        self.ast_tree.delete(*self.ast_tree.get_children())
        self.status_var.set("Ready.")

    # ---------------- compiler ----------------
    def run_compiler(self):
        source = self.editor.get("1.0", "end-1c")
        if not source.strip():
            messagebox.showwarning("Nothing to run", "The editor is empty.")
            return
        self.editor.tag_remove("error_line", "1.0", tk.END)
        self.status_var.set("Running compiler...")
        self.update_idletasks()

        result = cr.run_source(source, compiler_path=COMPILER_PATH)
        if "error" in result:
            messagebox.showerror("Compiler error", result["error"])
            self.status_var.set("Failed to run compiler.")
            return
        self._display_result(result)

    def _pipeline_status(self, result):
        if not result["parsed"]:
            lexer_ok = "Lexical Error" not in result["raw_stderr"]
            return ["ok", "fail", "skip", "skip", "skip"] if lexer_ok else ["fail", "skip", "skip", "skip", "skip"]
        sem_ok = not result["semantic_errors"]
        tac_ok = sem_ok and bool(result["tac"].strip())
        return ["ok", "ok", "ok", "ok" if sem_ok else "fail", "ok" if tac_ok else "skip"]

    def _parse_errors(self, stderr_text):
        rows, lines, i = [], stderr_text.splitlines(), 0
        while i < len(lines):
            m = ERR_RE.match(lines[i])
            if m:
                rows.append((m.group(2), m.group(1), m.group(3)))
            else:
                m2 = SYNTAX_RE.match(lines[i])
                if m2:
                    msg = lines[i + 1].strip() if i + 1 < len(lines) else ""
                    rows.append((m2.group(1), "Syntax", msg))
                    i += 1
            i += 1
        return rows

    def _populate_ast(self, ast_text):
        self.ast_tree.delete(*self.ast_tree.get_children())
        stack = {-1: ""}
        for line in ast_text.splitlines():
            if not line.strip():
                continue
            depth = (len(line) - len(line.lstrip(" "))) // 4
            node = self.ast_tree.insert(stack.get(depth - 1, ""), "end", text=line.strip(), open=True)
            stack[depth] = node

    def _display_result(self, result):
        self._refresh_pipeline(self._pipeline_status(result))
        self._populate_ast(result["ast"])

        summary = [result["semantic_summary"]] if result["semantic_summary"] else []
        if result["semantic_errors"]:
            summary += [""] + result["semantic_errors"]
        ok = bool(result["semantic_summary"]) and not result["semantic_errors"]
        self._set_text(self.semantic_view, "\n".join(summary) or "(not reached)", "ok" if ok else "error")

        self._set_text(self.tac_view, result["tac"] or "(not generated -- see Semantic tab)")
        self._set_text(self.console_view, "--- stdout ---\n{}\n\n--- stderr ---\n{}".format(
            result["raw_stdout"].strip(), result["raw_stderr"].strip() or "(empty)"))

        rows = self._parse_errors(result["raw_stderr"])
        self.errors_tree.delete(*self.errors_tree.get_children())
        for row in rows:
            self.errors_tree.insert("", "end", values=row)
        self.error_badge.configure(text=str(len(rows)) if rows else "")

        if not result["parsed"]:
            self.status_var.set("Parsing failed -- see Errors / Raw.")
        elif result["semantic_errors"]:
            self.status_var.set(f"{len(result['semantic_errors'])} semantic error(s) found.")
        else:
            self.status_var.set("Success: parsed, type-checked, and generated TAC.")

    @staticmethod
    def _set_text(widget, content, tag=None):
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", content)
        if tag:
            widget.tag_add(tag, "1.0", tk.END)
        widget.configure(state="disabled")


if __name__ == "__main__":
    if not os.path.isfile(COMPILER_PATH):
        print("Warning: compiler binary not found at '{}'. Run 'make' first.".format(COMPILER_PATH))
    SyntaxStudioApp().mainloop()