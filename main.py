import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
import os
import sys
import threading
import shutil

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

_bin_ext = ".exe" if sys.platform == "win32" else ""

bundled_yt_dlp = os.path.join(base_dir, "bin", f"yt-dlp{_bin_ext}")
ffmpeg_path    = os.path.join(base_dir, "bin", f"ffmpeg{_bin_ext}")

# User-local yt-dlp (writable, self-updatable)
if sys.platform == "win32":
    _app_support = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")),
                                "DLMC Video Downloader", "bin")
else:
    _app_support = os.path.join(
        os.path.expanduser("~"), "Library", "Application Support",
        "DLMC Video Downloader", "bin"
    )
local_yt_dlp = os.path.join(_app_support, f"yt-dlp{_bin_ext}")

# Seed the local copy from the bundled binary if it doesn't exist
if not os.path.isfile(local_yt_dlp):
    os.makedirs(_app_support, exist_ok=True)
    if os.path.isfile(bundled_yt_dlp):
        shutil.copy2(bundled_yt_dlp, local_yt_dlp)
        if sys.platform != "win32":
            os.chmod(local_yt_dlp, 0o755)

# Prefer the local copy; fall back to bundled
yt_dlp_path = local_yt_dlp if os.path.isfile(local_yt_dlp) else bundled_yt_dlp
ffmpeg_available = os.path.exists(ffmpeg_path)
logo_path = os.path.join(base_dir, "logo.png")

# ---------------------------------------------------------------------------
# Root window & shared state
# ---------------------------------------------------------------------------
root = tk.Tk()
root.title("DLMC Video Downloader")
root.geometry("700x550")
root.resizable(True, True)
root.minsize(600, 450)

output_path = tk.StringVar()
all_download_buttons = []

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def build_command(url, output_dir, mode="quick", resolution="best",
                  audio_only=False, subtitles=False):
    """Build the yt-dlp command list."""
    if audio_only:
        command = [
            yt_dlp_path,
            "-f", "bestaudio",
            "--extract-audio", "--audio-format", "mp3",
            "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
            url,
        ]
    else:
        res_map = {
            "best":       "bestvideo+bestaudio",
            "720p":       "bestvideo[height<=720]+bestaudio",
            "1080p":      "bestvideo[height<=1080]+bestaudio",
            "2K (1440p)": "bestvideo[height<=1440]+bestaudio",
            "4K (2160p)": "bestvideo[height<=2160]+bestaudio",
        }
        fmt = res_map.get(resolution, "bestvideo+bestaudio")

        if mode == "quick" and not ffmpeg_available:
            command = [
                yt_dlp_path,
                "-f", "best[ext=mp4]/best",
                "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
                url,
            ]
        else:
            command = [
                yt_dlp_path,
                "-f", fmt,
                "--merge-output-format", "mp4",
                "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
                url,
            ]

    if ffmpeg_available:
        command.insert(1, "--ffmpeg-location")
        command.insert(2, ffmpeg_path)

    if subtitles and not audio_only:
        command.extend(["--write-subs", "--sub-langs", "en.*,en",
                         "--convert-subs", "srt"])

    return command


def append_to_status(status_box, msg):
    status_box.configure(state='normal')
    status_box.insert(tk.END, msg)
    status_box.see(tk.END)
    status_box.configure(state='disabled')


def set_download_state(in_progress):
    state = "disabled" if in_progress else "normal"
    for btn in all_download_buttons:
        btn.configure(state=state)


def run_single_download(url, output_dir, status_box, **kwargs):
    command = build_command(url, output_dir, **kwargs)

    if kwargs.get("mode") == "quick":
        if ffmpeg_available:
            append_to_status(status_box,
                             "Using ffmpeg to merge video + audio into .mp4\n")
        else:
            append_to_status(status_box,
                             "ffmpeg not available — downloading best single .mp4 stream\n")

    append_to_status(status_box, f"Starting download for: {url}\n\n")

    popen_kwargs = {}
    if sys.platform == "win32":
        popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, **popen_kwargs
        )
        for line in iter(process.stdout.readline, ''):
            append_to_status(status_box, line)
        process.stdout.close()
        process.wait()

        if process.returncode == 0:
            append_to_status(status_box, "\n✅ Download completed successfully.\n")
        else:
            append_to_status(status_box,
                             f"\n❌ Download failed with exit code {process.returncode}.\n")
    except Exception as e:
        append_to_status(status_box, f"\n⚠️ Unexpected error: {str(e)}\n")


