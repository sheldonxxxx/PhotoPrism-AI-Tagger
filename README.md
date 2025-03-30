**PhotoPrism Caption Generator**
=====================================

## Overview

This project is an AI caption generator for PhotoPrism, a self-hosted photo management platform. It uses AI models to generate captions for photos and updates the PhotoPrism database with the generated captions.

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

### Installation (Linux & Mac)

1. Clone the repository:
   ```bash
   git clone https://github.com/sheldonxxxx/PhotoPrism-AI-Tagger.git
   cd PhotoPrism-AI-Tagger
   ```
2. Install `uv`:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.local/bin/env
   ```
3. Install dependencies **(Nvidia GPU only)**:
   ```bash
   uv pip install torch torchvision torchaudio --index https://download.pytorch.org/whl/cu126
   ```
4. Rename `.env1` to `.env` and configure it with your PhotoPrism API credentials and other settings (see `Configuration` table below for details).
5. Edit `json_payload` in `worker.py` to match your filtering needs. **(Advance)**
6. Run the script:
   ```bash
   uv run worker.py
   ```

### Installation (Windows)

1. Clone the repository:
   ```bash
   git clone https://github.com/sheldonxxxx/PhotoPrism-AI-Tagger.git
   cd PhotoPrism-AI-Tagger
   ```
2. Install `uv`:
   ```bash
   winget install --id=astral-sh.uv  -e
   ```
3. Install dependencies **(Nvidia GPU only)**:
   ```bash
   uv pip install torch torchvision torchaudio --index https://download.pytorch.org/whl/cu126
   ```
4. Rename `.env1` to `.env` and configure it with your PhotoPrism API credentials and other settings (see `constants.py` for details).
5. Edit `json_payload` in `worker.py` to match your filtering needs. **(Advance)**
6. Run the script:
   ```bash
   uv run worker.py
   ```

## Configuration

The script uses environment variables to configure the PhotoPrism API connection and other settings. You can create a `.env` file with the following variables:

| Variable               | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `NODE_NAME`            | Name of the node for distributed processing (optional).                    |
| `PHOTOPRISM_ROOT_URL`  | Base URL of your PhotoPrism instance.                                      |
| `PHOTOPRISM_TOKEN`     | API token for authenticating with PhotoPrism.                              |
| `DISTRIBUTED_PROCESSING` | Enable distributed processing (1 for enabled, 0 for disabled).            |
| `DB_HOST`              | Hostname or IP address of the database server (required only if `DISTRIBUTED_PROCESSING=1`). |
| `DB_PORT`              | Port number for the database connection (default: 3306, required only if `DISTRIBUTED_PROCESSING=1`). |
| `DB_USER`              | Username for the database connection (required only if `DISTRIBUTED_PROCESSING=1`). |
| `DB_PASSWORD`          | Password for the database connection (required only if `DISTRIBUTED_PROCESSING=1`). |
| `DB_DATABASE`          | Name of the database to use (required only if `DISTRIBUTED_PROCESSING=1`). |
| `CAPTION_MODEL`        | AI model to use for caption generation (Default is `florence2`).                |
| `CAPTION_BATCH_SIZE`   | Number of photos to process in a single batch for caption generation. **Note:** Higher batch sizes require more GPU VRAM. Adjust based on your hardware capabilities. |
| `YOLO_MODEL`           | Ultralytics YOLO model to use for image tagging.                             |
| `YOLO_CONFIDENCE`      | Confidence threshold for YOLO tagging (0.0 to 1.0).                       |
| `CLEANUP`              | Enable cleanup of stale job (1 for enabled, 0 for disabled).         |
| `CLEANUP_STALE_HOURS`  | Number of hours after which stale job are cleaned up.                    |
| `PHOTO_START_OFFSET`   | Offset for starting photo processing (useful for resuming).                |
| `TOKENIZERS_PARALLELISM` | Enable or disable parallelism for tokenizers (For Debug).                |
| `FULL_SCAN`            | Perform a full scan of the PhotoPrism library (For Debug). |

## Troubleshooting

- Ensure your PhotoPrism API credentials are correct and the API is accessible.
- Check the console output for error messages or exceptions.
- If GPU installation issues occur, try reinstalling PyTorch and transformers with the `--no-deps` flag.