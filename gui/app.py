#!/usr/bin/env python3
"""
app.py -- Syntax Studio GUI.

Run from the project root:
    python3 gui/app.py
"""
import os
import re
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox
import compiler_runner as cr
MAX_UPLOAD_BYTES = 10 * 1024
ALLOWED_EXTENSIONS = ('.src', '.c', '.cpp', '.cc', '.cxx', '.java', '.txt')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPILER_PATH = os.path.join(PROJECT_ROOT, 'compiler')
MONO = ('Consolas', 12)
MONO_SM = ('Consolas', 10)
UI = ('Segoe UI', 10)
PILL_FONT = ('Segoe UI', 9, 'bold')
BG = '#f7f8fa'
WHITE = '#ffffff'
BORDER = '#e3e5e8'
ACCENT = '#2f6fed'
KEYWORD = '#6c5ce7'
COMMENT = '#6a9955'
NUMBER = '#b5760c'
CURLINE = '#eef4ff'
ERRLINE = '#ffe0e0'
GREEN = '#16a34a'
RED = '#dc2626'
GRAY = '#9aa0a6'
KEYWORDS = ('int', 'float', 'double', 'bool', 'boolean', 'public', 'private', 'protected', 'static', 'if', 'else', 'while', 'for', 'do', 'return', 'print', 'cout', 'true', 'false')
KEYWORD_RE = re.compile('\\b(?:' + '|'.join(KEYWORDS) + ')\\b')
COMMENT_RE = re.compile('//[^\\n]*')
NUMBER_RE = re.compile('\\b\\d+(?:\\.\\d+)?\\b')
ERR_RE = re.compile('(Lexical|Syntax|Semantic) Error at line (\\d+):?\\s*(.*)')
SAMPLES = {'C': '#include <stdio.h>\n\nint x = 10;\nint y = 20;\nint total = x + y;\n\nprintf(total);\n', 'C++': '#include <iostream>\nusing namespace std;\n\nint score = 75;\nbool passed = score >= 50;\n\nif (passed) {\n    cout << score;\n}\n', 'Java': 'int x = 10;\nint y = 20;\nint total = x + y;\n\nSystem.out.println(total);\n'}

def round_rect(canvas, x1, y1, x2, y2, radius, **options):
    points = [x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius, x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2, x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1]
    return canvas.create_polygon(points, smooth=True, **options)

def shade(hex_color, factor):
    color = hex_color.lstrip('#')
    red, green, blue = (min(255, max(0, int(int(color[index:index + 2], 16) * factor))) for index in (0, 2, 4))
    return '#{:02x}{:02x}{:02x}'.format(red, green, blue)

def measure(font, text):
    tkinter_font = tkfont.Font(font=font)
    return (tkinter_font.measure(text), tkinter_font.metrics('linespace'))

def draw_icon(canvas, icon_type, x, y, color):
    line_options = {'fill': color, 'width': 2.2, 'capstyle': tk.ROUND, 'joinstyle': tk.ROUND}
    if icon_type == 'folder':
        canvas.create_line(x - 9, y - 7, x - 3, y - 7, x, y - 4, x + 9, y - 4, x + 9, y + 8, x - 9, y + 8, x - 9, y - 7, **line_options)
    elif icon_type == 'save':
        canvas.create_rectangle(x - 8, y - 9, x + 8, y + 9, outline=color, width=2.2)
        canvas.create_rectangle(x - 4, y - 9, x + 4, y - 3, outline=color, width=1.8)
        canvas.create_rectangle(x - 5, y + 2, x + 5, y + 9, outline=color, width=1.8)
    elif icon_type == 'eraser':
        canvas.create_polygon(x - 9, y + 2, x + 2, y - 9, x + 4, y - 9, x + 9, y - 4, x + 9, y - 2, x - 2, y + 9, x - 5, y + 9, x - 9, y + 5, fill='', outline=color, width=2, joinstyle=tk.ROUND)
        canvas.create_line(x - 6, y - 1, x + 1, y + 6, fill=color, width=2, capstyle=tk.ROUND)
        canvas.create_line(x - 3, y + 9, x + 10, y + 9, fill=color, width=2, capstyle=tk.ROUND)

