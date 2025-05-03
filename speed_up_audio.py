#!/usr/bin/env python3
import os
import subprocess
import datetime
import argparse
import json
import hashlib
from pathlib import Path

def get_creation_date(file_path):
    """Get file creation date and format it as YYYY-MM-DD"""
    timestamp = os.path.getctime(file_path)
    date = datetime.datetime.fromtimestamp(timestamp)
    return date.strftime("%Y-%m-%d")

def get_file_hash(file_path):
    """Generate a SHA-256 hash of a file to use as a digital fingerprint"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read the file in chunks to handle large files efficiently
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def load_config():
    """Load configuration from config files if they exist"""
    config_path = Path("playback_config.json")
    processed_files_path = Path("processed_files.json")
    global_config_path = Path("global_config.json")
    ignored_folders_path = Path("ignored_folders.json")
    
    # Load folder speeds config
    folder_speeds = {}
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                # Convert string keys back to Path objects
                config_data = json.load(f)
                for folder_str, speed in config_data.items():
                    folder_speeds[Path(folder_str)] = float(speed)
            print(f"Loaded {len(folder_speeds)} folder speed settings from configuration file")
        except Exception as e:
            print(f"Error loading configuration: {e}")
            folder_speeds = {}
    
    # Load processed files registry
    processed_files = {}
    if processed_files_path.exists():
        try:
            with open(processed_files_path, 'r') as f:
                processed_files = json.load(f)
            print(f"Loaded {len(processed_files)} processed file records")
        except Exception as e:
            print(f"Error loading processed files registry: {e}")
            processed_files = {}
    
    # Load global config (default speed)
    global_config = {"default_speed": 1.5}  # Default value if not set
    if global_config_path.exists():
        try:
            with open(global_config_path, 'r') as f:
                global_config = json.load(f)
            print(f"Using default speed: {global_config['default_speed']}x")
        except Exception as e:
            print(f"Error loading global configuration: {e}")
    
    # Load ignored folders
    ignored_folders = []
    if ignored_folders_path.exists():
        try:
            with open(ignored_folders_path, 'r') as f:
                ignored_folders_data = json.load(f)
                ignored_folders = [Path(folder_str) for folder_str in ignored_folders_data]
            if ignored_folders:
                print(f"Loaded {len(ignored_folders)} ignored folders")
        except Exception as e:
            print(f"Error loading ignored folders: {e}")
    
    return folder_speeds, processed_files, global_config, ignored_folders

def save_config(folder_speeds, processed_files=None, global_config=None, ignored_folders=None):
    """Save configuration to config files"""
    config_path = Path("playback_config.json")
    
    # Convert Path objects to strings for JSON serialization
    serializable_config = {str(folder): speed for folder, speed in folder_speeds.items()}
    
    try:
        with open(config_path, 'w') as f:
            json.dump(serializable_config, f, indent=2)
        print(f"Saved {len(folder_speeds)} folder speed settings to configuration file")
    except Exception as e:
        print(f"Error saving configuration: {e}")
    
    # Save processed files if provided
    if processed_files is not None:
        processed_files_path = Path("processed_files.json")
        try:
            with open(processed_files_path, 'w') as f:
                json.dump(processed_files, f, indent=2)
            print(f"Saved {len(processed_files)} processed file records")
        except Exception as e:
            print(f"Error saving processed files registry: {e}")
    
    # Save global config if provided
    if global_config is not None:
        global_config_path = Path("global_config.json")
        try:
            with open(global_config_path, 'w') as f:
                json.dump(global_config, f, indent=2)
            print(f"Saved global configuration with default speed: {global_config['default_speed']}x")
        except Exception as e:
            print(f"Error saving global configuration: {e}")
    
    # Save ignored folders if provided
    if ignored_folders is not None:
        ignored_folders_path = Path("ignored_folders.json")
        try:
            # Convert Path objects to strings for JSON serialization
            serializable_ignored = [str(folder) for folder in ignored_folders]
            with open(ignored_folders_path, 'w') as f:
                json.dump(serializable_ignored, f, indent=2)
            print(f"Saved {len(ignored_folders)} ignored folders")
        except Exception as e:
            print(f"Error saving ignored folders: {e}")

def update_processed_files(processed_files, file_path, output_file):
    """Add a processed file to the registry"""
    file_hash = get_file_hash(file_path)
    processed_files[file_hash] = {
        "input_path": str(file_path),
        "output_path": str(output_file),
        "processed_date": datetime.datetime.now().isoformat()
    }
    return processed_files

def configure_default_speed(global_config):
    """Configure or update the default playback speed"""
    current_default = global_config.get("default_speed", 1.5)
    print(f"\nCurrent default playback speed: {current_default}x")
    
    new_default = input("Enter new default playback speed (or press Enter to keep current): ")
    if new_default.strip():
        try:
            global_config["default_speed"] = float(new_default)
            print(f"Default playback speed updated to {global_config['default_speed']}x")
        except ValueError:
            print(f"Invalid input. Keeping default speed at {current_default}x")
    
    return global_config

def manage_ignored_folders(input_dir, ignored_folders):
    """Manage the list of folders to ignore during processing"""
    input_path = Path(input_dir)
    
    # Get all immediate subfolders
    subfolders = [f for f in input_path.iterdir() if f.is_dir()]
    all_folders = [input_path] + subfolders
    
    print("\nManage ignored folders:")
    print("----------------------")
    
    # Show current ignored folders
    if ignored_folders:
        print("Currently ignored folders:")
        for i, folder in enumerate(ignored_folders, 1):
            print(f"{i}. {folder.relative_to(input_path) if folder != input_path else 'main folder'}")
    else:
        print("No folders are currently being ignored.")
    
    # Show available folders
    print("\nAvailable folders:")
    for i, folder in enumerate(all_folders, 1):
        status = " (ignored)" if folder in ignored_folders else ""
        print(f"{i}. {folder.relative_to(input_path) if folder != input_path else 'main folder'}{status}")
    
    # Ask user what to do
    print("\nOptions:")
    print("1. Ignore additional folders")
    print("2. Remove folders from ignore list")
    print("3. Continue without changes")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == "1":
        # Add folders to ignore list
        folder_nums = input("Enter folder numbers to ignore (comma-separated): ").split(",")
        for num in folder_nums:
            try:
                idx = int(num.strip()) - 1
                if 0 <= idx < len(all_folders):
                    folder = all_folders[idx]
                    if folder not in ignored_folders:
                        ignored_folders.append(folder)
                        print(f"Added '{folder.relative_to(input_path) if folder != input_path else 'main folder'}' to ignored folders")
            except ValueError:
                continue
    
    elif choice == "2":
        # Remove folders from ignore list
        if not ignored_folders:
            print("No folders to remove from ignore list.")
        else:
            folder_nums = input("Enter folder numbers to remove from ignore list (comma-separated): ").split(",")
            for num in folder_nums:
                try:
                    idx = int(num.strip()) - 1
                    if 0 <= idx < len(all_folders):
                        folder = all_folders[idx]
                        if folder in ignored_folders:
                            ignored_folders.remove(folder)
                            print(f"Removed '{folder.relative_to(input_path) if folder != input_path else 'main folder'}' from ignored folders")
                except ValueError:
                    continue
    
    return ignored_folders

def get_folder_speeds(input_dir):
    """Interactively ask for playback speeds for each subfolder, using saved config if available"""
    input_path = Path(input_dir)
    
    # Load existing configuration
    folder_speeds, processed_files, global_config, ignored_folders = load_config()
    
    # Ask if user wants to configure default speed
    configure_default = input("\nDo you want to configure the default playback speed? (y/n): ").lower()
    if configure_default == 'y':
        global_config = configure_default_speed(global_config)
        save_config(folder_speeds, processed_files, global_config, ignored_folders)
    
    # Ask if user wants to manage ignored folders
    manage_ignored = input("\nDo you want to manage ignored folders? (y/n): ").lower()
    if manage_ignored == 'y':
        ignored_folders = manage_ignored_folders(input_dir, ignored_folders)
        save_config(folder_speeds, processed_files, global_config, ignored_folders)
    
    # Get all immediate subfolders
    subfolders = [f for f in input_path.iterdir() if f.is_dir()]
    
    # If no subfolders, check if main folder is configured or ask for speed
    if not subfolders:
        if input_path in folder_speeds:
            print(f"Using saved speed {folder_speeds[input_path]}x for main folder '{input_path.name}'")
            return folder_speeds, processed_files, global_config, ignored_folders
        
        speed = input(f"Enter playback speed for main folder '{input_path.name}' (e.g., 1.5, 2.0) [default: {global_config['default_speed']}x]: ")
        if speed.strip():
            folder_speeds[input_path] = float(speed)
        else:
            folder_speeds[input_path] = global_config['default_speed']
            print(f"Using default speed {global_config['default_speed']}x for main folder '{input_path.name}'")
        
        save_config(folder_speeds, processed_files, global_config, ignored_folders)
        return folder_speeds, processed_files, global_config, ignored_folders
    
    print("\nSetting playback speeds for each subfolder:")
    print("-------------------------------------------")
    
    # Check if main folder is configured or ask for speed
    if input_path in folder_speeds:
        print(f"Using saved speed {folder_speeds[input_path]}x for main folder '{input_path.name}'")
    else:
        speed = input(f"Enter playback speed for main folder '{input_path.name}' (e.g., 1.5, 2.0) [default: {global_config['default_speed']}x]: ")
        if speed.strip():
            folder_speeds[input_path] = float(speed)
        else:
            folder_speeds[input_path] = global_config['default_speed']
            print(f"Using default speed {global_config['default_speed']}x for main folder '{input_path.name}'")
    
    # Check if each subfolder is configured or ask for speed
    for subfolder in subfolders:
        if subfolder in folder_speeds:
            print(f"Using saved speed {folder_speeds[subfolder]}x for subfolder '{subfolder.name}'")
        else:
            speed = input(f"Enter playback speed for subfolder '{subfolder.name}' (e.g., 1.5, 2.0) [default: {global_config['default_speed']}x]: ")
            if speed.strip():
                folder_speeds[subfolder] = float(speed)
            else:
                folder_speeds[subfolder] = global_config['default_speed']
                print(f"Using default speed {global_config['default_speed']}x for subfolder '{subfolder.name}'")
    
    # Save updated configuration
    save_config(folder_speeds, processed_files, global_config, ignored_folders)
    
    return folder_speeds, processed_files, global_config, ignored_folders

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
    
    # Get playback speeds for each subfolder and processed files registry
    folder_speeds, processed_files, global_config, ignored_folders = get_folder_speeds(input_dir)
    
    # Find all .mp3 and .m4a files
    audio_files = list(input_path.glob("**/*.mp3")) + list(input_path.glob("**/*.m4a"))
    
    # Group files by subfolder
    files_by_folder = {}
    for file_path in audio_files:
        # Determine which subfolder this file belongs to
        parent_folder = file_path.parent
        
        # Skip files in ignored folders
        if parent_folder in ignored_folders:
            print(f"Skipping file in ignored folder: {file_path}")
            continue
        
        # Check if any parent folder is in the ignored list
        skip_file = False
        current = parent_folder
        while current.parts >= input_path.parts:
            if current in ignored_folders:
                print(f"Skipping file in ignored folder hierarchy: {file_path}")
                skip_file = True
                break
            if current == input_path:
                break
            current = current.parent
        
        if skip_file:
            continue
        
        # Find the closest parent folder that has a defined speed
        closest_parent = None
        current_folder = parent_folder
        while current_folder.parts >= input_path.parts:
            if current_folder in folder_speeds:
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
        # Skip ignored folders
        if folder in ignored_folders:
            print(f"Skipping ignored folder: {folder.relative_to(input_path) if folder != input_path else 'main folder'}")
            continue
            
        speed = folder_speeds.get(folder, global_config['default_speed'])  # Use default speed if not specified
        print(f"\nProcessing files in '{folder.relative_to(input_path) if folder != input_path else 'main folder'}' with speed {speed}x")
        
        for file_path in files:
            # Check if file has already been processed by calculating its hash
            file_hash = get_file_hash(file_path)
            if file_hash in processed_files:
                print(f"Skipping {file_path} (already processed previously to {processed_files[file_hash]['output_path']})")
                continue
            
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
                # Still record this file in our processed files registry
                processed_files = update_processed_files(processed_files, file_path, output_file)
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
                # Add to processed files registry
                processed_files = update_processed_files(processed_files, file_path, output_file)
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
                    # Add to processed files registry
                    processed_files = update_processed_files(processed_files, file_path, output_file)
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
                        # Add to processed files registry
                        processed_files = update_processed_files(processed_files, file_path, output_file)
                    except subprocess.CalledProcessError as e3:
                        print(f"All approaches failed for {file_path}")
                        print(f"FFmpeg error: {safe_decode(e3.stderr)}")
    
    # Save the updated processed files registry
    save_config(folder_speeds, processed_files, global_config, ignored_folders)

def non_interactive_process(input_dir, output_dir, default_speed=None, ignore_folders=None):
    """Process audio files in non-interactive mode with specified parameters"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    if not output_path.exists():
        output_path.mkdir(parents=True)
    
    # Load existing configuration
    folder_speeds, processed_files, global_config, ignored_folders = load_config()
    
    # Update default speed if provided
    if default_speed is not None:
        try:
            global_config["default_speed"] = float(default_speed)
            print(f"Using specified default speed: {global_config['default_speed']}x")
        except ValueError:
            print(f"Invalid default speed value. Using existing default: {global_config['default_speed']}x")
    
    # Update ignored folders if provided
    if ignore_folders:
        for folder_name in ignore_folders:
            folder_path = input_path / folder_name
            if folder_path.exists() and folder_path.is_dir() and folder_path not in ignored_folders:
                ignored_folders.append(folder_path)
                print(f"Added '{folder_name}' to ignored folders")
    
    # Find all .mp3 and .m4a files
    audio_files = list(input_path.glob("**/*.mp3")) + list(input_path.glob("**/*.m4a"))
    
    # Group files by subfolder
    files_by_folder = {}
    for file_path in audio_files:
        # Determine which subfolder this file belongs to
        parent_folder = file_path.parent
        
        # Skip files in ignored folders
        if parent_folder in ignored_folders:
            print(f"Skipping file in ignored folder: {file_path}")
            continue
        
        # Check if any parent folder is in the ignored list
        skip_file = False
        current = parent_folder
        while current.parts >= input_path.parts:
            if current in ignored_folders:
                print(f"Skipping file in ignored folder hierarchy: {file_path}")
                skip_file = True
                break
            if current == input_path:
                break
            current = current.parent
        
        if skip_file:
            continue
        
        # Find the closest parent folder that has a defined speed
        closest_parent = None
        current_folder = parent_folder
        while current_folder.parts >= input_path.parts:
            if current_folder in folder_speeds:
                closest_parent = current_folder
                break
            # Move up one directory
            if current_folder == input_path:
                break
            current_folder = current_folder.parent
        
        # If no matching parent found, use the main input directory
        if closest_parent is None:
            closest_parent = input_path
            # If main folder doesn't have a speed, set it to default
            if closest_parent not in folder_speeds:
                folder_speeds[closest_parent] = global_config['default_speed']
                print(f"Setting main folder '{closest_parent.name}' to default speed {global_config['default_speed']}x")
        
        if closest_parent not in files_by_folder:
            files_by_folder[closest_parent] = []
        
        files_by_folder[closest_parent].append(file_path)
    
    # Process files by folder
    for folder, files in files_by_folder.items():
        # Skip ignored folders
        if folder in ignored_folders:
            print(f"Skipping ignored folder: {folder.relative_to(input_path) if folder != input_path else 'main folder'}")
            continue
            
        speed = folder_speeds.get(folder, global_config['default_speed'])  # Use default speed if not specified
        print(f"\nProcessing files in '{folder.relative_to(input_path) if folder != input_path else 'main folder'}' with speed {speed}x")
        
        # Process files in this folder
        for file_path in files:
            # Check if file has already been processed by calculating its hash
            file_hash = get_file_hash(file_path)
            if file_hash in processed_files:
                print(f"Skipping {file_path} (already processed previously to {processed_files[file_hash]['output_path']})")
                continue
            
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
                # Still record this file in our processed files registry
                processed_files = update_processed_files(processed_files, file_path, output_file)
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
                # Add to processed files registry
                processed_files = update_processed_files(processed_files, file_path, output_file)
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
                    # Add to processed files registry
                    processed_files = update_processed_files(processed_files, file_path, output_file)
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
                        # Add to processed files registry
                        processed_files = update_processed_files(processed_files, file_path, output_file)
                    except subprocess.CalledProcessError as e3:
                        print(f"All approaches failed for {file_path}")
                        print(f"FFmpeg error: {safe_decode(e3.stderr)}")
    
    # Save the updated processed files registry
    save_config(folder_speeds, processed_files, global_config, ignored_folders)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch process audio files with subfolder-specific speeds and date-prefixed filenames")
    parser.add_argument("input_dir", help="Input directory containing audio files")
    parser.add_argument("output_dir", help="Output directory for processed files")
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode using saved settings")
    parser.add_argument("--default-speed", type=float, help="Set default playback speed (non-interactive mode only)")
    parser.add_argument("--ignore-folders", nargs="+", help="List of folder names to ignore (non-interactive mode only)")
    parser.add_argument("--folder-speeds", nargs="+", help="Set speeds for specific folders in format folder_name:speed (non-interactive mode only)")
    
    args = parser.parse_args()
    
    if args.non_interactive:
        # Run in non-interactive mode
        non_interactive_process(args.input_dir, args.output_dir, args.default_speed, args.ignore_folders)
    else:
        # Run in interactive mode
        process_audio_files(args.input_dir, args.output_dir)
