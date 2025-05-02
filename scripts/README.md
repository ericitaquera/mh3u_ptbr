# MH3U Scripts Summary

This folder contains Python scripts developed to assist with the localization and modding of *Monster Hunter 3 Ultimate (MH3U)*.

## Included Scripts

### `unpack_arc.py`

Extracts `.arc` container files, decompresses contents, and generates a structured `.properties` metadata file.

* Handles individual ARC files or folders recursively
* Applies correct file extensions based on internal identifiers
* Output directory structure mirrors `$ROMFS_DIR`
* See [detailed README](./README.md) for full documentation

### `repack_arc.py`

(Coming soon / in progress)
Rebuilds `.arc` container files using the extracted files and `.properties` metadata.

* Intended to reverse the process done by `unpack_arc.py`
* Supports compression, proper file alignment, and header generation

## Requirements

* Python 3.6+
* Required environment variables:

  * `BASE_DIR`
  * `ROMFS_DIR`
  * Optionally `ARC_EXTRACTED_DIR`

---

For full documentation of the ARC extraction process, see [`README.md`](./README.md).
