# FBX to Video Converter

A Python application that converts FBX animation files to MP4 videos using Blender's Python API.

## Feature

- Batch conversion of FBX files to MP4 videos

## Requirements

- Python 3.11
- Blender 4.5.1 LTS(I haven't tested other versions.)

## Installation

1. Install Rye package manager if not already installed
2. Clone this repository
3. Install dependencies:
```bash
$ rye sync
```

## Usage

1. Place your FBX animation files in the `animations/` directory
2. Run the conversion script:
```bash
$ rye run python src/main.py
```
3. Converted MP4 videos will be saved in the `output_videos/` directory

## Directory Structure

```
fbx2video/
├── animations/          # Input FBX files
├── output_videos/       # Generated MP4 files
├── src/
│   └── main.py         # Main conversion script
├── pyproject.toml      # Project configuration
└── README.md
```

## How It Works

The application processes FBX files through the following steps:

1. Clears the default Blender scene
2. Imports each FBX file using Blender's import functionality
3. Configures render settings for video output
4. Renders the animation to MP4 format using FFMPEG
