"""InstaPDF arayüzü: linki yapıştır, 'PDF Yap'a bas."""
import os
import queue
import re
import threading
import tkinter as tk
from tkinter import ttk

from instapdf import OUT_DIR, InstaPdfError, make_pdf

IG_LINK = re.compile(r"instagram\.com/(?:[^/]+/)?(?:p|reel|tv)/")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("InstaPDF")
        self.geometry("560x420")
        self.minsize(460, 360)
        self.events = queue.Queue()
        self.last_pdf = None

        frm = ttk.Frame(self, padding=14)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Instagram post linki:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        row = ttk.Frame(frm)
        row.pack(fill="x", pady=(4, 8))
        self.url = tk.StringVar()
        entry = ttk.Entry(row, textvariable=self.url, font=("Segoe UI", 10))
        entry.pack(side="left", fill="x", expand=True, ipady=3)
        entry.bind("<Return>", lambda e: self.start())
        ttk.Button(row, text="Yapıştır", command=self.paste).pack(side="left", padx=(6, 0))

        login_row = ttk.Frame(frm)
        login_row.pack(fill="x", pady=(0, 8))
        ttk.Label(login_row, text="Oturum (opsiyonel):").pack(side="left")
        self.login = tk.StringVar()
        ttk.Entry(login_row, textvariable=self.login, width=22).pack(side="left", padx=6)

        self.go = ttk.Button(frm, text="PDF Yap", command=self.start)
        self.go.pack(fill="x", ipady=6)

        self.bar = ttk.Progressbar(frm, mode="determinate")
        self.bar.pack(fill="x", pady=8)

        self.log = tk.Text(frm, height=9, state="disabled", font=("Consolas", 9), wrap="word")
        self.log.pack(fill="both", expand=True)

        btns = ttk.Frame(frm)
        btns.pack(fill="x", pady=(8, 0))
        self.open_btn = ttk.Button(btns, text="PDF'i Aç", command=self.open_pdf, state="disabled")
        self.open_btn.pack(side="left")
        ttk.Button(btns, text="Klasörü Aç", command=self.open_folder).pack(side="left", padx=6)

        entry.focus_set()
        self.paste(only_instagram=True)
        self.after(100, self.poll)

    def paste(self, only_instagram=False):
        try:
            text = self.clipboard_get().strip()
        except tk.TclError:
            return
        if not only_instagram or IG_LINK.search(text):
            self.url.set(text)

    def write(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start(self):
        url = self.url.get().strip()
        if not url:
            self.write("Önce bir link yapıştır.")
            return
        self.go.configure(state="disabled")
        self.open_btn.configure(state="disabled")
        self.bar.configure(value=0)
        self.write("-" * 40)
        login = self.login.get().strip() or None
        threading.Thread(target=self.work, args=(url, login), daemon=True).start()

    def work(self, url, login):
        try:
            pdf = make_pdf(url, login=login, progress=lambda m: self.events.put(("msg", m)))
            self.events.put(("done", pdf))
        except InstaPdfError as e:
            self.events.put(("error", str(e)))
        except Exception as e:
            self.events.put(("error", f"Beklenmeyen hata: {e}"))

    def poll(self):
        while not self.events.empty():
            kind, val = self.events.get()
            if kind == "msg":
                self.write(val)
                m = re.match(r"\s*(\d+)/(\d+)$", val)
                if m:
                    self.bar.configure(value=int(m[1]) * 100 / int(m[2]))
            elif kind == "done":
                self.last_pdf = val
                self.bar.configure(value=100)
                self.go.configure(state="normal")
                self.open_btn.configure(state="normal")
                self.url.set("")
            elif kind == "error":
                self.write("HATA: " + val)
                self.go.configure(state="normal")
        self.after(100, self.poll)

    def open_pdf(self):
        if self.last_pdf and self.last_pdf.exists():
            os.startfile(self.last_pdf)

    def open_folder(self):
        OUT_DIR.mkdir(exist_ok=True)
        os.startfile(OUT_DIR)


if __name__ == "__main__":
    App().mainloop()
