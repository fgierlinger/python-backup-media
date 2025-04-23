"""
This script provides a command-line interface (CLI) tool for backing up media files (images and videos)
from an SD card to a specified backup directory. The files are organized into subdirectories by year,
based on their metadata or last modification time.

Modules:
    - logging: For logging errors and information.
    - shutil: For file operations like copying and moving.
    - argparse: For parsing command-line arguments.
    - datetime: For handling date and time operations.
    - pathlib.Path: For filesystem path manipulations.
    - PIL.Image: For working with image files.
    - PIL.ExifTags: For accessing EXIF metadata tags.

Constants:
    - IMAGE_EXTENSIONS: A set of supported image file extensions.
    - VIDEO_EXTENSIONS: A set of supported video file extensions.

Functions:
    - get_exif_date_taken(image_path): Extracts the 'DateTimeOriginal' metadata from the EXIF data of an image file.
    - get_file_year(path): Determines the year associated with a file based on its metadata or modification time.
    - backup_media_files(sd_card_path, backup_path, dry_run=False, move_files=False): Backs up media files from an SD
      card to a specified backup directory, organizing them by year.
    - main(): Parses command-line arguments and invokes the backup_media_files function.

Usage:
    Run the script from the command line with the required arguments:
    ```
    python cli.py <sd_card_path> <backup_path> [-n | --dry-run] [--move]
    ```
    - `<sd_card_path>`: Path to the SD card containing the media files.
    - `<backup_path>`: Path to the destination directory for the backup.
    - `-n | --dry-run`: Optional flag to perform a dry run without making changes.
    - `--move`: Optional flag to move files instead of copying them.

    ```
    python cli.py /path/to/sd_card /path/to/backup --dry-run
    ```
"""
import logging
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv'}


def get_exif_date_taken(image_path):
    """
    Extracts the 'DateTimeOriginal' metadata from the EXIF data of an image file.
    Args:
        image_path (str): The file path to the image from which to extract the EXIF date.
    Returns:
        datetime.datetime or None: The extracted 'DateTimeOriginal' as a datetime object if available
        and successfully parsed, otherwise None.
    Notes:
        - The function uses the PIL library to open the image and access its EXIF data.
        - If the EXIF data is missing or does not contain the 'DateTimeOriginal' tag, the function
          returns None.
        - If an error occurs during processing (e.g., invalid file format), the function handles
          the exception and returns None.
    """

    try:
        image = Image.open(image_path)
        exif_data = image.getexif()
        if not exif_data:
            return None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'DateTimeOriginal':
                return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error("Error reading EXIF data from %s: %s", image_path, str(e))
        return None
    return None


def get_file_year(path):
    """
    Determines the year associated with a given file based on its metadata or modification time.

    Args:
        path (Path): The file path as a `Path` object.

    Returns:
        int: The year extracted from the file's metadata (e.g., EXIF data for images)
             or the file's last modification time. If neither is available, returns the current year.

    Notes:
        - For image files, the function attempts to extract the year from the EXIF "date taken" metadata.
        - If the EXIF data is unavailable or the file is not an image, the function falls back to the
          file's last modification timestamp.
        - In case of any errors during processing, the current year is returned as a fallback.
    """
    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        date_taken = get_exif_date_taken(path)
        if date_taken:
            return date_taken.year
    try:
        timestamp = path.stat().st_mtime
        return datetime.fromtimestamp(timestamp).year
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error("Error getting file year for %s: %s", path, str(e))
        return datetime.now().year


def backup_media_files(sd_card_path, backup_path, dry_run=False, move_files=False):
    """
    Backs up media files (images and videos) from an SD card to a specified backup directory.
    This function scans the provided SD card path for files, filters them based on their extensions,
    organizes them into folders by year, and either copies or moves them to the backup directory.
    Args:
        sd_card_path (str or Path): The path to the SD card containing the media files.
        backup_path (str or Path): The destination path where the media files will be backed up.
        dry_run (bool, optional): If True, performs a dry run without making any changes. Defaults to False.
        move_files (bool, optional): If True, moves the files instead of copying them. Defaults to False.
    Returns:
        None
    Notes:
        - Only files with extensions listed in IMAGE_EXTENSIONS or VIDEO_EXTENSIONS are processed.
        - Files are organized into subdirectories named after the year extracted from the file metadata.
        - If a file already exists in the target directory, it is skipped.
        - If `dry_run` is enabled, no files or directories are created or modified, and actions are logged instead.
    Raises:
        None
    Example:
        backup_media_files('/path/to/sd_card', '/path/to/backup', dry_run=True, move_files=False)
    """

    sd_card_path = Path(sd_card_path)
    backup_path = Path(backup_path)

    if not sd_card_path.exists():
        print(f"SD card path '{sd_card_path}' does not exist.")
        return

    for file in sd_card_path.rglob('*'):
        if not file.is_file():
            logging.error("Provided file is not a file.")
            continue

        ext = file.suffix.lower()
        if ext not in IMAGE_EXTENSIONS and ext not in VIDEO_EXTENSIONS:
            logging.error("file extension '%s' not in IMAGE_EXTENSIONS nor in VIDEO_EXTENSIONS", ext)
            continue

        year = get_file_year(file)
        target_dir = backup_path / str(year)
        target_file = target_dir / file.name

        if dry_run:
            if not target_dir.exists():
                print(f"[DRY RUN] Would create folder: {target_dir}")
            else:
                print(f"[DRY RUN] Folder exists: {target_dir}")
            action = "move" if move_files else "copy"
            print(f"[DRY RUN] Would {action}: {file} -> {target_file}")
            continue

        target_dir.mkdir(parents=True, exist_ok=True)
        if target_file.exists():
            print(f"File already exists, skipping: {target_file}")
            continue

        print(f"{'Moving' if move_files else 'Copying'}: {file} -> {target_file}")
        if move_files:
            shutil.move(file, target_file)
        else:
            shutil.copy2(file, target_file)


def main():
    """
    Main function for the CLI tool to backup media files from an SD card to a specified backup location.
    This function parses command-line arguments to determine the source SD card path, the destination
    backup path, and optional flags for dry-run mode and moving files instead of copying.
    Command-line Arguments:
        sd_card_path (str): Path to the SD card containing the media files to be backed up.
        backup_path (str): Path to the destination directory where the media files will be backed up.
        -n, --dry-run (bool): Optional flag to perform a dry run, showing what actions would be taken
            without actually making any changes.
        --move (bool): Optional flag to move files from the SD card to the backup location instead of
            copying them.
    Calls:
        backup_media_files: A function that performs the actual backup operation based on the provided
        arguments.
    """

    parser = argparse.ArgumentParser(
        description="Backup pictures and videos from an SD card to a backup location organized by year.")
    parser.add_argument("sd_card_path", help="Path to the SD card")
    parser.add_argument("backup_path", help="Path to the backup destination")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying them")
    args = parser.parse_args()

    backup_media_files(args.sd_card_path, args.backup_path, dry_run=args.dry_run, move_files=args.move)
