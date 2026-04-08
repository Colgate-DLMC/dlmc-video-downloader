# DLMC Video Downloader

A simple macOS app for downloading videos from YouTube and other platforms.
Built by the Colgate University Digital Learning & Media Center.

---

## What It Does

DLMC Video Downloader gives you a clean, no-fuss interface to download videos from YouTube and hundreds of other sites — no browser extensions, no command line required.

Paste a URL, choose a folder, and download. That's it.

---

## Download

Grab the latest `.pkg` installer from the [Releases](../../releases) page.

- macOS Apple Silicon (arm64) only
- Installs to `/Applications`
- No dependencies required — everything is bundled

---

## How to Use

1. Download and run the `.pkg` installer
2. Open **DLMC Video Downloader** from `/Applications`
3. Paste a video URL into the URL field
4. Click **Choose Output Folder** to pick where to save
5. Click **Download**

Progress is shown in the status window. Videos are saved as `.mp4`.

---

## macOS Security Warning

Because this app is not yet signed with an Apple Developer certificate, macOS Gatekeeper may block it on first launch with a message like *"cannot be opened because the developer cannot be verified."*

**To open it anyway:**

1. Open **Finder** and go to `/Applications`
2. **Right-click** (or Control-click) on **DLMC Video Downloader**
3. Select **Open** from the menu
4. Click **Open** again in the dialog that appears

You only need to do this once — after that, the app opens normally.

---

## What's Inside

This app bundles and wraps two open-source tools:

| Tool | Purpose | License |
|------|---------|---------|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Video downloading | Unlicense |
| [ffmpeg](https://ffmpeg.org) | Audio/video merging | LGPL v2.1 |

DLMC Video Downloader does not implement any download or media processing functionality itself. All of that is handled by these upstream projects.

---

## Supported Sites

Anywhere yt-dlp works — YouTube, Vimeo, Twitter/X, Instagram, and [many more](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

---

## Acceptable Use

Please read the [Acceptable Use Policy](ACCEPTABLE_USE.md) before using this tool.

In short: only download content you have the right to download. This tool is provided as-is — you are responsible for how you use it.

---

## License

[MIT](LICENSE) — © 2026 Colgate-DLMC
