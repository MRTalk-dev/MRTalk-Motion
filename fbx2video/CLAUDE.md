# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Python project that converts FBX animation files to MP4 videos using Blender's Python API (bpy). The project processes FBX files from an `animations/` directory and outputs rendered MP4 videos to `output_videos/`.

## Development Setup and Commands

### Package Management
This project uses [Rye](https://rye-up.com/) for dependency management. Common commands:

- Install dependencies: `rye sync`
- Add a dependency: `rye add <package>`
- Add dev dependency: `rye add --dev <package>`
- Run Python script: `rye run python src/main.py`
- Create virtual environment: `rye sync`

### Running the Application
- Main script: `rye run python src/main.py`
- The script processes all `.fbx` files in the `animations/` directory
- Output videos are saved to `output_videos/` directory

## Architecture

### Core Components
- `src/main.py`: Main entry point containing the FBX to MP4 conversion logic
- `render_fbx_to_mp4()`: Core function that handles Blender scene setup, FBX import, render configuration, and MP4 export

### Key Dependencies
- `bpy` (Blender Python API): Used for 3D scene manipulation, FBX import, and video rendering
- Requires Blender's Python environment or standalone bpy installation

### Directory Structure
- `animations/`: Input directory for FBX files
- `output_videos/`: Output directory for rendered MP4 files (created automatically)
- `src/`: Source code directory

### Rendering Process
1. Clear existing Blender scene objects
2. Import FBX file using `bpy.ops.import_scene.fbx()`
3. Configure render settings (FFMPEG, MPEG4, H264 codec)
4. Execute animation rendering with `bpy.ops.render.render(animation=True)`

## Important Notes
- This project requires Blender's Python API (bpy) which may need special installation or running within Blender's Python environment
- The script processes files in batch mode, converting all FBX files found in the animations directory
- Comments in the code are in Japanese