def choose_directory():
    folder = filedialog.askdirectory()
    if folder:
        output_path.set(folder)


def validate_inputs(url, output_dir):
    if not url:
        messagebox.showerror("Missing URL", "Please enter a YouTube or video URL.")
        return False
    if not output_dir:
        messagebox.showerror("Missing Output Folder",
                             "Please choose an output folder.")
        return False
    return True


def clear_status(status_box):
    status_box.configure(state='normal')
    status_box.delete('1.0', tk.END)
    status_box.configure(state='disabled')


def show_help():
    win = tk.Toplevel(root)
    win.title("DLMC Video Downloader Help")
    win.geometry("560x500")
    win.resizable(True, True)
    win.minsize(400, 320)

    text = scrolledtext.ScrolledText(win, wrap='word', state='normal',
                                     padx=12, pady=8)
    text.pack(fill='both', expand=True, padx=10, pady=(10, 0))

    help_text = """\
DLMC Video Downloader — Help

OVERVIEW
DLMC Video Downloader is a graphical interface for yt-dlp, a powerful video
downloading tool that supports thousands of sites including YouTube, Vimeo,
Twitter/X, SoundCloud, and many more.

QUICK DOWNLOAD
Paste a single video URL and click Download to grab the best available quality.
  • If ffmpeg is available, video and audio streams are merged into an .mp4 file.
  • If ffmpeg is unavailable, the best single-file .mp4 stream is downloaded.

ADVANCED OPTIONS
Format:
  • Video & Audio — downloads and merges the best video and audio streams.
  • Audio Only (MP3) — extracts audio and saves it as an .mp3 file.

Resolution:
  • best — highest resolution available (default).
  • 720p, 1080p, 2K (1440p), 4K (2160p) — caps the download at that height.
    Note: ffmpeg is required to merge separate video and audio streams.

Subtitles:
  • When checked, English subtitles are downloaded as a separate .srt file
    alongside the video. (Requires ffmpeg.)

DOWNLOAD MULTIPLE
Paste multiple URLs — one per line — and click Download All.
Downloads run sequentially. Progress for each is shown in the status area.

OUTPUT FOLDER
All tabs share the same output folder. Click "Choose Output Folder" to select
where downloaded files are saved. The path is shown in red when selected.

UPDATING yt-dlp
DLMC Video Downloader automatically checks for a yt-dlp update each time the
app launches. The result briefly appears in the title bar for a few seconds.
You can also update manually at any time by clicking "Update yt-dlp".

TIPS
  • If a download fails, check that the URL is publicly accessible and that
    the site is supported by yt-dlp.
  • For best quality, ffmpeg must be bundled with the app — it is needed to
    merge separate video and audio streams into a single .mp4.
  • Downloaded files are named automatically using the video's title.
"""
    text.insert('1.0', help_text)
    text.configure(state='disabled')

    ttk.Button(win, text="Close", command=win.destroy).pack(pady=8)
    win.transient(root)
    win.grab_set()


def show_about():
    messagebox.showinfo(
        "About DLMC Video Downloader",
        "DLMC Video Downloader\n"
        "Version 3.1\n\n"
        "A graphical interface for yt-dlp + ffmpeg.\n"
        "Download videos from YouTube and thousands\n"
        "of other sites.\n\n"
        "Powered by yt-dlp (open source)"
    )


def _run_yt_dlp_update(callback):
    def _worker():
        try:
            proc = subprocess.run(
                [yt_dlp_path, "--update"],
                capture_output=True, text=True, timeout=60,
            )
            output = (proc.stdout + proc.stderr).strip()
            if proc.returncode == 0:
                if "up to date" in output.lower() or "up-to-date" in output.lower():
                    callback("yt-dlp is up to date")
                else:
                    callback("yt-dlp updated")
            else:
                callback("yt-dlp update failed")
        except Exception:
            callback("yt-dlp update failed")
    threading.Thread(target=_worker, daemon=True).start()

