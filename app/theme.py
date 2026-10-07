"""
Modern dark theme for the AI Human Voice application.
Applies ttk.Style rules and provides colour/font constants.
"""
import tkinter as tk
from tkinter import ttk

# ── Colour palette ─────────────────────────────────────────────────────────
BG          = "#1e1e2e"   # main background
BG_CARD     = "#2a2a3e"   # panel / card background
BG_INPUT    = "#13131f"   # text-input area
ACCENT      = "#7c6af7"   # primary accent (purple-blue)
ACCENT_DARK = "#5a4ed1"   # hover / pressed
SUCCESS     = "#50fa7b"   # green for completed
WARNING     = "#f1fa8c"   # yellow for in-progress
ERROR       = "#ff5555"   # red for errors
FG          = "#cdd6f4"   # main text
FG_DIM      = "#6c7086"   # secondary / disabled text
FG_HEADING  = "#f5c2e7"   # heading text

# ── Fonts ──────────────────────────────────────────────────────────────────
FONT_HEADING = ("Segoe UI", 14, "bold")
FONT_LABEL   = ("Segoe UI", 10)
FONT_BODY    = ("Segoe UI", 10)
FONT_SMALL   = ("Segoe UI", 9)
FONT_MONO    = ("Consolas", 10)


def apply(root: tk.Tk) -> ttk.Style:
    """Configure and return the ttk Style for the application."""
    root.configure(bg=BG)

    style = ttk.Style(root)

    # Use a base that supports full styling on all platforms
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass   # clam not available — fall back to default

    # ── General ───────────────────────────────────────────────────────
    style.configure(".",
        background=BG,
        foreground=FG,
        fieldbackground=BG_INPUT,
        font=FONT_BODY,
        borderwidth=0,
        focuscolor=ACCENT,
    )

    # ── Frames ────────────────────────────────────────────────────────
    style.configure("TFrame",      background=BG)
    style.configure("Card.TFrame", background=BG_CARD, relief="flat")

    # ── Labels ────────────────────────────────────────────────────────
    style.configure("TLabel",       background=BG,      foreground=FG,        font=FONT_BODY)
    style.configure("Card.TLabel",  background=BG_CARD, foreground=FG,        font=FONT_BODY)
    style.configure("Heading.TLabel", background=BG,   foreground=FG_HEADING, font=FONT_HEADING)
    style.configure("Dim.TLabel",   background=BG,      foreground=FG_DIM,    font=FONT_SMALL)
    style.configure("Dim.Card.TLabel", background=BG_CARD, foreground=FG_DIM, font=FONT_SMALL)
    style.configure("Success.TLabel", background=BG,    foreground=SUCCESS,   font=FONT_SMALL)
    style.configure("Error.TLabel",   background=BG,    foreground=ERROR,     font=FONT_SMALL)
    style.configure("Warning.TLabel", background=BG,    foreground=WARNING,   font=FONT_SMALL)

    # ── Buttons ───────────────────────────────────────────────────────
    style.configure("Accent.TButton",
        background=ACCENT, foreground="#ffffff",
        font=("Segoe UI", 10, "bold"),
        borderwidth=0, relief="flat", padding=(14, 8),
    )
    style.map("Accent.TButton",
        background=[("active", ACCENT_DARK), ("disabled", "#444456")],
        foreground=[("disabled", FG_DIM)],
    )
    style.configure("TButton",
        background=BG_CARD, foreground=FG,
        font=FONT_BODY, borderwidth=0, relief="flat", padding=(10, 6),
    )
    style.map("TButton",
        background=[("active", "#3a3a5e"), ("disabled", "#2a2a3e")],
        foreground=[("disabled", FG_DIM)],
    )
    style.configure("Danger.TButton",
        background="#3d1f1f", foreground=ERROR,
        font=FONT_SMALL, borderwidth=0, relief="flat", padding=(8, 4),
    )
    style.map("Danger.TButton",
        background=[("active", "#5c2c2c")],
    )
    style.configure("Small.TButton",
        background=BG_CARD, foreground=FG,
        font=FONT_SMALL, borderwidth=0, relief="flat", padding=(6, 3),
    )
    style.map("Small.TButton",
        background=[("active", "#3a3a5e")],
    )

    # ── Combobox ──────────────────────────────────────────────────────
    style.configure("TCombobox",
        fieldbackground=BG_INPUT, background=BG_CARD,
        foreground=FG, selectforeground=FG,
        selectbackground=ACCENT,
        arrowcolor=ACCENT,
    )
    style.map("TCombobox",
        fieldbackground=[("readonly", BG_INPUT)],
        foreground=[("readonly", FG)],
    )

    # ── Scale (slider) ────────────────────────────────────────────────
    style.configure("TScale",
        background=BG, troughcolor=BG_CARD,
        sliderrelief="flat",
    )

    # ── Progressbar ───────────────────────────────────────────────────
    style.configure("TProgressbar",
        troughcolor=BG_CARD, background=ACCENT,
        borderwidth=0, thickness=6,
    )

    # ── Scrollbar ─────────────────────────────────────────────────────
    style.configure("TScrollbar",
        background=BG_CARD, troughcolor=BG,
        arrowcolor=FG_DIM, borderwidth=0,
    )
    style.map("TScrollbar",
        background=[("active", ACCENT)],
    )

    # ── Separator ─────────────────────────────────────────────────────
    style.configure("TSeparator", background=BG_CARD)

    # ── Notebook (tabs) ───────────────────────────────────────────────
    style.configure("TNotebook",        background=BG, borderwidth=0)
    style.configure("TNotebook.Tab",
        background=BG_CARD, foreground=FG_DIM,
        padding=(14, 6), borderwidth=0,
    )
    style.map("TNotebook.Tab",
        background=[("selected", BG)],
        foreground=[("selected", ACCENT)],
    )

    return style
