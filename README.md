# 🔍 mac-checkcache

<details>
    <summary>A macOS utility script for checking system caches</summary>
    
    This script provides a simple way to analyze and manage cache files on macOS systems, helping to identify potential disk space issues and improve system performance.
</details>

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

## 📝 Overview

`mac-checkcache` is a Python utility that scans and analyzes cache directories on macOS systems. It helps identify large or outdated cache files that might be consuming valuable disk space.

## ✨ Features

<details>
    <summary>Click to expand features</summary>
    
    - Scans common macOS cache locations
    - Reports cache size by application
    - Identifies outdated cache files
    - Provides options for safe cache cleaning
    - Generates detailed reports of cache usage
</details>

## 🔧 Requirements

- Python 3.6+
- macOS 10.13+
- Admin privileges (for certain cache directories)

## 📥 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mac-checkcache.git
cd mac-checkcache

# Install dependencies (if any)
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Basic usage
python src/main.py

# Scan specific directories
python src/main.py --dirs ~/Library/Caches /Library/Caches

# Generate a report
python src/main.py --report

# Clean old caches (use with caution)
python src/main.py --clean
```

## 📊 Examples

<details>
    <summary>Example output</summary>
    
    ```
    === macOS Cache Report ===
    
    User Caches: 1.2 GB
        - Safari: 350 MB
        - Chrome: 420 MB
        - Spotify: 150 MB
    
    System Caches: 2.3 GB
        - Software Updates: 1.1 GB
        - App Store: 800 MB
        - Font Caches: 200 MB
    
    Recommendation: 650 MB of cache can be safely cleared
    ```
</details>

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.