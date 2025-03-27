#!/usr/bin/env python3
import os
import subprocess
import datetime
import argparse
from pathlib import Path

def get_creation_date(file_path):
    """Get file creation date and format it as YYYY-MM-DD"""
    timestamp = os.path.getctime(file_path)
    date = datetime.datetime.fromtimestamp(timestamp)
    return date.strftime("%Y-%m-%d")

def get_subfolder_speeds(input_dir):
    """Interactively ask for playback speeds for each subfolder"""
    input_path = Path(input_dir)
    
    # Get all immediate subfolders
    subfolders = [f for f in input_path.iterdir() if f.is_dir()]
    
    # If no subfolders, ask for speed for the main folder
    if not subfolders:
        speed = input(f"Enter playback speed for main folder '{input_path.name}' (e.g., 1.5, 2.0): ")
        return {input_path: float(speed)}
    
    subfolder_speeds = {}
    print("\nSetting playback speeds for each subfolder:")
    print("-------------------------------------------")
    
    # Ask for speed for the main folder (for files directly in the input directory)
    speed = input(f"Enter playback speed for main folder '{input_path.name}' (e.g., 1.5, 2.0): ")
    subfolder_speeds[input_path] = float(speed)
    
    # Ask for speed for each subfolder
    for subfolder in subfolders:
        speed = input(f"Enter playback speed for subfolder '{subfolder.name}' (e.g., 1.5, 2.0): ")
        subfolder_speeds[subfolder] = float(speed)
    
    return subfolder_speeds

def safe_decode(byte_string):
    """Safely decode bytes to string, handling encoding errors"""
    if byte_string is None:
        return ""
    try:
        return byte_string.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return byte_string.decode('latin-1')
        except:
            return str(byte_string)

def process_audio_files(input_dir, output_dir):
    """Process all .mp3 and .m4a files in the directory and subdirectories"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    if not output_path.exists():
        output_path.mkdir(parents=True)
    
    # Get playback speeds for each subfolder
    subfolder_speeds = get_subfolder_speeds(input_dir)
    
    # Find all .mp3 and .m4a files
    audio_files = list(input_path.glob("**/*.mp3")) + list(input_path.glob("**/*.m4a"))
    
    # Group files by subfolder
    files_by_folder = {}
    for file_path in audio_files:
        # Determine which subfolder this file belongs to
        parent_folder = file_path.parent
        
        # Find the closest parent folder that has a defined speed
        closest_parent = None
        current_folder = parent_folder
        while current_folder.parts >= input_path.parts:
            if current_folder in subfolder_speeds:
                closest_parent = current_folder
                break
            # Move up one directory
            if current_folder == input_path:
                break
            current_folder = current_folder.parent
        
        # If no matching parent found, use the main input directory
        if closest_parent is None:
            closest_parent = input_path
        
        if closest_parent not in files_by_folder:
            files_by_folder[closest_parent] = []
        
        files_by_folder[closest_parent].append(file_path)
    
    # Process files by folder
    for folder, files in files_by_folder.items():
        speed = subfolder_speeds.get(folder, 2.0)  # Default to 2.0 if not specified
        print(f"\nProcessing files in '{folder.relative_to(input_path) if folder != input_path else 'main folder'}' with speed {speed}x")
        
        for file_path in files:
            # Get relative path to maintain folder structure
            rel_path = file_path.relative_to(input_path)
            
            # Create output subdirectories if needed
            output_subdir = output_path / rel_path.parent
            if not output_subdir.exists():
                output_subdir.mkdir(parents=True)
            
            # Get creation date and prepare new filename
            creation_date = get_creation_date(file_path)
            new_filename = f"{creation_date}-{file_path.name}"
            output_file = output_subdir / new_filename
            
            # Skip if output file already exists
            if output_file.exists():
                print(f"Skipping {file_path} (output already exists)")
                continue
            
            print(f"Processing: {file_path} -> {output_file} (speed: {speed}x)")
            
            # Process audio with FFmpeg (custom speed, preserve pitch)
            # Focus only on audio stream and copy metadata
            if file_path.suffix.lower() == ".mp3":
                cmd = [
                    "ffmpeg", "-i", str(file_path),
                    "-map", "0:a", # Select only audio stream
                    "-filter:a", f"atempo={speed}",
                    "-c:a", "libmp3lame",
                    "-q:a", "2",
                    "-map_metadata", "0",
                    "-id3v2_version", "3",
                    str(output_file)
                ]
            else:  # .m4a files
                cmd = [
                    "ffmpeg", "-i", str(file_path),
                    "-map", "0:a", # Select only audio stream
                    "-filter:a", f"atempo={speed}",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-map_metadata", "0",
                    str(output_file)
                ]
            
            try:
                # Use binary mode (not text mode) to avoid encoding issues
                result = subprocess.run(cmd, check=True, capture_output=True)
                print(f"Successfully processed: {output_file}")
            except subprocess.CalledProcessError as e:
                print(f"Error processing {file_path}: {e}")
                print(f"FFmpeg error: {safe_decode(e.stderr)}")
                
                # Try an alternative approach if the first one fails
                print(f"Trying alternative approach for {file_path}...")
                try:
                    # Simpler command that ignores all non-audio content
                    alt_cmd = [
                        "ffmpeg", "-i", str(file_path),
                        "-vn",  # No video
                        "-filter:a", f"atempo={speed}",
                        "-c:a", "libmp3lame" if file_path.suffix.lower() == ".mp3" else "aac",
                        "-q:a", "2" if file_path.suffix.lower() == ".mp3" else "-b:a", "192k" if file_path.suffix.lower() != ".mp3" else None,
                        str(output_file)
                    ]
                    # Remove None values from the command
                    alt_cmd = [x for x in alt_cmd if x is not None]
                    
                    result = subprocess.run(alt_cmd, check=True, capture_output=True)
                    print(f"Successfully processed with alternative method: {output_file}")
                except subprocess.CalledProcessError as e2:
                    print(f"Alternative approach also failed for {file_path}: {e2}")
                    print(f"FFmpeg error: {safe_decode(e2.stderr)}")
                    
                    # Try a third approach with minimal options
                    print(f"Trying minimal approach for {file_path}...")
                    try:
                        # Bare minimum command
                        min_cmd = [
                            "ffmpeg", "-i", str(file_path),
                            "-vn",  # No video
                            "-filter:a", f"atempo={speed}",
                            str(output_file)
                        ]
                        
                        result = subprocess.run(min_cmd, check=True, capture_output=True)
                        print(f"Successfully processed with minimal method: {output_file}")
                    except subprocess.CalledProcessError as e3:
                        print(f"All approaches failed for {file_path}")
                        print(f"FFmpeg error: {safe_decode(e3.stderr)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch process audio files with subfolder-specific speeds and date-prefixed filenames")
    parser.add_argument("input_dir", help="Input directory containing audio files")
    parser.add_argument("output_dir", help="Output directory for processed files")
    
    args = parser.parse_args()
    process_audio_files(args.input_dir, args.output_dir)