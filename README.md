# 🇧🇷 Monster Hunter 3 Ultimate - PT-BR Localization

![Built on Windows... unwillingly](https://img.shields.io/badge/Built%20on-Windows%20%F0%9F%98%B5-blue)

**mh3u_ptbr** is a fan-made project to localize the Nintendo 3DS game *Monster Hunter 3 Ultimate* into Brazilian Portuguese.  
This repository contains scripts, tools, and documentation to extract, translate, and rebuild game assets.

> 🖤 *Made with heartache on Windows* — a Linux user’s sacrifice for compatibility.

---

## 📦 Project Structure

| Folder / Script            | Description                                               |
|---------------------------|-----------------------------------------------------------|
| `env.bat`                 | Sets environment variables for use across scripts         |
| `scripts/`                | Automation scripts for extraction, translation, and packing |
| `tools/`                  | Tools like `arc_extractor`, (optionally Kuriimu2)         |
| `original/`               | Extracted game assets (.arc, .gmd, etc.)                  |
| `translated/`             | Edited `.txt` translation files                           |
| `logs/`                   | Logs generated during pipeline execution                  |
| `README.md`               | Project documentation                                     |

---

## 🛠️ Requirements

- **Windows OS**  
  Project developed and tested on Windows 10+ for compatibility with required tools

- **Python 3.x** (mandatory)  
  Required for scripting GMD text extraction, processing, and batch automation

- [`arc_extractor`](https://github.com/username/arc_extractor)  
  Tool for unpacking and repacking `.arc` files from the ROMFS

- [Visual Studio Code](https://code.visualstudio.com/)  
  Recommended text editor for translating `.txt` files

- [GodMode9](https://github.com/d0k3/GodMode9)  
  To extract the ROMFS from a physical cartridge or CIA file on a real 3DS

- [Kuriimu2](https://github.com/FanTranslatorsInternational/Kuriimu2) *(optional)*  
  GUI tool that can help explore `.arc` and `.gmd` files during translation

---

## 🚀 How It Works

1. **Extract** the ROMFS using GodMode9
2. **Unpack** `.arc` containers using `arc_extractor`
3. **Extract and convert** `.gmd` files to `.txt` using Python scripts
4. **Translate** the `.txt` files manually (VSCode recommended)
5. **Repack** translated `.txt` into `.gmd`, then back into `.arc`
6. **Rebuild** the ROMFS and test your changes in Citra or on a real console

---

## 🌍 Translation Guidelines

- Maintain structure and tags such as `<SUB 0>`, `<PAGE>`, etc.
- Respect in-game formatting and avoid text overflow
- Aim to preserve the original tone and intent of characters/dialogue
- Prefer natural Brazilian Portuguese phrasing over literal translations

---

## 💡 Optional Tools

- **Kuriimu2** can be useful for previewing ARC/GMD contents visually  
- **Notepad++** sometimes faster and easier than VS Code for certain tasks

---

## 📜 Legal Notice

This is a **non-commercial fan translation** project not affiliated with Capcom, Nintendo, or any official publisher.  
This repository contains **no copyrighted game content**.

You must own a legal copy of *Monster Hunter 3 Ultimate* to use this pipeline.

---

## 💬 Credits

- **Project Lead:** [@ericitaquera](https://github.com/ericitaquera)  
- **Tools Used:** arc_extractor, Python 3, GodMode9, Visual Studio Code  
- **Special Thanks:** 🙌 
  To everyone who contributed — knowingly or not — to the ROM hacking and fan translation scene:  co
  toolmakers, reverse engineers, tutorial writers, testers, and community sharers.  
  *"If I have seen further, it is by standing on the shoulders of giants."* — Isaac Newton   
