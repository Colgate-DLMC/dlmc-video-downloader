import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import subprocess
import os
import threading

script_dir = os.path.dirname(os.path.abspath(__file__))
yt_dlp_path = os.path.join(script_dir, "bin", "yt-dlp")
ffmpeg_path = os.path.join(script_dir, "bin", "ffmpeg")
ffmpeg_available = os.path.exists(ffmpeg_path) and os.access(ffmpeg_path, os.X_OK)

def append_status(msg):
    status_box.configure(state='normal')
    status_box.insert(tk.END, msg)
    status_box.see(tk.END)
    status_box.configure(state='disabled')

def run_download(url, output_dir):
    if ffmpeg_available:
        command = [
            yt_dlp_path,
            "-f", "bestvideo+bestaudio",
            "--ffmpeg-location", ffmpeg_path,
            "--merge-output-format", "mp4",
            "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
            url
        ]
        append_status("Using ffmpeg to merge video + audio into .mp4\\n")
    else:
        command = [
            yt_dlp_path,
            "-f", "best[ext=mp4]/best",
            "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
            url
        ]
        append_status("ffmpeg not available — downloading best single .mp4 stream\\n")

    append_status(f"Starting download for: {url}\\n\\n")

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(process.stdout.readline, ''):
            append_status(line)
        process.stdout.close()
        process.wait()

        if process.returncode == 0:
            append_status("\\n✅ Download completed successfully.\\n")
        else:
            append_status(f"\\n❌ Download failed with exit code {process.returncode}.\\n")
    except Exception as e:
        append_status(f"\\n⚠️ Unexpected error: {str(e)}\\n")

def download_video():
    url = url_entry.get().strip()
    output_dir = output_path.get()

    if not url:
        messagebox.showerror("Missing URL", "Please enter a YouTube or video URL.")
        return

    if not output_dir:
        messagebox.showerror("Missing Output Folder", "Please choose an output folder.")
        return

    status_box.configure(state='normal')
    status_box.delete('1.0', tk.END)
    status_box.configure(state='disabled')

    threading.Thread(target=run_download, args=(url, output_dir), daemon=True).start()

def choose_directory():
    folder = filedialog.askdirectory()
    if folder:
        output_path.set(folder)

root = tk.Tk()
root.title("DLMC Video Downloader")
root.geometry("600x400")
root.resizable(True, True)
root.minsize(500, 300)

tk.Label(root, text="Video URL:").pack(pady=(10, 0))
url_entry = tk.Entry(root, width=60)
url_entry.pack(pady=5)

output_path = tk.StringVar()
tk.Button(root, text="Choose Output Folder", command=choose_directory).pack(pady=5)
tk.Label(root, textvariable=output_path, fg="red").pack()

tk.Button(root, text="Download", command=download_video).pack(pady=10)

tk.Label(root, text="Status:").pack(pady=(10, 0))
status_box = scrolledtext.ScrolledText(root, width=60, height=10, state='disabled', wrap='word')
status_box.pack(padx=10, pady=(0, 10))

root.mainloop()

