# Lunar File Invasion

- **Writeup:** [lunar-file-invasion-writeup.md](lunar-file-invasion-writeup.md)

## Files

- HTML templates: `admin_*.html`, `twofa*.html`, `lunar_files_template.html`, `admin_help*.html`
- `cookies.txt`
- `database.db`

## Summary

LFI via weak blacklist on download route; double-encoding traversal to pull templates and DB, recover 2FA PIN, and read flag.
