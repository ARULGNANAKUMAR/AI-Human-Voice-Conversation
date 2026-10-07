"""
gui.py — Main application window for AI Human Voice Conversation.

Layout:
  Left panel  : Text input + voice controls + generate/playback buttons
  Right panel : Audio history list
"""
import logging
import queue
import shutil
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk
from typing import List, Optional

import app.theme as theme
from app.dialogs import ask_save_path, ask_confirm, show_error, show_info
from config import (
    APP_NAME, AUDIO_DIR, DEFAULT_LANGUAGE, DEFAULT_SPEED,
    DEFAULT_VOICE, SUPPORTED_FORMATS,
)
from models.audio_record import AudioRecord
from services.audio_service import AudioService
from services.history_service import HistoryService
from services.text_processor import TextProcessor
from services.tts_service import TTSService, get_voices_for_language
from utils.file_utils import timestamped_filename, temp_path, ensure_dirs
from utils.validators import validate_text

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Worker message types
# ─────────────────────────────────────────────────────────────────────────────
class _Msg:
    PROGRESS   = "progress"
    DONE       = "done"
    ERROR      = "error"
    STATUS     = "status"


# ─────────────────────────────────────────────────────────────────────────────
# Main window
# ─────────────────────────────────────────────────────────────────────────────
class VoiceApp(tk.Tk):
    """Root Tkinter window — owns all services and the main event loop."""

    def __init__(
        self,
        tts_service:     TTSService,
        audio_service:   AudioService,
        history_service: HistoryService,
    ) -> None:
        super().__init__()

        self._tts     = tts_service
        self._audio   = audio_service
        self._history = history_service
        self._text_proc = TextProcessor()

        # State
        self._generating    = False
        self._current_audio: Optional[Path] = None
        self._playback_paused = False
        self._ui_queue: queue.Queue = queue.Queue()

        # Build UI
        self._configure_window()
        self._style = theme.apply(self)
        self._build_ui()
        self._load_history()

        # Poll the worker queue
        self._poll_queue()

        # Playback ticker
        self._tick_playback()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Window setup ──────────────────────────────────────────────────

    def _configure_window(self) -> None:
        self.title(APP_NAME)
        self.geometry("1160x800")
        self.minsize(900, 650)
        self.configure(bg=theme.BG)
        # Centre on screen
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - 1160) // 2
        y = (sh - 800)  // 2
        self.geometry(f"1160x800+{x}+{y}")

    # ── UI construction ───────────────────────────────────────────────

    def _build_ui(self) -> None:
        # ── Title bar area ────────────────────────────────────────────
        title_bar = tk.Frame(self, bg=theme.BG, pady=12)
        title_bar.pack(fill="x", padx=20)

        tk.Label(
            title_bar, text="🎙  " + APP_NAME,
            font=("Segoe UI", 17, "bold"),
            bg=theme.BG, fg=theme.FG_HEADING,
        ).pack(side="left")

        tk.Label(
            title_bar, text="Powered by Microsoft Edge Neural TTS",
            font=theme.FONT_SMALL, bg=theme.BG, fg=theme.FG_DIM,
        ).pack(side="left", padx=(14, 0), pady=(4, 0))

        # ── Separator ─────────────────────────────────────────────────
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20)

        # ── Main paned layout ─────────────────────────────────────────
        main = tk.Frame(self, bg=theme.BG)
        main.pack(fill="both", expand=True, padx=16, pady=12)

        # Left panel (~60%)  Right panel (~40%)
        left  = tk.Frame(main, bg=theme.BG)
        right = tk.Frame(main, bg=theme.BG, width=370)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right.pack(side="right", fill="both", expand=False)
        right.pack_propagate(False)

        self._build_left(left)
        self._build_right(right)

    # ── Left panel ────────────────────────────────────────────────────

    def _build_left(self, parent: tk.Frame) -> None:
        # ── Text input card ───────────────────────────────────────────
        card_text = self._card(parent, "Content")
        card_text.pack(fill="both", expand=True, pady=(0, 10))

        # Text area
        txt_frame = tk.Frame(card_text, bg=theme.BG_CARD)
        txt_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self._text_area = tk.Text(
            txt_frame,
            wrap="word", font=("Segoe UI", 11),
            bg=theme.BG_INPUT, fg=theme.FG,
            insertbackground=theme.ACCENT,
            relief="flat", bd=0,
            padx=10, pady=8,
            height=12,
        )
        sb = ttk.Scrollbar(txt_frame, command=self._text_area.yview)
        self._text_area.configure(yscrollcommand=sb.set)
        self._text_area.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._text_area.bind("<KeyRelease>", self._update_char_count)

        # Bottom bar of text card
        bot = tk.Frame(card_text, bg=theme.BG_CARD)
        bot.pack(fill="x", padx=12, pady=(0, 10))

        self._char_label = tk.Label(
            bot, text="Characters: 0",
            font=theme.FONT_SMALL, bg=theme.BG_CARD, fg=theme.FG_DIM,
        )
        self._char_label.pack(side="left")

        ttk.Button(bot, text="Clear", style="Small.TButton",
                   command=self._clear_text).pack(side="right")

        # ── Voice settings card ───────────────────────────────────────
        card_cfg = self._card(parent, "Voice Settings")
        card_cfg.pack(fill="x", pady=(0, 10))

        cfg_inner = tk.Frame(card_cfg, bg=theme.BG_CARD)
        cfg_inner.pack(fill="x", padx=12, pady=(4, 12))

        # Row 1 — Language + Voice
        row1 = tk.Frame(cfg_inner, bg=theme.BG_CARD)
        row1.pack(fill="x", pady=(0, 8))

        self._build_combo(row1, "Language", left=True)
        self._build_combo(row1, "Voice",    left=False)

        # Row 2 — Speed + Style
        row2 = tk.Frame(cfg_inner, bg=theme.BG_CARD)
        row2.pack(fill="x")

        # Speed slider
        spd_col = tk.Frame(row2, bg=theme.BG_CARD)
        spd_col.pack(side="left", fill="x", expand=True, padx=(0, 16))

        tk.Label(spd_col, text="Speed", font=theme.FONT_SMALL,
                 bg=theme.BG_CARD, fg=theme.FG_DIM).pack(anchor="w")

        slider_row = tk.Frame(spd_col, bg=theme.BG_CARD)
        slider_row.pack(fill="x")

        tk.Label(slider_row, text="0.5×", font=theme.FONT_SMALL,
                 bg=theme.BG_CARD, fg=theme.FG_DIM).pack(side="left")

        self._speed_var = tk.DoubleVar(value=DEFAULT_SPEED)
        self._speed_slider = ttk.Scale(
            slider_row, from_=0.5, to=2.0, orient="horizontal",
            variable=self._speed_var, command=self._update_speed_label,
        )
        self._speed_slider.pack(side="left", fill="x", expand=True, padx=6)

        tk.Label(slider_row, text="2.0×", font=theme.FONT_SMALL,
                 bg=theme.BG_CARD, fg=theme.FG_DIM).pack(side="left")

        self._speed_label = tk.Label(
            spd_col, text="1.0×", font=("Segoe UI", 9, "bold"),
            bg=theme.BG_CARD, fg=theme.ACCENT,
        )
        self._speed_label.pack(anchor="e")

        # Style combo
        sty_col = tk.Frame(row2, bg=theme.BG_CARD)
        sty_col.pack(side="right", fill="x", expand=True)

        tk.Label(sty_col, text="Style", font=theme.FONT_SMALL,
                 bg=theme.BG_CARD, fg=theme.FG_DIM).pack(anchor="w")
        self._style_var = tk.StringVar(value="Conversational")
        style_cb = ttk.Combobox(
            sty_col, textvariable=self._style_var,
            values=["Conversational", "Newscast", "Cheerful",
                    "Calm", "Empathetic", "Excited"],
            state="readonly", width=18,
        )
        style_cb.pack(fill="x")

        # ── Action buttons card ───────────────────────────────────────
        card_act = self._card(parent, "")
        card_act.pack(fill="x", pady=(0, 10))

        act_inner = tk.Frame(card_act, bg=theme.BG_CARD)
        act_inner.pack(fill="x", padx=12, pady=10)

        # Generate button
        self._btn_generate = ttk.Button(
            act_inner, text="⚡  Generate Voice",
            style="Accent.TButton",
            command=self._on_generate,
        )
        self._btn_generate.pack(side="left", padx=(0, 10))

        # Playback controls
        pb_frame = tk.Frame(act_inner, bg=theme.BG_CARD)
        pb_frame.pack(side="left")

        self._btn_play = ttk.Button(pb_frame, text="▶  Play",
                                    style="TButton", command=self._on_play,
                                    state="disabled")
        self._btn_play.pack(side="left", padx=(0, 6))

        self._btn_pause = ttk.Button(pb_frame, text="⏸  Pause",
                                     style="TButton", command=self._on_pause,
                                     state="disabled")
        self._btn_pause.pack(side="left", padx=(0, 6))

        self._btn_stop = ttk.Button(pb_frame, text="⏹  Stop",
                                    style="TButton", command=self._on_stop,
                                    state="disabled")
        self._btn_stop.pack(side="left", padx=(0, 10))

        # Save button
        self._btn_save = ttk.Button(
            act_inner, text="💾  Save Audio",
            style="TButton", command=self._on_save,
            state="disabled",
        )
        self._btn_save.pack(side="left")

        # ── Progress + status ─────────────────────────────────────────
        card_stat = self._card(parent, "")
        card_stat.pack(fill="x")

        stat_inner = tk.Frame(card_stat, bg=theme.BG_CARD)
        stat_inner.pack(fill="x", padx=12, pady=10)

        self._progress = ttk.Progressbar(
            stat_inner, mode="determinate", maximum=100,
        )
        self._progress.pack(fill="x", pady=(0, 6))

        self._status_var = tk.StringVar(value="Ready")
        self._status_label = tk.Label(
            stat_inner, textvariable=self._status_var,
            font=theme.FONT_SMALL, bg=theme.BG_CARD, fg=theme.FG_DIM,
            anchor="w",
        )
        self._status_label.pack(fill="x")

        self._current_label = tk.Label(
            stat_inner, text="",
            font=theme.FONT_SMALL, bg=theme.BG_CARD, fg=theme.ACCENT,
            anchor="w",
        )
        self._current_label.pack(fill="x")

        # Populate dropdowns
        self._populate_language_combo()

    def _build_combo(self, parent: tk.Frame, label: str, left: bool) -> None:
        """Helper to build a labelled combobox in a flex column."""
        col = tk.Frame(parent, bg=theme.BG_CARD)
        if left:
            col.pack(side="left", fill="x", expand=True, padx=(0, 16))
        else:
            col.pack(side="left", fill="x", expand=True)

        tk.Label(col, text=label, font=theme.FONT_SMALL,
                 bg=theme.BG_CARD, fg=theme.FG_DIM).pack(anchor="w")

        if label == "Language":
            self._lang_var = tk.StringVar(value=DEFAULT_LANGUAGE)
            cb = ttk.Combobox(col, textvariable=self._lang_var,
                               state="readonly", width=16)
            cb.bind("<<ComboboxSelected>>", self._on_language_change)
            self._lang_combo = cb
        else:
            self._voice_var = tk.StringVar()
            cb = ttk.Combobox(col, textvariable=self._voice_var,
                               state="readonly", width=32)
            self._voice_combo = cb

        cb.pack(fill="x")

    def _populate_language_combo(self) -> None:
        from services.tts_service import VOICE_CATALOGUE
        langs = list(VOICE_CATALOGUE.keys())
        self._lang_combo["values"] = langs
        self._lang_var.set(DEFAULT_LANGUAGE)
        self._populate_voice_combo(DEFAULT_LANGUAGE)

    def _populate_voice_combo(self, language: str) -> None:
        voices = get_voices_for_language(language)
        display_names = [d for d, _ in voices]
        self._voice_combo["values"] = display_names
        if display_names:
            # Try to keep the default voice selected
            for i, (_, vid) in enumerate(voices):
                if vid == DEFAULT_VOICE:
                    self._voice_combo.current(i)
                    return
            self._voice_combo.current(0)

    def _get_selected_voice_id(self) -> str:
        """Map the displayed voice name back to the edge-tts voice ID."""
        lang  = self._lang_var.get()
        voices = get_voices_for_language(lang)
        idx   = self._voice_combo.current()
        if 0 <= idx < len(voices):
            return voices[idx][1]
        return DEFAULT_VOICE

    # ── Right panel — Audio History ───────────────────────────────────

    def _build_right(self, parent: tk.Frame) -> None:
        card = self._card(parent, "Audio History")
        card.pack(fill="both", expand=True)

        # Scrollable list container
        canvas = tk.Canvas(card, bg=theme.BG_CARD, highlightthickness=0)
        vsb = ttk.Scrollbar(card, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y", padx=(0, 4))
        canvas.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)

        self._history_frame = tk.Frame(canvas, bg=theme.BG_CARD)
        self._history_window = canvas.create_window(
            (0, 0), window=self._history_frame, anchor="nw"
        )

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(self._history_window, width=event.width)

        self._history_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mouse-wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self._history_canvas = canvas
        self._history_items: List[tk.Frame] = []

        self._no_history_label = tk.Label(
            self._history_frame,
            text="No generated audio yet.\nGenerate your first voice above!",
            font=theme.FONT_SMALL, bg=theme.BG_CARD, fg=theme.FG_DIM,
            justify="center",
        )
        self._no_history_label.pack(pady=30)

    # ── History item widget ───────────────────────────────────────────

    def _add_history_item(self, record: AudioRecord) -> None:
        """Insert a history card at the top of the history panel."""
        if self._no_history_label.winfo_ismapped():
            self._no_history_label.pack_forget()

        item = tk.Frame(
            self._history_frame,
            bg="#313152", pady=8, padx=10,
        )
        item.pack(fill="x", pady=(0, 6))
        self._history_items.insert(0, item)

        # Filename
        tk.Label(
            item, text=f"🔊  {record.filename}",
            font=("Segoe UI", 9, "bold"),
            bg="#313152", fg=theme.FG,
            anchor="w",
        ).pack(fill="x")

        # Meta line
        meta = f"{record.created_at_display}  ·  {record.duration_str}  ·  {record.format.upper()}"
        tk.Label(
            item, text=meta,
            font=theme.FONT_SMALL, bg="#313152", fg=theme.FG_DIM,
            anchor="w",
        ).pack(fill="x", pady=(2, 6))

        # Buttons
        btn_row = tk.Frame(item, bg="#313152")
        btn_row.pack(fill="x")

        def play_this(p=record.filepath):
            self._play_file(Path(p))

        def delete_this(r=record, w=item):
            self._delete_history_item(r, w)

        ttk.Button(btn_row, text="▶ Play",
                   style="Small.TButton", command=play_this).pack(side="left", padx=(0, 6))
        ttk.Button(btn_row, text="🗑 Delete",
                   style="Danger.TButton", command=delete_this).pack(side="left")

    def _load_history(self) -> None:
        """Load all existing history records from DB into the UI."""
        records = self._history.all_records()
        # Records come newest-first; we want newest at top
        for record in reversed(records):
            if Path(record.filepath).exists():
                self._add_history_item(record)

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _card(parent: tk.Widget, title: str) -> tk.Frame:
        """Create a rounded-looking card frame with an optional title."""
        outer = tk.Frame(parent, bg=theme.BG_CARD, padx=0, pady=0)
        if title:
            tk.Label(
                outer, text=title.upper(),
                font=("Segoe UI", 8, "bold"),
                bg=theme.BG_CARD, fg=theme.FG_DIM,
                padx=12, pady=8,
            ).pack(anchor="w")
        return outer

    def _set_status(self, message: str, colour: str = theme.FG_DIM) -> None:
        self._status_var.set(message)
        self._status_label.configure(fg=colour)

    def _set_progress(self, pct: int) -> None:
        self._progress["value"] = pct

    # ── Event handlers ────────────────────────────────────────────────

    def _on_language_change(self, _event=None) -> None:
        lang = self._lang_var.get()
        self._populate_voice_combo(lang)

    def _update_char_count(self, _event=None) -> None:
        n = len(self._text_area.get("1.0", "end-1c"))
        self._char_label.configure(text=f"Characters: {n:,}")

    def _update_speed_label(self, _val=None) -> None:
        self._speed_label.configure(text=f"{self._speed_var.get():.1f}×")

    def _clear_text(self) -> None:
        self._text_area.delete("1.0", "end")
        self._update_char_count()

    # ── Generate ──────────────────────────────────────────────────────

    def _on_generate(self) -> None:
        text = self._text_area.get("1.0", "end-1c").strip()
        ok, msg = validate_text(text)
        if not ok:
            show_error("Validation Error", msg)
            return

        voice = self._get_selected_voice_id()
        speed = round(self._speed_var.get(), 2)

        self._generating = True
        self._btn_generate.state(["disabled"])
        self._btn_play.state(["disabled"])
        self._btn_pause.state(["disabled"])
        self._btn_stop.state(["disabled"])
        self._btn_save.state(["disabled"])
        self._set_progress(0)
        self._set_status("Processing text…", theme.WARNING)

        chunks = self._text_proc.prepare(text)
        logger.info("Starting generation: %d chunk(s), voice=%s, speed=%.1f",
                    len(chunks), voice, speed)

        t = threading.Thread(
            target=self._worker_generate,
            args=(chunks, voice, speed, text),
            daemon=True,
        )
        t.start()

    def _worker_generate(
        self,
        chunks: List[str],
        voice: str,
        speed: float,
        original_text: str,
    ) -> None:
        """Background thread: synthesise, combine, update UI via queue."""
        try:
            total = len(chunks)

            def tts_progress(pct: int) -> None:
                # pct is TTS progress (0-100 within TTS phase = first 80%)
                overall = int(pct * 0.80)
                self._ui_queue.put((_Msg.PROGRESS, overall))
                self._ui_queue.put((_Msg.STATUS, f"Generating voice… {pct}%"))

            self._ui_queue.put((_Msg.STATUS, f"Generating {total} chunk(s)…"))
            chunk_paths = self._tts.synthesise_chunks(
                chunks, voice, speed, progress_callback=tts_progress
            )

            self._ui_queue.put((_Msg.STATUS, "Combining audio…"))
            self._ui_queue.put((_Msg.PROGRESS, 85))

            out_name  = timestamped_filename("mp3")
            out_path  = AUDIO_DIR / out_name
            tmp_path  = temp_path(".mp3")

            combined  = self._audio.combine_chunks(chunk_paths, tmp_path)
            shutil.move(str(combined), str(out_path))

            # Clean up chunk temps
            for p in chunk_paths:
                try:
                    p.unlink(missing_ok=True)
                except OSError:
                    pass

            self._ui_queue.put((_Msg.PROGRESS, 95))
            self._ui_queue.put((_Msg.STATUS, "Saving to history…"))

            lang = self._lang_var.get()
            record = AudioRecord(
                filename=out_name,
                filepath=str(out_path),
                text=original_text,
                voice=voice,
                language=lang,
                speed=speed,
                format="mp3",
            )
            record = self._history.add(record)

            self._ui_queue.put((_Msg.PROGRESS, 100))
            self._ui_queue.put((_Msg.DONE, (out_path, record)))

        except Exception as exc:
            logger.exception("Generation failed")
            self._ui_queue.put((_Msg.ERROR, str(exc)))

    # ── Playback ──────────────────────────────────────────────────────

    def _on_play(self) -> None:
        if self._current_audio is None:
            return
        if self._playback_paused:
            self._audio.resume()
            self._playback_paused = False
            self._btn_pause.configure(text="⏸  Pause")
            self._set_status("Playing…", theme.SUCCESS)
        else:
            self._play_file(self._current_audio)

    def _on_pause(self) -> None:
        if self._audio.is_playing():
            self._audio.pause()
            self._playback_paused = True
            self._btn_pause.configure(text="▶  Resume")
            self._set_status("Paused", theme.FG_DIM)
        elif self._playback_paused:
            self._audio.resume()
            self._playback_paused = False
            self._btn_pause.configure(text="⏸  Pause")
            self._set_status("Playing…", theme.SUCCESS)

    def _on_stop(self) -> None:
        self._audio.stop()
        self._playback_paused = False
        self._btn_pause.configure(text="⏸  Pause")
        self._set_status("Stopped", theme.FG_DIM)

    def _play_file(self, path: Path) -> None:
        if not path.exists():
            show_error("File Not Found", f"Audio file not found:\n{path}")
            return
        self._audio.stop()
        self._playback_paused = False
        ok = self._audio.play(path)
        if ok:
            self._current_audio = path
            self._btn_pause.configure(text="⏸  Pause")
            self._btn_pause.state(["!disabled"])
            self._btn_stop.state(["!disabled"])
            self._set_status("Playing…", theme.SUCCESS)
            self._current_label.configure(text=f"▶  {path.name}")
        else:
            show_error("Playback Error", "Unable to play the audio file.\nCheck pygame installation.")

    # ── Save ──────────────────────────────────────────────────────────

    def _on_save(self) -> None:
        if self._current_audio is None:
            return
        stem = self._current_audio.stem
        dest = ask_save_path(f"{stem}.mp3")
        if not dest:
            return

        dest_path = Path(dest)
        fmt = dest_path.suffix.lstrip(".").lower()

        try:
            if fmt == "wav":
                self._audio.convert_to_wav(self._current_audio, dest_path)
            else:
                shutil.copy2(str(self._current_audio), str(dest_path))
            show_info("Saved", f"Audio saved to:\n{dest_path}")
            logger.info("Audio saved → %s", dest_path)
        except Exception as exc:
            logger.exception("Save failed")
            show_error("Save Error", f"Unable to save the audio file.\n{exc}")

    # ── Delete history item ───────────────────────────────────────────

    def _delete_history_item(self, record: AudioRecord, widget: tk.Frame) -> None:
        if not ask_confirm("Delete", f"Delete '{record.filename}'?"):
            return
        self._history.delete(record.id, delete_file_too=True)
        widget.destroy()
        self._history_items = [w for w in self._history_items if w != widget]
        if not self._history_items:
            self._no_history_label.pack(pady=30)

    # ── Queue polling ─────────────────────────────────────────────────

    def _poll_queue(self) -> None:
        """Drain the worker-to-UI queue and update widgets safely."""
        try:
            while True:
                msg_type, payload = self._ui_queue.get_nowait()

                if msg_type == _Msg.PROGRESS:
                    self._set_progress(payload)

                elif msg_type == _Msg.STATUS:
                    self._set_status(payload, theme.WARNING)

                elif msg_type == _Msg.DONE:
                    out_path, record = payload
                    self._current_audio = out_path
                    self._generating = False

                    self._btn_generate.state(["!disabled"])
                    self._btn_play.state(["!disabled"])
                    self._btn_save.state(["!disabled"])

                    self._set_status("✔  Generation complete!", theme.SUCCESS)
                    self._current_label.configure(text=f"Ready: {out_path.name}")
                    self._add_history_item(record)

                elif msg_type == _Msg.ERROR:
                    self._generating = False
                    self._btn_generate.state(["!disabled"])
                    self._set_progress(0)
                    self._set_status("⚠  Generation failed — check logs.", theme.ERROR)
                    show_error(
                        "Voice Generation Failed",
                        f"Voice generation failed.\n\nDetails:\n{payload}\n\n"
                        "Please check your internet connection and TTS configuration.",
                    )

        except queue.Empty:
            pass

        self.after(100, self._poll_queue)

    # ── Playback ticker ───────────────────────────────────────────────

    def _tick_playback(self) -> None:
        """Update play button state when audio finishes naturally."""
        if not self._audio.is_playing() and not self._playback_paused:
            # Was playing but stopped — reset UI
            if self._btn_stop["state"] != "disabled":
                self._btn_pause.configure(text="⏸  Pause")
        self.after(500, self._tick_playback)

    # ── Close ─────────────────────────────────────────────────────────

    def _on_close(self) -> None:
        self._audio.stop()
        self._audio.cleanup()
        logger.info("Application closed")
        self.destroy()
