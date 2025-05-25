# 🇧🇷 Monster Hunter 3 Ultimate - PT-BR Localization

![Built on Windows... unwillingly](https://img.shields.io/badge/Built%20on-Windows%20%F0%9F%98%B5-blue)

**mh3u_ptbr** is a fan-made project to localize the Nintendo 3DS game *Monster Hunter 3 Ultimate* into Brazilian Portuguese.  
This repository contains scripts, tools, and documentation to extract, translate, and rebuild game assets.

> 🖤 *Made with heartache on Windows* — a Linux user’s sacrifice for compatibility.

> 📄 See [DISCLAIMER.md](DISCLAIMER.md) for important legal and usage terms.

[![Watch the video](https://img.youtube.com/vi/tMayulQo3zo/maxresdefault.jpg)](https://youtu.be/tMayulQo3zo)

### [Demo do início da tradução](https://youtu.be/tMayulQo3zo)

---

## 📦 Project Structure

| Folder Name          | Purpose                                                       |
|----------------------|---------------------------------------------------------------|
| `romfs_extracted/`   | Original ROMFS files extracted from the game                  |
| `arc_extracted/`     | Unpacked `.arc` files from ROMFS                              |
| `gmd_texts/`         | Extracted `.txt` files from `.gmd` (before translation)       |
| `gmd_texts_ptbr/`    | Translated `.txt` files (Brazilian Portuguese)                |
| `gmd_repacked/`      | `.gmd` files repacked from the translated texts               |
| `arc_repacked/`      | `.arc` files rebuilt with the repacked `.gmd`                 |
| `romfs_final/`       | Final ROMFS with all translated content ready to inject       |
| `scripts/`           | Auxiliary scripts                                             |
| `tmp/`               | Temporary or intermediary files                               |
| `tools/`             | Tools like extractors, editors, packers                       |
| `logs/`              | Processing and debug logs from scripts                        |
| `images/`            | Edited image textures edited                                  |


---

## 🛠️ Requirements

- **Windows OS**  
  Project developed and tested on Windows 10+ for compatibility with required tools

- **Python 3.x** (mandatory)  
  Required for scripting GMD text extraction, processing, and batch automation

- [ctrtool](https://github.com/3DSGuy/ctrtool) (mandatory)
  Command-line tool to extract `romfs.bin` and other 3DS filesystem content.  
  Used to unpack the dumped ROMFS from *Monster Hunter 3 Ultimate* into modifiable folders.

- [GodMode9](https://github.com/d0k3/GodMode9)  
  To extract the ROMFS from a physical cartridge or CIA file on a real 3DS

- [Kuriimu2](https://github.com/FanTranslatorsInternational/Kuriimu2) *(optional)*  
  GUI tool that can help explore `.arc` and `.gmd` files during translation

- [Visual Studio Code](https://code.visualstudio.com/) *(optional)*
  Recommended text editor for translating `.txt` files

- [Notepad++](https://notepad-plus-plus.org/) *(optional)*
  Lightweight text editor useful for quick edits to `.txt` translation files.

- [HxD](https://mh-nexus.de/en/hxd/) *(optional)*  
  Powerful hex editor useful for inspecting and modifying binary `.arc` and compressed files at the byte level.
  
---

## 🚀 How It Works

1. **Extract** the ROMFS using GodMode9
2. **Unpack** `.arc` containers using using Python scripts
3. **Extract and convert** `.gmd` files to `.txt` using Python scripts
4. **Translate** the `.txt` files manually or using an IA.
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
- **Tools Used:** Python 3, GodMode9, Visual Studio Code, Notepad++, HxD Hex Editor, Citra Emulator.
- **Special Thanks:** 🙌 
  To everyone who contributed — knowingly or not — to the ROM hacking and fan translation scene:
  toolmakers, reverse engineers, tutorial writers, testers, and community sharers.  
  *"If I have seen further, it is by standing on the shoulders of giants."* — Isaac Newton   

## 🛡️ License

📘 All code and scripts in this repository are licensed under the [MIT License](LICENSE).  
📚 All translated text content is shared under the [CC BY-NC 4.0 License](LICENSE-TRANSLATIONS.txt).

> You must own a legal copy of *Monster Hunter 3 Ultimate* to use this pipeline.  
> This is a non-commercial fan project and is not affiliated with Capcom or Nintendo.

