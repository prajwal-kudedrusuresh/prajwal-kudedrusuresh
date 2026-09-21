# Setup

1. Create a repo named **exactly** your GitHub username — e.g. `prajwal-kudedrusuresh/prajwal-kudedrusuresh`.
   GitHub treats this special repo's README as your profile page.
2. Drop all these files in at the repo root (keep the folder structure: `assets/`, `scripts/`, `.github/workflows/`).
3. Push. The banner (`assets/dark.svg` / `assets/light.svg`) already reflects your photo — no action needed.
4. To update the banner later: replace `assets/photo.png` with a new photo (or edit the `LINES` / `CONTACT`
   text inside `scripts/ascii_to_svg.py`) and push — the GitHub Action rebuilds both SVGs automatically.
5. The stats badges in the README (`github-readme-stats.vercel.app`) are already pointed at your username
   and need no setup — they render live on every page view.
6. Optional: replace the two placeholder repo names under "pinned_projects" with your real repo names
   (or delete that section and use GitHub's native "Pin repositories" feature instead).

## Manually regenerating the banner locally
```bash
pip install -r requirements.txt
python3 scripts/ascii_to_svg.py --photo assets/photo.png --out-dir assets
```
