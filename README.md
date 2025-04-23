# Backup Media CLI Tool

This project provides a command-line interface (CLI) tool for backing up media
files (images and videos) from an SD card to a specified backup directory. The
files are organized into subdirectories by year, based on their metadata or last
modification time.

## Features

- Supports image and video file formats.
- Organizes files into subdirectories by year.
- Options to copy or move files.
- Dry-run mode to preview actions without making changes.
- Automatically updates version information using Commitizen.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/python-backup-media.git
   cd python-backup-media
   ```

2. Installation
   ```bash
   pip install .
   ```

## Usage

Run the script from the command line with the required arguments:

```bash
backup-media <sd_card_path> <backup_path> [-n | --dry-run] [--move]
```

### Arguments

- `<sd_card_path>`: Path to the SD card containing the media files.
- `<backup_path>`: Path to the destination directory for the backup.
- `-n | --dry-run`: Optional flag to perform a dry run without making changes.
- `--move`: Optional flag to move files instead of copying them.
- `--version`: Show the version of the script.

## Development

### Running Tests

To run the tests, use:
```bash
python -m unittest discover tests
```

### Versioning

This project uses [Commitizen](https://commitizen-tools.github.io/commitizen/)
for versioning. To bump the version, run:
```bash
cz bump
```

## License

This project is licensed under the MIT License. See the LICENSE file for
details.
