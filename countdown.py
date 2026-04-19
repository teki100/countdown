import random
import threading
import time
import tkinter as tk
from tkinter import ttk

# Session timing (seconds)
SESSION_SECONDS = 60 * 60  # main window countdown + background loop length
POPUP_INTERVAL_MIN = 15 * 60
POPUP_INTERVAL_MAX = 20 * 60
BREAK_FLASH_SECONDS = 30
FINAL_BLOCK_SECONDS = 10 * 60


class CountdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown one hour")
        self.root.geometry("580x300")
        self.root.configure(background="#66a189")
        self.root.resizable(False, False)

        self.countdown_thread = None
        self.is_counting = False

        self.initial_frame = tk.Frame(self.root, background="#66a189")
        self.countdown_frame = tk.Frame(self.root, background="#66a189")

        # macOS system Tk does not support Font spacing1/2/3; use two labels + pady for line gap
        hint_kw = dict(
            fg="white",
            bg="#66a189",
            font=("Courier", 16),
            justify=tk.CENTER,
            wraplength=540,
        )
        tk.Label(
            self.initial_frame,
            text="\n1 hour session · full-screen breaks every 15–20 min\n\n· 30 s reminder · then 10 min closing block",
            **hint_kw,
        ).pack(pady=(16, 10))
        

        self.start_button = ttk.Button(
            self.initial_frame,
            text="Start session",
            style="Custom.TButton",
            command=self.start_countdowns,
        )
        self.start_button.pack(pady=12)
        self.initial_shutdown_button = ttk.Button(
            self.initial_frame,
            text="Exit app",
            style="Custom.TButton",
            command=self.shutdown,
        )
        self.initial_shutdown_button.pack(pady=0)

        self.phase_label = tk.Label(
            self.countdown_frame,
            text="\nMain session",
            fg="#f1db77",
            bg="#66a189",
            font=("Courier", 12),
        )
        self.phase_label.pack(pady=(12, 0))

        self.countdown_label = ttk.Label(self.countdown_frame, style="Custom.TLabel")
        self.countdown_label.pack(pady=24)
        self.countdown_shutdown_button = ttk.Button(
            self.countdown_frame,
            text="Pause & return home",
            style="Custom.TButton",
            command=self.stop_countdowns,
        )
        self.countdown_shutdown_button.pack(pady=0)

        self.initial_frame.pack()

    def start_countdowns(self):
        self.start_button.config(state="disabled")
        self.initial_frame.pack_forget()
        self.countdown_frame.pack()
        self.phase_label.config(text="\nMain session (random breaks)")

        self.is_counting = True
        self.countdown_thread = threading.Thread(target=self.countdown_loop, daemon=True)
        self.countdown_thread.start()

        self.update_session_countdown(SESSION_SECONDS)

    def stop_countdowns(self):
        self.is_counting = False
        self.countdown_frame.pack_forget()
        self.initial_frame.pack()
        self.start_button.config(state="normal")

    def shutdown(self):
        self.root.quit()

    def update_session_countdown(self, remaining):
        if not self.is_counting:
            returnπ
        if remaining >= 0:
            minutes = remaining // 60
            sec = remaining % 60
            self.countdown_label.config(text=f"{minutes:02d}:{sec:02d}")
            self.root.after(1000, self.update_session_countdown, remaining - 1)
        else:
            # Stop background popups before the long closing fullscreen
            self.is_counting = False
            self.phase_label.config(text="Closing block")
            self.show_countdown(
                FINAL_BLOCK_SECONDS,
                "Final block — stay with it",
                on_complete_exit=True,
            )

    def countdown_loop(self):
        start_time = time.time()

        while self.is_counting and (time.time() - start_time < SESSION_SECONDS):
            interval = random.randint(POPUP_INTERVAL_MIN, POPUP_INTERVAL_MAX)
            elapsed = 0
            while elapsed < interval and self.is_counting:
                time.sleep(1)
                elapsed += 1
            if self.is_counting:
                self.root.after(
                    0,
                    lambda: self.show_countdown(
                        BREAK_FLASH_SECONDS,
                        "Short break",
                        on_complete_exit=False,
                    ),
                )

    def show_countdown(self, seconds, heading, on_complete_exit):
        countdown_window = tk.Toplevel(self.root)
        countdown_window.attributes("-fullscreen", True)
        countdown_window.configure(bg="#66a189")

        title = tk.Label(
            countdown_window,
            text=heading,
            font=("Courier", 32, "bold"),
            fg="white",
            bg="#66a189",
        )
        title.pack(pady=(80, 20))

        label = tk.Label(
            countdown_window,
            text="",
            font=("Courier", 120),
            fg="white",
            bg="#66a189",
        )
        label.pack(expand=True)

        footer = (
            "Esc exits final block and returns home"
            if on_complete_exit
            else "Esc closes this screen (session continues)"
        )
        hint = tk.Label(
            countdown_window,
            text=footer,
            font=("Courier", 18),
            fg="#e8f5e9",
            bg="#66a189",
        )
        hint.pack(side=tk.BOTTOM, pady=40)

        def update_countdown(remaining):
            if remaining >= 0:
                minutes = remaining // 60
                sec = remaining % 60
                label.config(text=f"{minutes:02d}:{sec:02d}")
                countdown_window.after(1000, update_countdown, remaining - 1)
            else:
                countdown_window.destroy()
                if on_complete_exit:
                    self.root.quit()

        update_countdown(seconds)

        def on_escape(_event):
            countdown_window.destroy()
            if on_complete_exit:
                self.start_button.config(state="normal")
                self.countdown_frame.pack_forget()
                self.initial_frame.pack()

        countdown_window.bind("<Escape>", on_escape)


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Custom.TButton",
        width=22,
        padding=5,
        foreground="white",
        background="#66a189",
        font=("Courier", 16, "bold", "underline"),
        relief="flat",
        focusthickness=3,
        focuscolor="none",
    )
    style.configure(
        "Custom.TLabel",
        foreground="white",
        background="#66a189",
        font=("Courier", 32),
        padding=5,
    )
    style.map(
        "Custom.TButton",
        background=[("active", "#66a189"), ("pressed", "#66a189")],
        foreground=[("pressed", "white"), ("active", "#f1db77")],
    )
    app = CountdownApp(root)
    root.mainloop()
