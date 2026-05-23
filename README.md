# NMC-SOFTWARE

Basic desktop app for opening and previewing `.inp` files.

## Run

```bash
python app.py
```

## Example template file

- `/home/runner/work/NMC-SOFTWARE/NMC-SOFTWARE/example.inp` is included in the working folder as a ready-to-use template dataset.
- The app loads this file as the template preview by default.

## Current features

- `file` menu with:
  - `open inp` (implemented)
  - `open ideal` (placeholder)
- More polished interface:
  - title/header section
  - quick action buttons
  - split layout with template panel + parsed data preview panel
- Built-in INP template (modeled after the shared example style) shown in the main window
- Opens `.inp`/text files and shows file text in a styled child preview window
- Parses numeric rows and stores values in this order:
  1. Center frequency
  2. Bandwidth
  3. Q value
  4. ReVAR
  5. Minp
  6. Mout
  7. PHimp (inch)
  8. PHout (inch)