# ---------------------------------------------------------------------------
# Tab action functions
# ---------------------------------------------------------------------------

def quick_download():
    url = quick_url_entry.get().strip()
    output_dir = output_path.get()
    if not validate_inputs(url, output_dir):
        return
    clear_status(quick_status)
    set_download_state(True)

    def _run():
        try:
            run_single_download(url, output_dir, quick_status, mode="quick")
        finally:
            set_download_state(False)

    threading.Thread(target=_run, daemon=True).start()


def advanced_download():
    url = adv_url_entry.get().strip()
    output_dir = output_path.get()
    if not validate_inputs(url, output_dir):
        return
    clear_status(adv_status)
    set_download_state(True)

    audio_only = adv_audio_only.get()
    resolution = adv_resolution.get()
    subtitles  = adv_subtitles.get()

    def _run():
        try:
            run_single_download(url, output_dir, adv_status,
                                mode="advanced", resolution=resolution,
                                audio_only=audio_only, subtitles=subtitles)
        finally:
            set_download_state(False)

    threading.Thread(target=_run, daemon=True).start()


def multi_download():
    raw = multi_url_text.get("1.0", tk.END).strip()
    output_dir = output_path.get()

    urls = [u.strip() for u in raw.splitlines() if u.strip()]
    if not urls:
        messagebox.showerror("Missing URLs", "Please enter at least one URL.")
        return
    if not output_dir:
        messagebox.showerror("Missing Output Folder",
                             "Please choose an output folder.")
        return

    clear_status(multi_status)
    set_download_state(True)

    def _run():
        try:
            total = len(urls)
            for i, url in enumerate(urls, 1):
                append_to_status(multi_status,
                                 f"--- Downloading {i} of {total} ---\n")
                run_single_download(url, output_dir, multi_status, mode="quick")
                append_to_status(multi_status, "\n")
            append_to_status(multi_status,
                             f"=== All {total} downloads finished ===\n")
        finally:
            set_download_state(False)

    threading.Thread(target=_run, daemon=True).start()


def toggle_resolution(*_args):
    if adv_audio_only.get():
        adv_resolution_combo.configure(state="disabled")
    else:
        adv_resolution_combo.configure(state="readonly")

# ---------------------------------------------------------------------------
# Menu bar
# ---------------------------------------------------------------------------
menubar = tk.Menu(root)
help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="Help", command=show_help)
help_menu.add_separator()
help_menu.add_command(label="About", command=show_about)
menubar.add_cascade(label="Help", menu=help_menu)
root.config(menu=menubar)

# ---------------------------------------------------------------------------
# Logo
# ---------------------------------------------------------------------------
try:
    logo_image = tk.PhotoImage(file=logo_path)
    w = logo_image.width()
    if w > 300:
        factor = w // 300
        if factor >= 2:
            logo_image = logo_image.subsample(factor)
    logo_label = ttk.Label(root, image=logo_image)
    logo_label.pack(pady=(10, 5))
except Exception:
    pass  # App works without logo

# ---------------------------------------------------------------------------
# Shared output folder row
# ---------------------------------------------------------------------------
folder_frame = ttk.Frame(root)
folder_frame.pack(fill="x", padx=15, pady=(0, 5))

ttk.Button(folder_frame, text="Choose Output Folder",
           command=choose_directory).pack(side="left")
ttk.Label(folder_frame, textvariable=output_path,
          foreground="red").pack(side="left", padx=(10, 0), fill="x", expand=True)


def _manual_update_yt_dlp():
    update_btn.configure(state="disabled")

    def _on_result(msg):
        def _show():
            messagebox.showinfo("yt-dlp Update", msg)
            update_btn.configure(state="normal")
        root.after(0, _show)

    _run_yt_dlp_update(_on_result)


update_btn = ttk.Button(folder_frame, text="Update yt-dlp",
                        command=_manual_update_yt_dlp)
update_btn.pack(side="right")

# ---------------------------------------------------------------------------
# Notebook (tabs)
# ---------------------------------------------------------------------------
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

# ======================= Tab 1: Quick Download ============================
quick_tab = ttk.Frame(notebook)
notebook.add(quick_tab, text="Quick Download")

