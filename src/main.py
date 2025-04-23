#!/usr/bin/env python3

import os
import sys
import time
import datetime
import shutil
from pathlib import Path


import os

def get_dir_size(path):
    if not os.path.isdir(path):
        return 0  # Skip if it's not a directory
    size = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                size += entry.stat().st_size
            elif entry.is_dir():
                size += get_dir_size(entry.path)
    return size

def format_size(size):
    """Format size in bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

def get_last_access_time(path):
    """Get the last access time of a file or directory"""
    try:
        return datetime.datetime.fromtimestamp(os.path.getatime(path))
    except (PermissionError, FileNotFoundError):
        return None

def is_old_cache(path, months=12):
    """Check if a file or directory hasn't been accessed in the specified months"""
    last_access = get_last_access_time(path)
    if not last_access:
        return False
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30*months)
    return last_access < cutoff_date

def print_dir_tree(path, prefix="", is_last=True, max_depth=3, current_depth=0):
    """Print a directory tree with size and last access information"""
    if current_depth > max_depth:
        return
    
    try:
        basename = os.path.basename(path)
        size = get_dir_size(path)
        last_access = get_last_access_time(path)
        
        last_access_str = last_access.strftime("%Y-%m-%d %H:%M:%S") if last_access else "Unknown"
        
        is_old = is_old_cache(path)
        old_marker = " [OLD]" if is_old else ""
        
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{basename} ({format_size(size)}, Last access: {last_access_str}){old_marker}")
        
        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            
            try:
                items = list(os.scandir(path))
                for i, item in enumerate(items):
                    print_dir_tree(item.path, prefix + extension, i == len(items) - 1, 
                                  max_depth, current_depth + 1)
            except (PermissionError, FileNotFoundError):
                print(f"{prefix}{extension}└── [Permission denied or not found]")
    except (PermissionError, FileNotFoundError):
        print(f"{prefix}└── [Error accessing {os.path.basename(path)}]")

def analyze_cache_directory(directory):
    """Analyze a cache directory and print detailed report"""
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return
    
    print(f"\n{'='*80}")
    print(f"CACHE ANALYSIS: {directory}")
    print(f"{'='*80}")
    
    total_size = get_dir_size(directory)
    print(f"Total size: {format_size(total_size)}")
    
    print("\nDirectory structure:")
    print_dir_tree(directory)
    
    old_caches = []
    try:
        with os.scandir(directory) as it:
            for entry in it:
                if is_old_cache(entry.path):
                    size = get_dir_size(entry.path) if entry.is_dir() else entry.stat().st_size
                    last_access = get_last_access_time(entry.path)
                    old_caches.append((entry.path, size, last_access))
    except (PermissionError, FileNotFoundError):
        print("Permission denied or directory not found when scanning for old caches")
    
    if old_caches:
        print("\nOld caches (not accessed in 12+ months):")
        for path, size, last_access in old_caches:
            last_access_str = last_access.strftime("%Y-%m-%d") if last_access else "Unknown"
            print(f"- {os.path.basename(path)}: {format_size(size)}, Last access: {last_access_str}")
    
    return old_caches

def interactive_cleanup(directories):
    """Provide interactive cleanup for old cache files"""
    all_old_caches = []
    
    for directory in directories:
        old_caches = analyze_cache_directory(directory)
        if old_caches:
            all_old_caches.extend(old_caches)
    
    if not all_old_caches:
        print("\nNo old caches found to clean up.")
        return
    
    print("\n" + "="*80)
    print("INTERACTIVE CLEANUP")
    print("="*80)
    print(f"Found {len(all_old_caches)} items that haven't been accessed in 12+ months.")
    
    while True:
        choice = input("\nOptions:\n1. Delete all old caches\n2. Select individual caches to delete\n3. Exit without deleting\nYour choice (1-3): ")
        
        if choice == "1":
            total_freed = 0
            for path, size, _ in all_old_caches:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    print(f"Deleted: {path}")
                    total_freed += size
                except (PermissionError, FileNotFoundError) as e:
                    print(f"Error deleting {path}: {e}")
            print(f"\nCleanup complete. Freed approximately {format_size(total_freed)} of space.")
            break
            
        elif choice == "2":
            for i, (path, size, last_access) in enumerate(all_old_caches):
                last_access_str = last_access.strftime("%Y-%m-%d") if last_access else "Unknown"
                print(f"{i+1}. {path} ({format_size(size)}, Last access: {last_access_str})")
                delete = input("   Delete? (y/n): ").lower()
                if delete == 'y':
                    try:
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.remove(path)
                        print(f"   Deleted: {path}")
                    except (PermissionError, FileNotFoundError) as e:
                        print(f"   Error deleting {path}: {e}")
            print("\nSelective cleanup complete.")
            break
            
        elif choice == "3":
            print("Exiting without cleanup.")
            break
            
        else:
            print("Invalid option. Please enter 1, 2, or 3.")

# Main execution
if __name__ == "__main__":
    home_dir = os.path.expanduser("~")
    
    cache_dirs = [
        "/Library/Caches",
        "/System/Library/Caches",
        f"{home_dir}/Library/Caches"
    ]
    
    interactive_cleanup(cache_dirs)
    print("\nCache analysis and cleanup completed.")
    sys.exit(0)
# End of script
# This script is designed to analyze and clean up cache directories on macOS.
# It provides detailed information about the size and last access time of files and directories,
# and allows the user to interactively delete old caches that haven't been accessed in over 12 months.
# The script uses Python's os and datetime modules to gather information about the file system,
# and provides a user-friendly interface for cleanup operations.
# The script is intended to be run from the command line and requires Python 3.x.


