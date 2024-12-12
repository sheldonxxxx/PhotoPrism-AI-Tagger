import os
import dotenv

dotenv.load_dotenv()

bool_t = lambda x: x.lower() in ['true', 'yes', '1']

PHOTOPRISM_ROOT_URL = os.environ.get('PHOTOPRISM_ROOT_URL')
PHOTOPRISM_PHOTO_API = os.environ.get('PHOTOPRISM_PHOTO_API', "/api/v1/photos")
PHOTOPRISM_DL_API = os.environ.get('PHOTOPRISM_DL_API', "/api/v1/dl/{hash}")
PHOTOPRISM_TOKEN = os.environ.get('PHOTOPRISM_TOKEN')

DP = bool_t(os.environ.get('DISTRIBUTED_PROCESSING', '0'))

if DP:
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = int(os.environ.get('DB_PORT'))
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_DATABASE = os.environ.get('DB_DATABASE')
else:
    DB_PATH = os.environ.get('DB_PATH', 'photo_tasks.db')
    
PHOTO_START_OFFSET = int(os.environ.get('PHOTO_START_OFFSET', 0))

NODE_NAME = os.environ.get('NODE_NAME')

TEMP_PHOTO_DIR = os.environ.get('TEMP_PHOTO_DIR', '/tmp')

FULL_SCAN = bool_t(os.environ.get('FULL_SCAN', '0'))
CAPTION_MODEL = os.environ.get('CAPTION_MODEL', 'microsoft/kosmos-2-patch14-224')
CAPTION_BATCH_SIZE = int(os.environ.get('CAPTION_BATCH_SIZE', 1))
YOLO_MODEL = os.environ.get('CLS_MODEL', 'yolo11x-cls.pt')
YOLO_CONFIDENCE = float(os.environ.get('YOLO_CONFIDENCE', 0.7))
