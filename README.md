# LIVP Extractor

Small Python script to extract the image and video from iPhone Live Photo archives that end up with a `.livp` extension (often produced when uploading/sharing Live Photos to services like Baidu Cloud).

See the implementation in [main.py](main.py) and key symbols: [`IMAGE_EXTS`](main.py), [`sanitize_stem`](main.py), [`get_unique_stem`](main.py), [`main`](main.py).

## Why .livp?
Some cloud services (notably Baidu Cloud) convert or package iPhone Live Photos into ZIP-like archives and give them a `.livp` extension. Each archive typically contains a still image (HEIC / JPG) and a `.mov` video. This script extracts those two files.

## Requirements
- Python 3.6+
- Standard library only (zipfile, pathlib, shutil, re)

## Usage
1. Run the script:
```bash
python main.py
```
2. Enter the path to the folder containing `.livp` files when prompted (you can drag the folder into the terminal to paste its path).
3. Confirm extraction. Extracted pairs are placed into a `converted` subfolder next to the input folder.

## Behavior
- Scans the folder tree for `*.livp`.
- For each archive, extracts the first image (one of [`IMAGE_EXTS`](main.py)) and the first `.mov`.
- Produces files named `<original_stem>.<ext>` and `<original_stem>.mov` in `converted/`.
- Handles name collisions via [`get_unique_stem`](main.py) which uses [`sanitize_stem`](main.py) and checks existing files to avoid overwrites.

## Notes
- If an archive lacks either the image or the `.mov`, the file is skipped and counted as a failure.
- The script is designed for Windows-style filenames and sanitizes invalid characters.
- Output folder: `converted` inside the input folder.

## Troubleshooting
- Corrupt archives produce a `BadZipFile` message and are counted as failed.
- Ensure the input path is a directory (the script validates this).

## License
This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.

You are free to:
- Use, copy, and modify this project
- Share it with others
- Use it for personal, educational, or other non-commercial purposes

Under the following conditions:
- **Attribution** — You must give appropriate credit to the author.
- **Non-Commercial** — You may **not** use this project for commercial purposes.

Commercial use requires **explicit permission from the author**.

Full license text:
https://creativecommons.org/licenses/by-nc/4.0/
