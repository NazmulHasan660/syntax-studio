#!/usr/bin/env python3
"""
app.py

Tkinter GUI for Syntax Studio. Lets you load or type a .src program,
run it through the compiled C binary, and see the AST, Semantic
Analysis result, and generated Three Address Code in separate tabs.

Run from the project root:
    python3 gui/app.py

Requires the compiler binary to already be built:
    make
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import compiler_runner as cr

MAX_UPLOAD_BYTES = 10 * 1024  # 10 KB cap on loaded files
ALLOWED_EXTENSIONS = (".src", ".c", ".txt")

# gui/app.py -> project root is one level up
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPILER_PATH = os.path.join(PROJECT_ROOT, "compiler")

MONO_FONT = ("Consolas", 11)
MONO_FONT_SMALL = ("Consolas", 10)


class SyntaxStudioApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Syntax Studio")
        self.geometry("1100x700")

        self._build_toolbar()
        self._build_body()
        self._build_statusbar()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_toolbar(self):
        toolbar = ttk.Frame(self, padding=6)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(toolbar, text="Load File", command=self.load_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="Run Compiler", command=self.run_compiler).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=4)

        self.file_label = ttk.Label(toolbar, text="No file loaded (using editor text)")
        self.file_label.pack(side=tk.LEFT, padx=16)

    def _build_body(self):
        body = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=6)

        # --- Left: source editor ---
        editor_frame = ttk.Frame(body)
        ttk.Label(editor_frame, text="Source (.src)").pack(anchor="w")

        editor_container = ttk.Frame(editor_frame)
        editor_container.pack(fill=tk.BOTH, expand=True)

        self.editor = tk.Text(editor_container, wrap="none", font=MONO_FONT, undo=True)
        editor_yscroll = ttk.Scrollbar(editor_container, orient="vertical", command=self.editor.yview)
        self.editor.configure(yscrollcommand=editor_yscroll.set)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        editor_yscroll.pack(side=tk.RIGHT, fill=tk.Y)

        body.add(editor_frame, weight=1)

        # --- Right: output tabs ---
        output_frame = ttk.Frame(body)
        ttk.Label(output_frame, text="Compiler Output").pack(anchor="w")

        self.notebook = ttk.Notebook(output_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.ast_view = self._make_output_tab("AST")
        self.semantic_view = self._make_output_tab("Semantic Analysis")
        self.tac_view = self._make_output_tab("Three Address Code")
        self.errors_view = self._make_output_tab("Errors / Raw")

        body.add(output_frame, weight=1)

    def _make_output_tab(self, title):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)

        container = ttk.Frame(frame)
        container.pack(fill=tk.BOTH, expand=True)

        text = tk.Text(container, wrap="none", font=MONO_FONT_SMALL, state="disabled")
        yscroll = ttk.Scrollbar(container, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=yscroll.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)

        text.tag_configure("error", foreground="#c0392b")
        text.tag_configure("ok", foreground="#1e8449")

        return text

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Ready.")
        status = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding=4)
        status.pack(side=tk.BOTTOM, fill=tk.X)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def load_file(self):
        path = filedialog.askopenfilename(
            title="Load source file",
            filetypes=[
                ("Supported files", "*.src *.c *.txt"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        ext = os.path.splitext(path)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            messagebox.showerror(
                "Unsupported file type",
                "Please choose a .src, .c, or .txt file.",
            )
            return

        size = os.path.getsize(path)
        if size > MAX_UPLOAD_BYTES:
            messagebox.showerror(
                "File too large",
                "'{}' is {} KB. Please choose a file under {} KB.".format(
                    os.path.basename(path), size // 1024, MAX_UPLOAD_BYTES // 1024
                ),
            )
            return

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as exc:
            messagebox.showerror("Could not read file", str(exc))
            return

        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        self.file_label.config(text=os.path.basename(path))
        self.status_var.set("Loaded '{}'.".format(path))

    def clear_all(self):
        self.editor.delete("1.0", tk.END)
        self.file_label.config(text="No file loaded (using editor text)")
        for view in (self.ast_view, self.semantic_view, self.tac_view, self.errors_view):
            self._set_text(view, "")
        self.status_var.set("Ready.")

    def run_compiler(self):
        source = self.editor.get("1.0", tk.END)

        if not source.strip():
            messagebox.showwarning("Nothing to run", "The editor is empty.")
            return

        self.status_var.set("Running compiler...")
        self.update_idletasks()

        result = cr.run_source(source, compiler_path=COMPILER_PATH)

        if "error" in result:
            self._set_text(self.errors_view, result["error"], tag="error")
            self.notebook.select(self.errors_view.master.master)
            self.status_var.set("Failed to run compiler.")
            return

        self._display_result(result)

    def _display_result(self, result):
        # AST tab
        self._set_text(self.ast_view, result["ast"] or "(no AST -- parsing failed)")

        # Semantic tab: summary line plus each individual error
        semantic_lines = []
        if result["semantic_summary"]:
            semantic_lines.append(result["semantic_summary"])
        if result["semantic_errors"]:
            semantic_lines.append("")
            semantic_lines.extend(result["semantic_errors"])
        semantic_text = "\n".join(semantic_lines) if semantic_lines else "(not reached -- parsing failed)"

        is_ok = bool(result["semantic_summary"]) and not result["semantic_errors"]
        self._set_text(self.semantic_view, semantic_text, tag=("ok" if is_ok else "error"))

        # TAC tab
        self._set_text(self.tac_view, result["tac"] or "(not generated -- see Semantic Analysis tab)")

        # Errors / Raw tab: parser/lexer errors (if parsing failed) or full raw output
        if not result["parsed"]:
            raw = result["raw_stderr"].strip() or "Parsing failed (no diagnostic message captured)."
            self._set_text(self.errors_view, raw, tag="error")
        else:
            raw = "--- stdout ---\n{}\n\n--- stderr ---\n{}".format(
                result["raw_stdout"].strip(), result["raw_stderr"].strip() or "(empty)"
            )
            self._set_text(self.errors_view, raw)

        # Jump to the most relevant tab and update the status bar.
        if not result["parsed"]:
            self.notebook.select(3)  # Errors tab
            self.status_var.set("Parsing failed. See 'Errors / Raw' tab.")
        elif result["semantic_errors"]:
            self.notebook.select(1)  # Semantic tab
            self.status_var.set("Parsed OK, {} semantic error(s) found.".format(
                len(result["semantic_errors"])))
        else:
            self.notebook.select(2)  # TAC tab
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
        print("Warning: compiler binary not found at '{}'.".format(COMPILER_PATH))
        print("Run 'make' in the project root first.")

    app = SyntaxStudioApp()
    app.mainloop()
    app.mainloop()