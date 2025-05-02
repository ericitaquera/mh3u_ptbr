# Unpack ARC

This tool extracts and decompresses ARC container files used in *Monster Hunter 3 Ultimate (MH3U)*.

## Features

* Accepts a single `.arc` file or a directory (recursively) containing multiple `.arc` files
* Decompresses files using `zlib` when needed
* Automatically assigns correct file extensions based on `UNK1` type signatures
* Outputs all extracted files into a directory tree that mirrors the structure under `$ROMFS_DIR`
* Generates a `.properties` file with metadata per archive, formatted for compatibility with repacking tools

## Requirements

* Python 3.6+
* Environment variables:

  * `BASE_DIR`: Root project directory (required)
  * `ROMFS_DIR`: Path prefix to strip from ARC file locations to determine relative paths (required)
  * `ARC_EXTRACTED_DIR`: Base directory to output extracted files (optional if output path is passed as argument)

## Usage

```bash
python unpack_arc.py <file.arc|directory> [output_dir]
```

If `output_dir` is omitted, the script uses `$ARC_EXTRACTED_DIR`. Output subdirectories are derived from the ARC’s relative path under `$ROMFS_DIR`.

## Output Structure

For an ARC at:

```
$ROMFS_DIR/arc/ID/ID_lb_spa.arc
```

The output will go to:

```
$ARC_EXTRACTED_DIR/arc/ID/ID_lb_spa.arc/
```

And its metadata will be saved as:

```
$ARC_EXTRACTED_DIR/arc/ID/ID_lb_spa.arc.properties
```

## .properties Format

```
OFFSET;UNK1;FLAGS;FULLPATH;COMPRESSED;SIGNATURE;SIZE;ZSIZE
0x00008000;0x242bb29a;0x00000040;GUI/font/Common_spa.gmd;YES;0x00009c78;693;116
```

* `OFFSET`: File position in the ARC
* `UNK1`: Type ID used to infer extension
* `FLAGS`: Bitfield from the ARC entry (e.g. compression flags)
* `FULLPATH`: Path to save the extracted file under the output directory
* `COMPRESSED`: `YES`/`NO` depending on zlib use
* `SIGNATURE`: First two bytes of zlib stream reversed and zero-padded
* `SIZE`: Raw size
* `ZSIZE`: Compressed size

---

Let me know if you'd like to include screenshots, test samples, or repacking notes.
