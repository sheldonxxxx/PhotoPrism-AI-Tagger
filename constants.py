import os
import tempfile
import dotenv

dotenv.load_dotenv()

# Helper function to convert string to boolean
bool_t = lambda x: x.lower() in ['true', 'yes', '1']

# Photoprism configuration
PHOTOPRISM_ROOT_URL = os.environ.get('PHOTOPRISM_ROOT_URL')  # Base URL for Photoprism
PHOTOPRISM_PHOTO_API = os.environ.get('PHOTOPRISM_PHOTO_API', "/api/v1/photos")  # API endpoint for photos
PHOTOPRISM_DL_API = os.environ.get('PHOTOPRISM_DL_API', "/api/v1/dl/{hash}")  # API endpoint for downloading photos
PHOTOPRISM_TOKEN = os.environ.get('PHOTOPRISM_TOKEN')  # Authentication token for Photoprism

# Distributed processing configuration
DP = bool_t(os.environ.get('DISTRIBUTED_PROCESSING', '0'))  # Enable or disable distributed processing

if DP:
    # Database configuration for distributed processing
    DB_HOST = os.environ.get('DB_HOST')  # Database host
    DB_PORT = int(os.environ.get('DB_PORT'))  # Database port
    DB_USER = os.environ.get('DB_USER')  # Database username
    DB_PASSWORD = os.environ.get('DB_PASSWORD')  # Database password
    DB_DATABASE = os.environ.get('DB_DATABASE')  # Database name
else:
    # Local database file path
    DB_PATH = os.environ.get('DB_PATH', 'photo_tasks.db')  # Path to local SQLite database

# Node configuration
NODE_NAME = os.environ.get('NODE_NAME')  # Name of the processing node

# Temporary directory for photo storage
TEMP_PHOTO_DIR = os.environ.get('TEMP_PHOTO_DIR', tempfile.gettempdir())

# Scanning and model configuration
FULL_SCAN = bool_t(os.environ.get('FULL_SCAN', '0'))  # Enable or disable full scan mode
CAPTION_MODEL = os.environ.get('CAPTION_MODEL', 'florence2')  # Default captioning model
KOSMOS2_MODEL = os.environ.get('KOSMOS2_MODEL', 'microsoft/kosmos-2-patch14-224')  # Kosmos-2 model
FLORENCE2_MODEL = os.environ.get('FLORENCE2_MODEL', "microsoft/Florence-2-base")  # Florence-2 model
CAPTION_BATCH_SIZE = int(os.environ.get('CAPTION_BATCH_SIZE', 1))  # Batch size for captioning

# YOLO model configuration
YOLO_MODEL = os.environ.get('YOLO_MODEL', 'yolo11x-cls.pt')  # YOLO model file
YOLO_CONFIDENCE = float(os.environ.get('YOLO_CONFIDENCE', 0.7))  # Confidence threshold for YOLO model

CLEANUP = bool_t(os.environ.get('CLEANUP', '0'))  # Enable or disable cleanup before processing
CLEANUP_STALE_HOURS = int(os.environ.get('CLEANUP_STALE_HOURS', 24))  # Stale hours for cleanup

RESUME = bool_t(os.environ.get('RESUME', '0'))  # Enable or disable resume mode