def make_pill(parent, text, status):
    colors = {'ok': ('#e8f9ee', GREEN), 'fail': ('#fdecea', RED), 'skip': ('#f1f2f4', GRAY)}
    icons = {'ok': '✓', 'fail': '✕', 'skip': '–'}
    background, foreground = colors[status]
    label = '{}  {}'.format(text, icons[status])
    text_width, text_height = measure(PILL_FONT, label)
    width, height = (text_width + 22, text_height + 12)
    canvas = tk.Canvas(parent, highlightthickness=0, bd=0, bg=BG, width=width, height=height)
    round_rect(canvas, 1, 1, width - 1, height - 1, height / 2, fill=background, outline='')
    canvas.create_text(width / 2, height / 2, text=label, fill=foreground, font=PILL_FONT)
    return canvas

def make_connector(parent):
    canvas = tk.Canvas(parent, width=22, height=18, highlightthickness=0, bd=0, bg=BG)
    canvas.create_line(0, 9, 22, 9, fill='#c7cad1', dash=(3, 2))
    return canvas

class RoundedButton(tk.Canvas):

    def __init__(self, parent, text, command=None, *, radius=8, bg=None, fg='white', border_color=None, border_width=0, font=UI, padx=14, pady=7, icon=None):
        background = bg or ACCENT
        super().__init__(parent, highlightthickness=0, bd=0, bg=BG)
        self.command = command
        self.radius = radius
        self.colors = {'normal': background, 'hover': shade(background, 1.08), 'pressed': shade(background, 0.85)}
        text_width, text_height = measure(font, text)
        extra_width = 30 if icon else 0
        width = text_width + padx * 2 + extra_width
        height = text_height + pady * 2
        self.configure(width=width, height=height)
        self.shape = round_rect(self, 1, 1, width - 1, height - 1, radius, fill=background, outline=border_color or '', width=border_width)
        if icon:
            start = (width - text_width - extra_width) / 2
            draw_icon(self, icon, start + 10, height / 2, fg)
            self.create_text(start + extra_width, height / 2, text=text, fill=fg, font=font, anchor='w')
        else:
            self.create_text(width / 2, height / 2, text=text, fill=fg, font=font)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _on_enter(self, _event):
        self.itemconfig(self.shape, fill=self.colors['hover'])
        self.configure(cursor='hand2')

    def _on_leave(self, _event):
        self.itemconfig(self.shape, fill=self.colors['normal'])

    def _on_press(self, _event):
        self.itemconfig(self.shape, fill=self.colors['pressed'])

    def _on_release(self, event):
        self.itemconfig(self.shape, fill=self.colors['hover'])
        inside_button = 0 <= event.x <= int(self['width']) and 0 <= event.y <= int(self['height'])
        if inside_button and self.command:
            self.command()

class SyntaxStudioApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Syntax Studio')
        self.geometry('1300x860')
        self.minsize(1100, 700)
        self.configure(bg=BG)
        self.current_path = None
        self.is_dirty = False
        self.language_var = tk.StringVar(value='C++')
        self._configure_styles()
        self._build_menu()
        self._build_toolbar()
        self._build_pipeline()
        self._build_body()
        self._refresh_pipeline(['skip'] * 6)
        self._build_statusbar()
        self._bind_shortcuts()
        self.editor.insert('1.0', SAMPLES[self.language_var.get()])
        self._on_editor_change()

    def _configure_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure('TNotebook', background=BG, borderwidth=0)
        style.configure('TNotebook.Tab', padding=(8, 6), font=(UI[0], 9))
        style.configure('Treeview', rowheight=22, font=MONO_SM, fieldbackground=WHITE)
        style.configure('Treeview.Heading', font=(UI[0], 9, 'bold'))
        style.configure('TPanedwindow', background=BG)
        style.configure('TFrame', background=BG)

    def _build_menu(self):
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='Open...', accelerator='Ctrl+O', command=self.load_file)
        file_menu.add_command(label='Save', accelerator='Ctrl+S', command=self.save_file)
        file_menu.add_command(label='Save As...', accelerator='Ctrl+Shift+S', command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.destroy)
        menu_bar.add_cascade(label='File', menu=file_menu)
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label='Undo', accelerator='Ctrl+Z', command=lambda: self._safe(self.editor.edit_undo))
        edit_menu.add_command(label='Redo', accelerator='Ctrl+Y', command=lambda: self._safe(self.editor.edit_redo))
        edit_menu.add_command(label='Select All', accelerator='Ctrl+A', command=self._select_all)
        menu_bar.add_cascade(label='Edit', menu=edit_menu)
        run_menu = tk.Menu(menu_bar, tearoff=0)
        run_menu.add_command(label='Run Compiler', accelerator='Ctrl+Enter', command=self.run_compiler)
        menu_bar.add_cascade(label='Run', menu=run_menu)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label='About', command=lambda: messagebox.showinfo('About', 'Syntax Studio\nC, C++ and Java educational compiler front-end using Flex and Bison.'))
        menu_bar.add_cascade(label='Help', menu=help_menu)
        self.config(menu=menu_bar)

    @staticmethod
    def _safe(function):
        try:
            function()
        except tk.TclError:
            pass

    def _select_all(self, *_arguments):
        self.editor.tag_add('sel', '1.0', 'end-1c')
        return 'break'

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        toolbar.pack(fill=tk.X)
        inner = tk.Frame(toolbar, bg=WHITE)
        inner.pack(fill=tk.X, padx=10, pady=8)
        secondary_button = {'bg': WHITE, 'fg': '#202124', 'border_color': '#d5d8dd', 'border_width': 1, 'radius': 8, 'padx': 14, 'pady': 10}
        primary_button = {'bg': ACCENT, 'fg': 'white', 'radius': 8, 'font': (UI[0], 10, 'bold'), 'pady': 10}
        RoundedButton(inner, 'Load File', icon='folder', command=self.load_file, **secondary_button).pack(side=tk.LEFT, padx=(0, 6))
        RoundedButton(inner, 'Save', icon='save', command=self.save_file, **secondary_button).pack(side=tk.LEFT, padx=(0, 6))
        RoundedButton(inner, '▶ Run Compiler  (Ctrl+Enter)', command=self.run_compiler, **primary_button).pack(side=tk.LEFT, padx=(0, 6))
        RoundedButton(inner, 'Clear', icon='eraser', command=self.clear_all, **secondary_button).pack(side=tk.LEFT, padx=(0, 14))
        tk.Label(inner, text='Language:', bg=WHITE, fg='#202124', font=UI).pack(side=tk.LEFT, padx=(0, 5))
        language_box = ttk.Combobox(inner, textvariable=self.language_var, values=('C', 'C++', 'Java'), state='readonly', width=7, font=UI)
        language_box.pack(side=tk.LEFT, padx=(0, 14))
        language_box.bind('<<ComboboxSelected>>', self._on_language_change)
        file_information = tk.Frame(inner, bg=WHITE)
        file_information.pack(side=tk.LEFT)
        self.file_title = tk.Label(file_information, font=(UI[0], 10, 'bold'), bg=WHITE, anchor='w')
        self.file_title.pack(anchor='w')
        self.file_sub = tk.Label(file_information, font=(UI[0], 8), fg='#8a8f98', bg=WHITE, anchor='w')
        self.file_sub.pack(anchor='w')
        compiler_ready = os.path.isfile(COMPILER_PATH)
        tk.Label(inner, text='●  Compiler Ready' if compiler_ready else '●  Compiler Not Built (run make)', fg=GREEN if compiler_ready else RED, bg=WHITE, font=(UI[0], 9)).pack(side=tk.RIGHT)
        self._update_file_label()

    def _build_pipeline(self):
        self.pipeline_row = tk.Frame(self, bg=BG)
        self.pipeline_row.pack(fill=tk.X, padx=14, pady=(10, 8))

    def _refresh_pipeline(self, statuses):
        names = ('Lexer (Tokens)', 'Parser (AST)', 'Semantic', 'Intermediate (TAC)', 'Optimizer', 'Target (Assembly)')
        icons = {'ok': '✓', 'fail': '✕', 'skip': '–'}
        for widget in self.pipeline_row.winfo_children():
            widget.destroy()
        for index, (name, status) in enumerate(zip(names, statuses)):
            make_pill(self.pipeline_row, name, status).pack(side=tk.LEFT)
            if index < len(names) - 1:
                make_connector(self.pipeline_row).pack(side=tk.LEFT)
            self.notebook.tab(index, text='{}. {}  {}'.format(index + 1, name, icons[status]))

    def _build_body(self):
        body = ttk.Panedwindow(self, orient=tk.VERTICAL)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        top = ttk.Panedwindow(body, orient=tk.HORIZONTAL)
        editor_panel = tk.Frame(top, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        inspector_panel = tk.Frame(top, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        console_panel = tk.Frame(body, bg=BG)
        top.add(editor_panel, weight=1)
        top.add(inspector_panel, weight=1)
        body.add(top, weight=3)
        body.add(console_panel, weight=2)
        self._build_editor(editor_panel)
        self._build_output_panel(inspector_panel)
        self._build_console_panel(console_panel)

    def _build_editor(self, parent):
        left_panel = parent
        tk.Label(left_panel, text='Source Code Editor', font=(UI[0], 10, 'bold'), bg=WHITE).pack(anchor='w', padx=8, pady=(6, 4))
        editor_container = tk.Frame(left_panel, bg=BORDER)
        editor_container.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))
        self.linenumbers = tk.Text(editor_container, width=4, padx=6, wrap='none', font=MONO, bg='#eef0f2', fg='#8a8f98', bd=0, state='disabled', takefocus=0, cursor='arrow')
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)
        self.editor = tk.Text(editor_container, wrap='none', font=MONO, undo=True, bg=WHITE, bd=0, padx=6, insertbackground='black')
        vertical_scrollbar = ttk.Scrollbar(editor_container, orient='vertical', command=self.editor.yview)
        horizontal_scrollbar = ttk.Scrollbar(left_panel, orient='horizontal', command=self.editor.xview)
        self.editor.configure(yscrollcommand=self._on_editor_yview, xscrollcommand=horizontal_scrollbar.set)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.editor_yscroll = vertical_scrollbar
        self.linenumbers.bind('<MouseWheel>', lambda event: self.editor.yview_scroll(int(-event.delta / 120), 'units'))
        self.linenumbers.bind('<Button-4>', lambda _event: self.editor.yview_scroll(-1, 'units'))
        self.linenumbers.bind('<Button-5>', lambda _event: self.editor.yview_scroll(1, 'units'))
        tag_options = (('kw', {'foreground': KEYWORD}), ('comment', {'foreground': COMMENT}), ('number', {'foreground': NUMBER}), ('curline', {'background': CURLINE}), ('error_line', {'background': ERRLINE}))
        for tag, options in tag_options:
            self.editor.tag_configure(tag, **options)
        self.editor.tag_lower('curline')
        self.editor.tag_raise('error_line')
        self.editor.bind('<KeyRelease>', self._on_editor_change)
        self.editor.bind('<ButtonRelease-1>', self._on_editor_change)

    def _build_output_panel(self, parent):
        right_panel = parent
        output_header = tk.Frame(right_panel, bg=WHITE)
        output_header.pack(fill=tk.X, padx=8, pady=(6, 4))
        tk.Label(output_header, text='Compiler Pipeline Phase Inspector', font=(UI[0], 10, 'bold'), bg=WHITE).pack(side=tk.LEFT)
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))
        self.tokens_view = self._make_text_tab('1. Lexer (Tokens)')
        self._build_parser_ast_tab()
        self.semantic_view = self._make_text_tab('3. Semantic')
        self.tac_view = self._make_text_tab('4. Intermediate (TAC)')
        self.optimizer_view = self._make_text_tab('5. Optimizer')
        self.assembly_view = self._make_text_tab('6. Target (Assembly)')

    def _build_parser_ast_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='2. Parser (AST)')
        self.parsing_view = tk.Text(frame, height=3, wrap='word', font=MONO_SM, state='disabled', bg=WHITE, bd=0, padx=6)
        self.parsing_view.pack(fill=tk.X)
        self.parsing_view.tag_configure('error', foreground=RED)
        self.parsing_view.tag_configure('ok', foreground=GREEN)
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        self.ast_tree = ttk.Treeview(tree_frame, show='tree')
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.ast_tree.yview)
        self.ast_tree.configure(yscrollcommand=scrollbar.set)
        self.ast_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _make_text_tab(self, title):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        text_widget = tk.Text(frame, wrap='none', font=MONO_SM, state='disabled', bg=WHITE, bd=0, padx=6)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.tag_configure('error', foreground=RED)
        text_widget.tag_configure('ok', foreground=GREEN)
        return text_widget

    def _build_console_panel(self, parent):
        header = tk.Frame(parent, bg=BG)
        header.pack(fill=tk.X, pady=(4, 2))
        tk.Label(header, text='■  Output Terminal / Console Log', font=(UI[0], 10, 'bold'), bg=BG).pack(side=tk.LEFT)
        self.error_badge = tk.Label(header, text='', bg=RED, fg='white', font=(UI[0], 8, 'bold'), padx=6)
        tk.Label(header, text='Click an error line to jump to source.', font=(UI[0], 8), fg='#8a8f98', bg=BG).pack(side=tk.RIGHT)
        container = tk.Frame(parent, bg=BORDER)
        container.pack(fill=tk.BOTH, expand=True)
        self.console_view = tk.Text(container, wrap='none', font=MONO_SM, state='disabled', bg=WHITE, bd=0, padx=8, pady=6)
        vertical = ttk.Scrollbar(container, orient='vertical', command=self.console_view.yview)
        horizontal = ttk.Scrollbar(container, orient='horizontal', command=self.console_view.xview)
        self.console_view.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        horizontal.pack(side=tk.BOTTOM, fill=tk.X)
        vertical.pack(side=tk.RIGHT, fill=tk.Y)
        self.console_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.console_view.tag_configure('error', foreground=RED)
        self.console_view.tag_configure('ok', foreground=GREEN)
        self.console_view.bind('<Button-1>', self._on_console_click)

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value='Ready.')
        self.status_label = tk.Label(self, textvariable=self.status_var, anchor='w', padx=8, pady=4, bg=BG)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def _bind_shortcuts(self):
        self.bind('<Control-o>', lambda _event: self.load_file())
        self.bind('<Control-s>', lambda _event: self.save_file())
        self.bind('<Control-Shift-S>', lambda _event: self.save_file_as())
        self.bind('<Control-Return>', lambda _event: self.run_compiler())
        self.bind('<Control-a>', self._select_all)

    def _on_editor_change(self, _event=None):
        self.is_dirty = True
        self._update_file_label()
        self._update_line_numbers()
        self._highlight_syntax()
        self._highlight_current_line()

    def _update_line_numbers(self):
        total_lines = int(self.editor.index('end-1c').split('.')[0])
        self.linenumbers.configure(state='normal')
        self.linenumbers.delete('1.0', tk.END)
        self.linenumbers.insert('1.0', '\n'.join((str(line) for line in range(1, total_lines + 1))))
        self.linenumbers.configure(state='disabled')
        self.linenumbers.yview_moveto(self.editor.yview()[0])

    def _highlight_syntax(self):
        content = self.editor.get('1.0', 'end-1c')
        for tag in ('kw', 'number', 'comment'):
            self.editor.tag_remove(tag, '1.0', tk.END)
        patterns = ((KEYWORD_RE, 'kw'), (NUMBER_RE, 'number'), (COMMENT_RE, 'comment'))
        for pattern, tag in patterns:
            for match in pattern.finditer(content):
                self.editor.tag_add(tag, '1.0+{}c'.format(match.start()), '1.0+{}c'.format(match.end()))

    def _highlight_current_line(self):
        self.editor.tag_remove('curline', '1.0', tk.END)
        current_position = self.editor.index('insert')
        self.editor.tag_add('curline', '{} linestart'.format(current_position), '{} lineend+1c'.format(current_position))

    def _on_editor_yview(self, first, last):
        self.editor_yscroll.set(first, last)
        self.linenumbers.yview_moveto(first)

    def _jump_to_editor_line(self, line_number):
        last_line = int(self.editor.index('end-1c').split('.')[0])
        line_number = max(1, min(line_number, last_line))
        self.editor.tag_remove('error_line', '1.0', tk.END)
        self.editor.tag_add('error_line', '{}.0'.format(line_number), '{}.end+1c'.format(line_number))
        self.editor.see('{}.0'.format(line_number))
        self.editor.mark_set('insert', '{}.0'.format(line_number))
        self.editor.focus_set()

    def _on_console_click(self, event):
        index = self.console_view.index('@{},{}'.format(event.x, event.y))
        line = self.console_view.get('{} linestart'.format(index), '{} lineend'.format(index))
        match = ERR_RE.search(line)
        if match:
            self._jump_to_editor_line(int(match.group(2)))

    def _update_file_label(self):
        if self.current_path:
            name = os.path.basename(self.current_path)
        else:
            extension = {'C': '.c', 'C++': '.cpp', 'Java': '.java'}[self.language_var.get()]
            name = 'untitled{}'.format(extension)
        if self.is_dirty:
            name += ' *'
        self.file_title.configure(text=name)
        self.file_sub.configure(text=self.current_path or '(unsaved)')

    def _on_language_change(self, _event=None):
        language = self.language_var.get()
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', SAMPLES[language])
        self.current_path = None
        self.is_dirty = True
        self._on_editor_change()
        self._refresh_pipeline(['skip'] * 6)
        self.status_var.set('{} sample loaded.'.format(language))

    def load_file(self):
        path = filedialog.askopenfilename(title='Load Source File', filetypes=[('Supported files', '*.src *.c *.cpp *.cc *.cxx *.java *.txt'), ('All files', '*.*')])
        if not path:
            return
        extension = os.path.splitext(path)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            messagebox.showerror('Unsupported file type', 'Please choose a .src, .c, .cpp, .java, or .txt file.')
            return
        if os.path.getsize(path) > MAX_UPLOAD_BYTES:
            messagebox.showerror('File too large', 'Please choose a file under 10 KB.')
            return
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as source_file:
                content = source_file.read()
        except OSError as error:
            messagebox.showerror('Could not read file', str(error))
            return
        self.editor.delete('1.0', tk.END)
        self.editor.insert('1.0', content)
        if extension in ('.cpp', '.cc', '.cxx'):
            self.language_var.set('C++')
        elif extension == '.java':
            self.language_var.set('Java')
        elif extension == '.c':
            self.language_var.set('C')
        self.current_path = path
        self.is_dirty = False
        self._on_editor_change()
        self.is_dirty = False
        self._update_file_label()
        self.status_var.set("Loaded '{}'.".format(path))

    def save_file(self):
        if self.current_path:
            self._write_to_path(self.current_path)
        else:
            self.save_file_as()

    def save_file_as(self):
        language = self.language_var.get()
        extension = {'C': '.c', 'C++': '.cpp', 'Java': '.java'}[language]
        path = filedialog.asksaveasfilename(title='Save Source File', defaultextension=extension, filetypes=[('Source files', '*.c *.cpp *.java *.src'), ('All files', '*.*')])
        if path:
            self._write_to_path(path)

    def _write_to_path(self, path):
        try:
            with open(path, 'w', encoding='utf-8') as source_file:
                source_file.write(self.editor.get('1.0', 'end-1c'))
        except OSError as error:
            messagebox.showerror('Could not save file', str(error))
            return
        self.current_path = path
        self.is_dirty = False
        self._update_file_label()
        self.status_var.set("Saved '{}'.".format(path))

    def clear_all(self):
        self.editor.delete('1.0', tk.END)
        self.current_path = None
        self._on_editor_change()
        self.is_dirty = False
        self._update_file_label()
        self._refresh_pipeline(['skip'] * 6)
        self.error_badge.pack_forget()
        for output_view in (self.tokens_view, self.parsing_view, self.semantic_view, self.tac_view, self.optimizer_view, self.assembly_view, self.console_view):
            self._set_text(output_view, '')
        self.ast_tree.delete(*self.ast_tree.get_children())
        self.status_var.set('Ready.')

    def run_compiler(self):
        source = self.editor.get('1.0', 'end-1c')
        if not source.strip():
            messagebox.showwarning('Nothing to run', 'The editor is empty.')
            return
        self.editor.tag_remove('error_line', '1.0', tk.END)
        self.status_var.set('Running {} compiler pipeline...'.format(self.language_var.get()))
        self.update_idletasks()
        result = cr.run_source(source, compiler_path=COMPILER_PATH, language=self.language_var.get())
        if 'error' in result:
            messagebox.showerror('Compiler error', result['error'])
            self.status_var.set('Failed to run compiler.')
            return
        self._display_result(result)

    @staticmethod
    def _output_section(output, title, next_title=None):
        marker = '===== {} ====='.format(title)
        start = output.find(marker)
        if start < 0:
            return ''
        start += len(marker)
        if next_title:
            end = output.find('===== {} ====='.format(next_title), start)
            if end < 0:
                end = len(output)
        else:
            end = len(output)
        return output[start:end].strip()

    def _prepare_six_phases(self, result):
        raw = result.get('raw_stdout', '')
        result['tac'] = self._output_section(raw, 'Three Address Code (TAC)', 'Code Optimization') or result.get('tac', '')
        result['optimizer'] = self._output_section(raw, 'Code Optimization', 'Target Code Generation (Assembly)')
        result['assembly'] = self._output_section(raw, 'Target Code Generation (Assembly)')

    def _pipeline_status(self, result):
        if result['lexical_errors']:
            return ['fail', 'skip', 'skip', 'skip', 'skip', 'skip']
        if not result['parsed']:
            return ['ok', 'fail', 'skip', 'skip', 'skip', 'skip']
        semantic_ok = not result['semantic_errors'] and 'SKIPPED' not in result['semantic_summary']
        tac_ok = semantic_ok and bool(result['tac'].strip()) and 'NOT GENERATED' not in result['tac']
        optimizer_ok = tac_ok and bool(result['optimizer'].strip()) and 'NOT EXECUTED' not in result['optimizer']
        assembly_ok = optimizer_ok and bool(result['assembly'].strip()) and 'NOT GENERATED' not in result['assembly']
        return ['ok', 'ok', 'ok' if semantic_ok else 'fail', 'ok' if tac_ok else 'skip', 'ok' if optimizer_ok else 'skip', 'ok' if assembly_ok else 'skip']

    def _parse_errors(self, stderr_text):
        rows = []
        for line in stderr_text.splitlines():
            match = ERR_RE.match(line.strip())
            if match:
                rows.append((match.group(2), match.group(1), match.group(3)))
        return rows

    def _populate_ast(self, ast_text):
        self.ast_tree.delete(*self.ast_tree.get_children())
        stack = {-1: ''}
        for line in ast_text.splitlines():
            if not line.strip():
                continue
            depth = (len(line) - len(line.lstrip(' '))) // 4
            parent = stack.get(depth - 1, '')
            node = self.ast_tree.insert(parent, 'end', text=line.strip(), open=True)
            stack[depth] = node

    def _display_result(self, result):
        self._prepare_six_phases(result)
        self._refresh_pipeline(self._pipeline_status(result))
        self._populate_ast(result['ast'])
        self._set_text(self.tokens_view, result['tokens'] or '(not reached)')
        self._set_text(self.parsing_view, result['parsing'] or '(not reached)', 'ok' if result['parsed'] else 'error')
        semantic_output = []
        if result['semantic_summary']:
            semantic_output.append(result['semantic_summary'])
        if result['semantic_errors']:
            semantic_output.append('')
            semantic_output.extend(result['semantic_errors'])
        if result['symbol_table']:
            semantic_output.extend(('', 'Symbol Table', '-' * 48, result['symbol_table']))
        semantic_ok = result['parsed'] and bool(result['semantic_summary']) and (not result['semantic_errors']) and ('SKIPPED' not in result['semantic_summary'])
        self._set_text(self.semantic_view, '\n'.join(semantic_output) or '(not reached)', 'ok' if semantic_ok else 'error')
        self._set_text(self.tac_view, result['tac'] or '(not generated -- see Semantic tab)')
        self._set_text(self.optimizer_view, result['optimizer'] or '(not generated -- see Intermediate tab)')
        self._set_text(self.assembly_view, result['assembly'] or '(not generated -- see Optimizer tab)')
        error_rows = self._parse_errors(result['raw_stderr'])
        failed = result['returncode'] != 0
        banner = 'BUILD FAILED: COMPILER ERROR ENCOUNTERED' if failed else 'BUILD SUCCESSFUL: ALL 6 PHASES COMPLETED'
        diagnostics = '\n'.join(('[ERROR] {} Error at line {}: {}'.format(error_type, line, message) for line, error_type, message in error_rows))
        summary = '=' * 54 + '\n' + banner + '\n' + '=' * 54
        if diagnostics:
            summary += '\n\n' + diagnostics
        console_output = '{}\n\nFull Console Output:\n\n{}{}'.format(summary, result['raw_stdout'].strip(), '\n\n' + result['raw_stderr'].strip() if result['raw_stderr'].strip() else '')
        self._set_text(self.console_view, console_output)
        self.console_view.configure(state='normal')
        self.console_view.tag_add('error' if failed else 'ok', '1.0', '{}.end'.format(len(summary.splitlines())))
        self.console_view.configure(state='disabled')
        if error_rows:
            self.error_badge.configure(text=str(len(error_rows)))
            self.error_badge.pack(side=tk.LEFT, padx=6)
        else:
            self.error_badge.pack_forget()
        if result['lexical_errors']:
            self.status_var.set('Lexical analysis failed -- see Errors / Raw.')
        elif not result['parsed']:
            self.status_var.set('Parsing failed -- see Errors / Raw.')
        elif result['semantic_errors']:
            self.status_var.set('{} semantic error(s) found.'.format(len(result['semantic_errors'])))
        else:
            self.status_var.set('Success: all 6 compiler phases completed.')

    @staticmethod
    def _set_text(widget, content, tag=None):
        widget.configure(state='normal')
        widget.delete('1.0', tk.END)
        widget.insert('1.0', content)
        if tag:
            widget.tag_add(tag, '1.0', tk.END)
        widget.configure(state='disabled')
if __name__ == '__main__':
    if not os.path.isfile(COMPILER_PATH):
        print("Warning: compiler binary not found at '{}'. Run 'make' first.".format(COMPILER_PATH))
    SyntaxStudioApp().mainloop()