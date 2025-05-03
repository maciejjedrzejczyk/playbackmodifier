# Audio Playback Speed Modifier

A Python script for batch-processing audio files to adjust playback speed while preserving pitch. The script allows you to set different playback speeds for different subfolders, preserves folder structure, and adds creation dates to filenames.

## Features

- **Batch process** all MP3 and M4A files in a directory and its subdirectories
- **Folder-specific playback speeds**: Set different speeds for each subfolder
- **Default playback speed**: Configure a global default speed for all folders
- **Folder exclusion**: Ignore specific folders during processing
- **Preserves pitch**: Speed up audio without the "chipmunk effect"
- **Maintains folder structure**: Output files follow the same organization as input files
- **Adds creation dates** to filenames in YYYY-MM-DD format
- **Robust error handling**: Multiple fallback methods for problematic files
- **Preserves metadata**: Audio tags and other metadata are maintained
- **Remembers folder settings**: Saves preferred playback speeds in a configuration file
- **Prevents duplicate processing**: Tracks processed files with digital fingerprints
- **Non-interactive mode**: Run with command-line arguments for automation

## Requirements

- Python 3.6 or higher
- FFmpeg (must be installed and available in your PATH)

## Installation

1. Make sure you have Python 3 installed
2. Install FFmpeg:
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH
3. Download the script or clone this repository

## Usage

### Interactive Mode (Default)

```bash
python speed_up_audio.py /path/to/input/directory /path/to/output/directory
```

### Non-Interactive Mode (For Automation)

```bash
python speed_up_audio.py /path/to/input/directory /path/to/output/directory --non-interactive [options]
```

Available options for non-interactive mode:
- `--default-speed 1.8`: Set the default playback speed
- `--ignore-folders folder1 folder2`: Specify folders to ignore
- `--folder-speeds folder1:1.5 folder2:2.0`: Set specific speeds for folders

Example:
```bash
python speed_up_audio.py podcasts output --non-interactive --default-speed 1.8 --ignore-folders "Daily News" "Commercials"
```

### Interactive Configuration

When you run the script in interactive mode, it will:

1. Ask if you want to configure the default playback speed
2. Ask if you want to manage ignored folders
3. Scan the input directory for subfolders
4. Check if playback speeds are already configured for each folder
5. Prompt you to enter a playback speed only for folders without saved settings
   - You can press Enter to use the default speed
6. Process all audio files with their corresponding folder's speed setting
7. Skip files that have been processed in previous runs
8. Skip files in ignored folders

Example interaction:

```
Do you want to configure the default playback speed? (y/n): y
Current default playback speed: 1.5x
Enter new default playback speed (or press Enter to keep current): 1.8
Default playback speed updated to 1.8x

Do you want to manage ignored folders? (y/n): y
Manage ignored folders:
----------------------
No folders are currently being ignored.

Available folders:
1. main folder
2. Science Shows
3. Interview Series
4. Daily News

Options:
1. Ignore additional folders
2. Remove folders from ignore list
3. Continue without changes

Enter your choice (1-3): 1
Enter folder numbers to ignore (comma-separated): 4
Added 'Daily News' to ignored folders

Setting playback speeds for each subfolder:
-------------------------------------------
Using saved speed 1.8x for main folder 'podcasts'
Enter playback speed for subfolder 'Science Shows' (e.g., 1.5, 2.0) [default: 1.8x]: 1.5
Using saved speed 2.0x for subfolder 'Interview Series'

Processing files in 'main folder' with speed 1.8x
Skipping podcasts/intro.mp3 (already processed previously to output/podcasts/2023-05-15-intro.mp3)
Processing: podcasts/new-episode.mp3 -> output/podcasts/2023-05-15-new-episode.mp3 (speed: 1.8x)
Successfully processed: output/podcasts/2023-05-15-new-episode.mp3

Processing files in 'Science Shows' with speed 1.5x
Processing: podcasts/Science Shows/episode1.mp3 -> output/podcasts/Science Shows/2023-05-10-episode1.mp3 (speed: 1.5x)
Successfully processed: output/podcasts/Science Shows/2023-05-10-episode1.mp3

Processing files in 'Interview Series' with speed 2.0x
Processing: podcasts/Interview Series/interview.mp3 -> output/podcasts/Interview Series/2023-05-12-interview.mp3 (speed: 2.0x)
Successfully processed: output/podcasts/Interview Series/2023-05-12-interview.mp3

Skipping ignored folder: Daily News
```

## Configuration Files

The script creates and maintains four JSON files:

1. `playback_config.json` - Stores folder-specific playback speeds
2. `processed_files.json` - Tracks processed files using SHA-256 hashes
3. `global_config.json` - Stores the default playback speed
4. `ignored_folders.json` - Stores the list of folders to ignore

These files allow the script to remember your settings and avoid reprocessing files.

## How It Works

1. The script recursively finds all `.mp3` and `.m4a` files in the input directory
2. It loads saved configurations or asks you to specify new ones
3. For each audio file:
   - Checks if the file is in an ignored folder (skips if true)
   - Calculates a SHA-256 hash to check if it's been processed before
   - Determines which folder's speed setting to use
   - Gets the file's creation date
   - Creates a new filename with the date prefix (YYYY-MM-DD-filename)
   - Uses FFmpeg to speed up the audio while preserving pitch
   - Preserves the original folder structure in the output directory
   - Maintains metadata from the original file
   - Records the file's hash in the processed files registry

## Output

The processed files will:
- Be placed in the output directory with the same folder structure as the input
- Have filenames prefixed with their creation date (e.g., `2023-05-15-podcast-episode.mp3`)
- Play faster at the specified speed while maintaining normal pitch
- Retain all metadata (artist, album, etc.) from the original files

## Troubleshooting

If you encounter errors:

- Make sure FFmpeg is properly installed and in your PATH
- Check that you have read/write permissions for the input and output directories
- For files with special characters in their names, try using paths without special characters
- If processing fails for specific files, the script will try alternative methods automatically
