"""
Simple dialog helpers that respect the application theme.
"""
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Optional

from app.theme import BG, FG, ACCENT


def ask_save_path(initial_filename: str = "audio.mp3") -> Optional[str]:
    """Show a Save As dialog. Returns chosen path or None if cancelled."""
    path = filedialog.asksaveasfilename(
        title="Save Audio File",
        initialfile=initial_filename,
        defaultextension=".mp3",
        filetypes=[
            ("MP3 Audio", "*.mp3"),
            ("WAV Audio", "*.wav"),
            ("All files", "*.*"),
        ],
    )
    return path if path else None


def show_error(title: str, message: str) -> None:
    messagebox.showerror(title, message)


def show_info(title: str, message: str) -> None:
    messagebox.showinfo(title, message)


def ask_confirm(title: str, message: str) -> bool:
    return messagebox.askyesno(title, message)
