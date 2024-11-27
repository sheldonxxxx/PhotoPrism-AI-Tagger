

**PhotoPrism Caption Generator**
=====================================

### Overview
------------

This project is a Python-based caption generator for PhotoPrism, a self-hosted photo management platform. It uses AI models to generate captions for photos and updates the PhotoPrism database with the generated captions.

### AI Model
------------
Caption: Kosmos-2
Tag: Yolov11x

### Requirements
---------------

* Python 3.10+
* PhotoPrism instance with API access
* GPU (optional but recommended for faster processing)

### Installation
---------------

#### CPU Installation

1. Clone the repository: `git clone https://github.com/sheldonchiu/PhotoPrism-AI-Tagger.git`
2. Install torch: `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu`
3. Install dependencies: `pip install -r requirements.txt`
4. Rename `.env1` to `.env` and fill it with your PhotoPrism API credentials and other configuration settings (see `constants.py` for details)
5. Edit `json_payload` in worker.py to match your own filtering needs
6. Run the script: `python worker.py`

#### GPU Installation (Linux)

1. Install CUDA and cuDNN (if not already installed)
2. Install the GPU version of PyTorch: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
3. Install the GPU version of transformers: `pip install transformers --index-url https://download.pytorch.org/whl/cu118`
4. Clone the repository: `git clone https://github.com/sheldonchiu/PhotoPrism-AI-Tagger.git`
5. Install dependencies: `pip install -r requirements.txt`
6. Rename `.env1` to `.env` and fill it with your PhotoPrism API credentials and other configuration settings (see `constants.py` for details)
7. Edit `json_payload` in worker.py to match your own filtering needs
8. Run the script: `python worker.py`

#### GPU Installation (Mac)

1. Install PyTorch: `pip install torch torchvision torchaudio`
2. Clone the repository: `git clone https://github.com/sheldonchiu/PhotoPrism-AI-Tagger.git`
3. Install dependencies: `pip install -r requirements.txt`
4. Rename `.env1` to `.env` and fill it with your PhotoPrism API credentials and other configuration settings (see `constants.py` for details)
5. Edit `json_payload` in worker.py to match your own filtering needs
6. Run the script: `python worker.py`


### Configuration
--------------

The script uses environment variables to configure the PhotoPrism API connection and other settings. You can create a `.env` file with the following variables:

* `PHOTOPRISM_ROOT_URL`: the URL of your PhotoPrism instance
* `PHOTOPRISM_TOKEN`: your PhotoPrism API token
* `NODE_NAME`: a unique identifier for this worker (default: `worker1`)
* `TEMP_PHOTO_DIR`: a temporary directory for storing downloaded photos (default: `/tmp`)

### Usage
-----

1. Run the script: `python worker.py`
2. The script will start processing photos in batches, generating captions and updating the PhotoPrism database.
3. You can monitor the progress and any errors in the console output.

### Troubleshooting
------------------

* Make sure your PhotoPrism API credentials are correct and the API is accessible.
* Check the console output for any error messages or exceptions.
* If you encounter issues with the GPU installation, try reinstalling PyTorch and transformers with the `--no-deps` flag.