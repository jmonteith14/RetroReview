# RetroReview — Static GitHub Pages Edition

This is a browser-only adaptation of RetroReview for GitHub Pages. It does not need Python, a server, a paid host, or a credit card after publication.

## Important data note

The project snapshot available when this static version was prepared contained the 4 generation records and 34 included platform records, but **zero game records**. Those platforms are included in `data/catalogue.json`; your full current catalogue and personal reviews need to be exported from your own current SQLite database using the migration script below. I have not invented game records or included private reviews in the public website files.

## Move your existing games and reviews

1. Download this project ZIP and extract it.
2. Copy `tools/export_sqlite.py` into your **existing RetroReview project folder** (the folder containing `data/retroreview.sqlite3`). Do not replace or delete your database.
3. Open Command Prompt or Terminal in that existing project folder and run:

   ```bash
   python tools/export_sqlite.py
   ```

   The script reads the database in read-only mode. It will let you choose the account whose reviews you want to move. Choose your own account to include your ratings and reviews. It does not export password hashes or sessions. To specify paths explicitly, use `python tools/export_sqlite.py --db "data/retroreview.sqlite3" --email "you@example.com" --out "retroreview-static-import.json"`.
4. Open the static website locally (or publish it first), click **Backup / Import → Import JSON backup**, and choose `retroreview-static-import.json`.
5. The import is stored in that browser's local storage. Export a backup after importing and keep it somewhere safe.

The exporter is designed for the schema used by the RetroReview project files available for this conversion. Keep the original database untouched until you have confirmed that the exported file contains your expected number of games, releases, and reviews and that they display correctly after import.

## Publish on GitHub Pages

1. Create a new **private repository** on GitHub if you want to keep the source files private. (A Pages site itself is public by default unless your GitHub plan and organization settings support access control; do not treat a private repository as a login wall for a published site.)
2. Upload the contents of this folder to the repository root: `index.html`, `app.js`, `styles.css`, `data/`, and `tools/`.
3. In the repository, open **Settings → Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**, select your main branch and the `/(root)` folder, then save.
5. Wait for GitHub Pages to publish and open the URL it provides.

No build step is required. Keep the relative `./` paths intact so the site also works when published under a repository subpath.

## What works without a backend

- Browse and search imported games, platforms, and generations.
- Filter by generation, platform, review status, and rating; sort by title or earliest release year.
- View imported game metadata and platform-specific release/source details.
- Create, edit, and delete personal platform-specific ratings and reviews.
- View a rating distribution, including per-platform scope.
- Toggle light/dark theme.
- Export a full JSON backup and import it on another browser/device, with merge or replace options.
- Choose a random unrated game.

## What cannot work without a backend

- **No account sign-in or shared accounts.** Browser-local data is not authenticated.
- **No automatic syncing between devices or browsers.** Export on one device and import on another to transfer changes.
- **No shared multi-user review database.** Each browser profile has its own local copy.
- **No live Wikipedia importer or automatic catalogue refresh.** Importing from Wikipedia requires a server-side importer or a separate manual data refresh workflow.
- **No central database or server-side recovery.** Clearing browser site data may erase the local copy. Export regular backups.
- **No security boundary for private reviews.** Do not publish personal review data inside `data/catalogue.json` or any public repository. Import your personal JSON in the browser after deployment instead.

## Data storage

The app saves the current working data in `localStorage` for this browser origin. JSON backups include the catalogue and all local reviews. A backup is portable, but anyone who gets that file can read its reviews. Store backup files privately.
