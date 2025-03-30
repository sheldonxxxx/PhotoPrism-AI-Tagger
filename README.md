**PhotoPrism Caption Generator**
=====================================

## Overview

This project is a Python-based caption generator for PhotoPrism, a self-hosted photo management platform. It uses AI models to generate captions for photos and updates the PhotoPrism database with the generated captions.

## AI Models

- **Caption Models**:
  - Florence 2: Super detailed but slower.
  - Kosmos-2: Faster on both CPU and GPU but less detailed.
- **Tagging Model**:
  - Yolov11x: Used for image classification and tagging.

## Requirements

- Python 3.10+
- PhotoPrism instance with API access
- GPU (optional but recommended for faster processing)

## Installation

### CPU Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sheldonxxxx/PhotoPrism-AI-Tagger.git
   cd PhotoPrism-AI-Tagger
   ```
2. Install `uv`:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Install dependencies:
   ```bash
   python -m uv pip install -r requirements.txt
   ```
4. Rename `.env1` to `.env` and configure it with your PhotoPrism API credentials and other settings (see `constants.py` for details).
5. Edit `json_payload` in `worker.py` to match your filtering needs.
6. Run the script:
   ```bash
   python -m uv python worker.py
   ```

### GPU Installation (Linux)

1. Install CUDA and cuDNN (if not already installed).
2. Install the GPU version of PyTorch:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
3. Clone the repository:
   ```bash
   git clone https://github.com/sheldonxxxx/PhotoPrism-AI-Tagger.git
   cd PhotoPrism-AI-Tagger
   ```
4. Install `uv`:
   ```bash
   pip install uv
   ```
5. Install dependencies:
   ```bash
   python -m uv pip install -r requirements.txt
   ```
6. Rename `.env1` to `.env` and configure it with your PhotoPrism API credentials and other settings (see `constants.py` for details).
7. Edit `json_payload` in `worker.py` to match your filtering needs.
8. Run the script:
   ```bash
   python -m uv python worker.py
   ```

### GPU Installation (Mac)

1. Install PyTorch:
   ```bash
   pip install torch torchvision torchaudio
   ```
2. Clone the repository:
   ```bash
   git clone https://github.com/sheldonchiu/PhotoPrism-AI-Tagger.git
   cd PhotoPrism-AI-Tagger
   ```
3. Install `uv`:
   ```bash
   pip install uv
   ```
4. Install dependencies:
   ```bash
   python -m uv pip install -r requirements.txt
   ```
5. Rename `.env1` to `.env` and configure it with your PhotoPrism API credentials and other settings (see `constants.py` for details).
6. Edit `json_payload` in `worker.py` to match your filtering needs.
7. Run the script:
   ```bash
   python -m uv python worker.py
   ```

## Configuration

The script uses environment variables to configure the PhotoPrism API connection and other settings. You can create a `.env` file with the following variables:

- `PHOTOPRISM_ROOT_URL`: The URL of your PhotoPrism instance.
- `PHOTOPRISM_TOKEN`: Your PhotoPrism API token.
- `NODE_NAME`: A unique identifier for this worker (default: `worker1`).
- `TEMP_PHOTO_DIR`: A temporary directory for storing downloaded photos (default: `/tmp`).

## Usage

1. Run the script:
   ```bash
   python -m uv python worker.py
   ```
2. The script will process photos in batches, generate captions, and update the PhotoPrism database.
3. Monitor progress and errors in the console output.

## Troubleshooting

- Ensure your PhotoPrism API credentials are correct and the API is accessible.
- Check the console output for error messages or exceptions.
- If GPU installation issues occur, try reinstalling PyTorch and transformers with the `--no-deps` flag.