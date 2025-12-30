import os
import shutil
import zipfile
import re
from pathlib import Path, PurePosixPath

def sanitize_stem(stem: str) -> str:
    # Remove characters invalid on Windows and collapse spaces
    return re.sub(r'[<>:"/\\|?*\n\r]+', '_', stem).strip()

# supported image extensions inside .livp archives
IMAGE_EXTS = ('.heic', '.jpg', '.jpeg')
def get_unique_stem(base_stem, existing_stems, output_dir: Path):
    """
    Generate a unique filename stem by checking both seen stems and existing files
    in output_dir to avoid overwrites across runs.
    """
    base_stem = sanitize_stem(base_stem)
    # if base not seen in this run, start counter at 0
    if base_stem not in existing_stems:
        existing_stems[base_stem] = 0

    candidate = base_stem if existing_stems[base_stem] == 0 else f"{base_stem}_{existing_stems[base_stem]}"
    # if candidate file(s) already exist on disk (any supported image ext or .mov), increment until unique
    while any((output_dir / f"{candidate}{ext}").exists() for ext in ('.mov',) + IMAGE_EXTS):
        existing_stems[base_stem] += 1
        candidate = f"{base_stem}_{existing_stems[base_stem]}"

    # increment for next duplicate within this run
    if existing_stems[base_stem] == 0:
        # leave counter at 0 so next duplicate becomes _1
        existing_stems[base_stem] = 0
    else:
        # we've already bumped above
        pass

    return candidate

def main():
    """
    Main function to extract .heic and .mov from .livp files.
    """
    # 1. Ask for the input folder path
    input_folder_path_str = input("Please enter the path to the folder containing .livp files: ").strip()
    # Remove quotes if user dragged and dropped folder in terminal
    input_folder_path_str = input_folder_path_str.replace('"', '').replace("'", "") 
    input_folder_path = Path(input_folder_path_str)

    if not input_folder_path.is_dir():
        print(f"Error: The path '{input_folder_path}' is not a valid directory.")
        return

    # Define the output folder path
    output_folder_path = input_folder_path / "converted"

    # 2. Find all .livp files
    print("Scanning directory tree... (this may take a moment for large folders)")
    
    # We convert to list to get the total count for the progress bar
    try:
        livp_files = list(input_folder_path.rglob("*.livp"))
    except Exception as e:
        print(f"Error scanning files: {e}")
        return

    num_files = len(livp_files)

    # 3. Show count and ask for confirmation
    print(f"Found {num_files} .livp file(s).")
    if num_files == 0:
        print("No .livp files found. Exiting.")
        return

    proceed = input("Do you want to proceed with extraction? (yes/no): ").strip().lower()
    if proceed not in ('yes', 'y'):
        print("Extraction cancelled by user.")
        return

    # Create the 'converted' directory
    output_folder_path.mkdir(exist_ok=True)

    successful_extractions = 0
    failed_extractions = 0
    
    # Dictionary to track filenames we have already seen to handle duplicates
    # Structure: {'IMG_0001': count}
    seen_filenames = {}

    print(f"\nStarting extraction to: {output_folder_path}")
    print("---------------------------------------------------")

    # 4. Process files
    # Enumerate gives us an index (i) to calculate progress
    for i, livp_path in enumerate(livp_files, 1):
        try:
            # --- Progress Update ---
            # Update user every 100 files so the console isn't flooded, 
            # but the user knows it's working.
            if i % 100 == 0 or i == num_files:
                percent = (i / num_files) * 100
                print(f"Processing {i}/{num_files} ({percent:.1f}%)...")

            # --- Handle Filename Collisions ---
            original_stem = livp_path.stem 
            # Get a unique stem (e.g., changes IMG_0001 to IMG_0001_1 if needed)
            unique_stem = get_unique_stem(original_stem, seen_filenames, output_folder_path)
            
            output_heic_path = output_folder_path / f"{unique_stem}.heic"
            output_mov_path = output_folder_path / f"{unique_stem}.mov"

            # --- Zip Extraction ---
            with zipfile.ZipFile(livp_path, 'r') as zip_ref:
                zip_contents = zip_ref.namelist()

                image_file_name = None
                mov_file_name = None

                for filename in zip_contents:
                    # Use PurePosixPath to get basename and path segments
                    p = PurePosixPath(filename)
                    name_lower = p.name.lower()
                    parts = [part.lower() for part in p.parts]

                    # skip macOS metadata or hidden path segments anywhere in the path
                    if any(part.startswith('__macosx') for part in parts) or any(part.startswith('.') for part in parts):
                        continue

                    if name_lower.endswith(IMAGE_EXTS):
                        # pick the first image we encounter (could be improved to pick largest)
                        image_file_name = filename if image_file_name is None else image_file_name
                    elif name_lower.endswith('.mov'):
                        mov_file_name = filename if mov_file_name is None else mov_file_name

                    if image_file_name and mov_file_name:
                        break

                if not image_file_name or not mov_file_name:
                    print(f"[!] Skipping {livp_path.name}: missing image ({', '.join(IMAGE_EXTS)}) or .mov inside archive")
                    failed_extractions += 1
                    continue

                # determine image extension and output path
                image_ext = PurePosixPath(image_file_name).suffix.lower()
                output_image_path = output_folder_path / f"{unique_stem}{image_ext}"

                # extract and rename
                with zip_ref.open(image_file_name) as source, open(output_image_path, 'wb') as target:
                    shutil.copyfileobj(source, target)

                with zip_ref.open(mov_file_name) as source, open(output_mov_path, 'wb') as target:
                    shutil.copyfileobj(source, target)

            successful_extractions += 1

        except zipfile.BadZipFile:
            print(f"[!] Error: Corrupt file '{livp_path.name}'")
            failed_extractions += 1
        except Exception as e:
            print(f"[!] Error processing '{livp_path.name}': {e}")
            failed_extractions += 1

    # 5. Final Summary
    print("\n" + "="*30)
    print("COMPLETED")
    print("="*30)
    print(f"Total processed: {num_files}")
    print(f"Successful:      {successful_extractions}")
    print(f"Failed:          {failed_extractions}")
    print(f"Output folder:   {output_folder_path}")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()