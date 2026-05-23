# NMC-SOFTWARE

Basic desktop app for opening and previewing `.inp` files.

## Run

```bash
python app.py
```

## Current features

- `File` menu with:
  - `Open INP` (implemented)
  - `Open Ideal` (placeholder)
- Opens `.inp`/text files and shows the file text in a child window
- Parses numeric rows and stores values in this order:
  1. Center frequency
  2. Bandwidth
  3. Q value
  4. ReVAR
  5. Minp
  6. Mout
  7. PHimp (inch)
  8. PHout (inch)