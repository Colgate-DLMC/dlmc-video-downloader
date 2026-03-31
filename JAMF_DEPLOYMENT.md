# JAMF Deployment Guide — DLMC Video Downloader

This guide covers:
1. Building a fresh `.pkg`
2. Uploading to JAMF Pro and scoping a policy
3. Removing a previously deployed version (old `dlmc-dlp.app`)

---

## Step 1: Build the `.pkg`

On your Mac build machine (Apple Silicon / arm64):

```bash
cd /path/to/dlmc-video-downloader
chmod +x build.sh
./build.sh
```

On success the script outputs:
```
App:     dist/dlmc-video-downloader.app
Package: dlmc-video-downloader.pkg
```

The `.pkg` installs the app to `/Applications/dlmc-video-downloader.app` and sets
`BundleIsRelocatable = false`, so JAMF will always drop it in `/Applications`.

---

## Step 2: Upload the PKG to JAMF Pro

1. Log into your **JAMF Pro** console.
2. Go to **Settings → Computer Management → Packages**.
3. Click **+ New**.
4. Set **Display Name** to `DLMC Video Downloader 1.2`.
5. Under **Filename**, upload `dlmc-video-downloader.pkg`.
6. Leave **Category** and **Priority** at defaults (or set as per your org's standards).
7. Click **Save**.

---

## Step 3: Create a Deployment Policy

1. Go to **Computers → Policies → + New**.
2. **General tab:**
   - Name: `Install DLMC Video Downloader`
   - Trigger: `Recurring Check-in` (or `Self Service` if you want user-initiated)
   - Execution Frequency: `Once per computer`
3. **Packages tab:**
   - Click **Configure**, then **+ Add**.
   - Select `DLMC Video Downloader 1.2`.
   - Action: `Install`.
4. **Scope tab:**
   - Add the target computers or smart groups.
5. Click **Save**.

JAMF will push the `.pkg` on the next check-in for scoped machines.

---

## Step 4: Verify Installation

After the policy runs, confirm via:

- **JAMF Pro → Computers → [machine] → Management History** — look for the policy in the completed list.
- SSH or Terminal on a test machine: `ls /Applications/dlmc-video-downloader.app`

---

## Step 5: Remove the Old `dlmc-dlp` App (if deployed)

If the previous version (`dlmc-dlp.app`, bundle ID `com.dlmc.dlmc-dlp`) was deployed
to managed machines, run the JAMF removal script below.

### Create a JAMF Script Policy

1. Go to **Settings → Computer Management → Scripts → + New**.
2. **General tab:**
   - Display Name: `Remove dlmc-dlp (legacy)`
3. **Script tab:** Paste the contents of `scripts/remove-dlmc-dlp.sh` (included in this repo).
4. Click **Save**.

### Create a Policy to Run It

1. **Computers → Policies → + New**.
2. **General tab:**
   - Name: `Remove Legacy dlmc-dlp`
   - Trigger: `Recurring Check-in`
   - Execution Frequency: `Once per computer`
3. **Scripts tab:** Add `Remove dlmc-dlp (legacy)`.
4. **Scope tab:** Target the same machines that received the old package.
5. Click **Save**.

> **Tip:** Run this removal policy *before or alongside* the new install policy to avoid
> having both versions present simultaneously.

---

## Package Identifier Reference

| Version | Bundle ID | App Path |
|---------|-----------|----------|
| New (1.2+) | `com.dlmc.video-downloader` | `/Applications/dlmc-video-downloader.app` |
| Legacy | `com.dlmc.dlmc-dlp` | `/Applications/dlmc-dlp.app` |