ttk.Label(quick_tab, text="Video URL:").pack(pady=(10, 0))
quick_url_entry = ttk.Entry(quick_tab, width=70)
quick_url_entry.pack(pady=5, padx=10)

quick_dl_btn = ttk.Button(quick_tab, text="Download", command=quick_download)
quick_dl_btn.pack(pady=5)
all_download_buttons.append(quick_dl_btn)

ttk.Label(quick_tab, text="Status:").pack(pady=(5, 0))
quick_status = scrolledtext.ScrolledText(
    quick_tab, width=80, height=12, state='disabled', wrap='word')
quick_status.pack(padx=10, pady=(0, 10), fill="both", expand=True)

# ======================= Tab 2: Advanced Options ==========================
adv_tab = ttk.Frame(notebook)
notebook.add(adv_tab, text="Advanced Options")

ttk.Label(adv_tab, text="Video URL:").pack(pady=(10, 0))
adv_url_entry = ttk.Entry(adv_tab, width=70)
adv_url_entry.pack(pady=5, padx=10)

format_frame = ttk.LabelFrame(adv_tab, text="Format")
format_frame.pack(fill="x", padx=15, pady=5)

adv_audio_only = tk.BooleanVar(value=False)
ttk.Radiobutton(format_frame, text="Video & Audio",
                variable=adv_audio_only, value=False,
                command=toggle_resolution).pack(side="left", padx=10, pady=5)
ttk.Radiobutton(format_frame, text="Audio Only (MP3)",
                variable=adv_audio_only, value=True,
                command=toggle_resolution).pack(side="left", padx=10, pady=5)

res_frame = ttk.LabelFrame(adv_tab, text="Resolution")
res_frame.pack(fill="x", padx=15, pady=5)

adv_resolution = tk.StringVar(value="best")
adv_resolution_combo = ttk.Combobox(
    res_frame, textvariable=adv_resolution, state="readonly",
    values=["best", "720p", "1080p", "2K (1440p)", "4K (2160p)"],
    width=20)
adv_resolution_combo.pack(padx=10, pady=5, anchor="w")

adv_subtitles = tk.BooleanVar(value=False)
ttk.Checkbutton(adv_tab, text="Download English subtitles (.srt)",
                variable=adv_subtitles).pack(padx=15, pady=5, anchor="w")

adv_dl_btn = ttk.Button(adv_tab, text="Download", command=advanced_download)
adv_dl_btn.pack(pady=5)
all_download_buttons.append(adv_dl_btn)

ttk.Label(adv_tab, text="Status:").pack(pady=(5, 0))
adv_status = scrolledtext.ScrolledText(
    adv_tab, width=80, height=8, state='disabled', wrap='word')
adv_status.pack(padx=10, pady=(0, 10), fill="both", expand=True)

# ======================= Tab 3: Download Multiple =========================
multi_tab = ttk.Frame(notebook)
notebook.add(multi_tab, text="Download Multiple")

ttk.Label(multi_tab, text="Paste URLs (one per line):").pack(pady=(10, 0))
multi_url_text = scrolledtext.ScrolledText(
    multi_tab, width=70, height=5, wrap='word')
multi_url_text.pack(padx=10, pady=5, fill="x")

multi_dl_btn = ttk.Button(multi_tab, text="Download All",
                           command=multi_download)
multi_dl_btn.pack(pady=5)
all_download_buttons.append(multi_dl_btn)

ttk.Label(multi_tab, text="Status:").pack(pady=(5, 0))
multi_status = scrolledtext.ScrolledText(
    multi_tab, width=80, height=8, state='disabled', wrap='word')
multi_status.pack(padx=10, pady=(0, 10), fill="both", expand=True)

# ---------------------------------------------------------------------------
# Auto-update yt-dlp on launch
# ---------------------------------------------------------------------------
DEFAULT_TITLE = "DLMC Video Downloader"


def _auto_update_on_launch():
    def _on_result(msg):
        def _show_title():
            root.title(f"{DEFAULT_TITLE} — {msg}")
            root.after(5000, lambda: root.title(DEFAULT_TITLE))
        root.after(0, _show_title)
    _run_yt_dlp_update(_on_result)


root.after(500, _auto_update_on_launch)

# ---------------------------------------------------------------------------
root.mainloop()
