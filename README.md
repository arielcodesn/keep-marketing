# keep-marketing

Hand-off folder between you and Claude for Keep – Photo & Video Cleaner hamster reels.

| Folder | Who adds files | What goes in it |
|---|---|---|
| `base-clips/` | You | Hamster emotion clips, ideally on flat green screen. Name them by emotion: `shocked.mp4`, `laughing.mp4`, `dance.mp4`, `strut.mp4`, … |
| `backgrounds/` | You | Background photos that are free for commercial use (Unsplash/Pexels). Name them by place: `beach-sunset.jpg`, `airport.jpg`, … |
| `reels/` | Claude | Finished 9:16 reels, named `keep_reel_<nn>_<background>_<joke>.mp4` |

Upload with **Add file → Upload files** on github.com (up to 25 MB per file).

Green-screen tips: flat, evenly lit green with no shadows on the backdrop, the floor the same green, a little gap around the hamster, minimal motion blur.

## Auto-sync to Google Drive

`.github/workflows/sync-reels-to-drive.yml` copies new files in `reels/` into Drive → Keep - Marketing → **Hamster Reels - Ready to Post** on every push. It only copies; it never deletes anything in Drive.

One-time setup:
1. Install rclone on your computer (https://rclone.org/install/).
2. Run `rclone config` → `n` (new remote) → name it `gdrive` → storage `drive` → leave client id/secret blank → scope `1` (full access) → leave the rest at defaults → sign in with the Google account that owns the Keep - Marketing folder.
3. Run `rclone config show gdrive` and copy everything it prints, including the `[gdrive]` line.
4. In this repo: **Settings → Secrets and variables → Actions → New repository secret**, name `RCLONE_CONFIG`, paste, save.
5. **Actions → Sync reels to Google Drive → Run workflow** to copy the existing reels.
