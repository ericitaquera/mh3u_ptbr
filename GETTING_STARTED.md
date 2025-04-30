# 🧪 Getting Started with mh3u_ptbr

This guide walks you through setting up your environment and preparing the game's assets to begin localization.

> 📄 See [DISCLAIMER.md](DISCLAIMER.md) for important legal and usage terms.

---

## 🚀 Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mh3u_ptbr.git
cd mh3u_ptbr
```

---

### 2. Run Environment Setup

This script creates the required directory structure and sets your working environment variables.

```powershell
. .\env.ps1
```

> ⚠️ Use `. .\env.ps1` (dot-space) to apply variables in your current session.

---

### 3. Get the Game's `romfs.bin`

Extract it from your legally owned copy of Monster Hunter 3 Ultimate using **GodMode9**:

- Mount your MH3U game in GodMode9
- Select `NCCH image options` → `Mount image to drive`
- Inside, locate `romfs.bin` and copy it to `SD:/gm9/out/`
- Move the file to: `C:\temp\mh3u_ptbr\romfs.bin`

---

### 4. Extract the ROMFS

```powershell
.\scripts\extract_romfs.ps1
```

This unpacks the contents of `romfs.bin` into the `romfs_extracted/` folder for further processing.

---

### 5. Search for Text Inside GMD Files

Use the provided script to locate specific strings in `.gmd` files:

```powershell
.\scripts\find_in_gmd.ps1
```

You'll be prompted to enter a string. The script will list all `.gmd` files containing it.

---

## 📂 Directory Overview

For detailed structure and folder descriptions, refer to `README.md`.

---

## 📝 Notes

- All support scripts are stored under `/scripts/`
- Tools like `ctrtool.exe` go under `/tools/`
- You must re-run `env.ps1` each time you open a new PowerShell session

---

Happy hacking! 🎮

