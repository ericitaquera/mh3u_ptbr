# Project Asset File Overview

This document explains the purpose of key asset files used in the localization and translation of *Monster Hunter 3 Ultimate (MH3U)*.

---

## 📝 Text Files

### Original Spanish Game Texts (`gmd_texts/`)

Located under:

```
gmd_texts/*/*/*/*/*/*/*/*.txt
```

These are the original `.gmd` script text files extracted from the Spanish version of the game. Each file contains dialogue lines or UI messages tied to NPCs or interface elements:

Example:

* `Npc001_spa.txt` through `Npc025_spa.txt`: NPC dialogue
* `NpcName_spa.txt`: NPC name labels

### Translated Portuguese Game Texts (`gmd_texts_ptbr/`)

Located under:

```
gmd_texts_ptbr/*/*/*/*/*/*/*/*.txt
```

These are the localized Portuguese versions of the `.gmd` files. They mirror the structure of the original files and are injected back into the game for patching.

Example:

* `Npc003_spa.txt`: The Portuguese translation of the dialogue spoken by NPC #003
* `Help_spa.txt`: Help menu or tutorial text

---

## 🖼️ Image Files (`images/`)

```
images/*.png
```

These images are visual assets for the start menu screen:

* `st_menu_01_eng.png`: English version
* `st_menu_01_fre.png`: French version
* `st_menu_01_ger.png`: German version
* `st_menu_01_ita.png`: Italian version
* `st_menu_01_spa.png`: Brazilian Portuguese version


---

## 💬 Prompt Files (`prompts_gpt/`)

```
prompts_gpt/*.prompt.txt
```

These contain prompt templates used by GPT-based models to guide the translation or tone of specific dialogue sets.

Examples:

* `Help_spa.prompt.txt`: Prompt context for help menu text
* `Npc003_spa.prompt.txt`: Prompt tailored for NPC #003’s dialogue translation

---

Let me know if you'd like to expand this document with screenshots, file format examples, or GPT automation workflow.
