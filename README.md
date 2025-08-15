# EXE File Finder

A simple Python-based GUI application for scanning a selected folder and listing all `.exe` files found.  
It also logs any permission errors encountered during the scan and saves results as text files.

## Features

- **User-friendly GUI** built with Tkinter
- **Non-blocking scan** using threading (keeps the UI responsive)
- **Permission error handling** for inaccessible directories or files
- **Automatic result saving** with timestamped filenames
- **Separate error log** if any permission issues occur
- Works both as a `.py` script and as a frozen `.exe` application

---

## Requirements

- **Python 3.6+**
- Standard library modules only (`tkinter`, `os`, `threading`, `datetime`, `sys`)

> **Note:** `tkinter` comes pre-installed with most Python distributions,  
> but on some Linux systems you may need to install it manually:
> ```bash
> sudo apt-get install python3-tk
> ```

---

## How to Run

### Option 1 — Run as a Python Script
1. Save `exe_finder.py` to your desired folder.
2. Open a terminal or command prompt in that folder.
3. Run:
   ```bash
   python exe_finder.py
