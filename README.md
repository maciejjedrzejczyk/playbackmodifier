# Audio Playback Speed Modifier

A Python script for batch-processing audio files to adjust playback speed while preserving pitch. The script allows you to set different playback speeds for different subfolders, preserves folder structure, and adds creation dates to filenames.

## Features

- **Batch process** all MP3 and M4A files in a directory and its subdirectories
- **Folder-specific playback speeds**: Set different speeds for each subfolder
- **Preserves pitch**: Speed up audio without the "chipmunk effect"
- **Maintains folder structure**: Output files follow the same organization as input files
- **Adds creation dates** to filenames in YYYY-MM-DD format
- **Robust error handling**: Multiple fallback methods for problematic files
- **Preserves metadata**: Audio tags and other metadata are maintained

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

```bash
python speed_up_audio.py /path/to/input/directory /path/to/output/directory
```

### Interactive Speed Selection

When you run the script, it will:

1. Scan the input directory for subfolders
2. Prompt you to enter a playback speed for the main folder and each subfolder
3. Process all audio files with their corresponding folder's speed setting

Example interaction:

```
Setting playback speeds for each subfolder:
-------------------------------------------
Enter playback speed for main folder 'podcasts' (e.g., 1.5, 2.0): 1.8
Enter playback speed for subfolder 'Science Shows' (e.g., 1.5, 2.0): 1.5
Enter playback speed for subfolder 'Interview Series' (e.g., 1.5, 2.0): 2.0
Enter playback speed for subfolder 'Daily News' (e.g., 1.5, 2.0): 2.5

Processing files in 'main folder' with speed 1.8x
Processing: podcasts/intro.mp3 -> output/podcasts/2023-05-15-intro.mp3 (speed: 1.8x)
Successfully processed: output/podcasts/2023-05-15-intro.mp3
...
```

## How It Works

1. The script recursively finds all `.mp3` and `.m4a` files in the input directory
2. It asks you to specify playback speeds for each subfolder
3. For each audio file:
   - Determines which folder's speed setting to use
   - Gets the file's creation date
   - Creates a new filename with the date prefix (YYYY-MM-DD-filename)
   - Uses FFmpeg to speed up the audio while preserving pitch
   - Preserves the original folder structure in the output directory
   - Maintains metadata from the original file

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