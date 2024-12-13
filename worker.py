import os
import sys
import utils
import constants
from detection import DescriptionGenerator, Classifier
from job_queue import PhotoProcessor
from PIL import Image

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

offset = constants.PHOTO_START_OFFSET

headers = {
    "X-Auth-Token": constants.PHOTOPRISM_TOKEN,
}

count = 50
processor = PhotoProcessor(worker_id=constants.NODE_NAME)
caption_processor = DescriptionGenerator()
yolo_processor = Classifier()

while True:
    json_payload = {
        "count": count,
        "offset": offset,
        "order": "added",
        "photo": True,
        "primary": True,
    }
    
    photo_response = utils.get_photos(json_payload, headers)
    logger.info(f"Successfully got photo details with offset {offset}")
    
    if photo_response:
        token = photo_response.headers["X-Download-Token"]
        photos = photo_response.json()
        
        if len(photos) == 0:
            logger.info("No more photos to process, will stop here")
            break
        
        for i in range(0, len(photos), constants.CAPTION_BATCH_SIZE):
            end = i + constants.CAPTION_BATCH_SIZE
            if end > len(photos):
                end = None
            batch = photos[i:end]
            batch_data = []
            stop_signal = False
            for photo in batch:
                photo_uid = photo['UID']
                if not constants.FULL_SCAN and photo['Description']:
                    logger.info(f"Photo {photo_uid} already has description, assuming all complete, if not, please re-run with env var FULL_SCAN=1")
                    sys.exit(0)
                
                status = processor.try_acquire_photo(photo_uid)
                if not status:
                    # Photo is already being processed by another worker
                    continue
            
                photo_hash = photo['Hash']
                filename =  os.path.basename(photo['FileName'])
                save_path = os.path.join(constants.TEMP_PHOTO_DIR, filename)
                status = utils.download_image(token, photo_hash, save_path, headers)
                if not status:
                    stop_signal = True
                    processor.mark_complete(photo_uid, "Error")
                    break
                logger.info(f"Image {photo_uid} downloaded and saved to: {save_path}")
                batch_data.append((photo_uid, save_path))
                
            if stop_signal or not batch_data:
                continue
                
            images = [Image.open(save_path) for _, save_path in batch_data]
            captions = caption_processor.generate(images)
            if not captions:
                for photo_uid, _ in batch_data:
                    processor.mark_complete(photo_uid, "Error")
                continue
            logger.info(f"Generated caption for {', '.join([photo_uid for photo_uid, _ in batch_data])}")
            
            labels = yolo_processor.classify(images)
            logger.info(f"Detected labels for {', '.join([photo_uid for photo_uid, _ in batch_data])}")
            
            for data, caption, label in zip(batch_data, captions, labels):
                photo_uid, save_path = data
                request_data = {
                    "Description": caption,
                    "DescriptionSrc": "manual",
                }
                update_response = utils.update_photo_detail(photo_uid,request_data, headers)
                
                if update_response:
                    logger.info(f"Updated description for {photo_uid}")
                    detail = update_response.json()['Details']
                    keywords = ','.join(detail['Keywords'].split(',') + label)
                    
                    detail['Keywords'] = keywords
                    detail['KeywordsSrc'] = "manual"
                    
                    request_data = {
                        "Details": detail,
                    }
                    logger.debug(f"Updated keywords for {photo_uid}: {keywords}")
                    
                    update_response = utils.update_photo_detail(photo_uid,request_data, headers)
                    if update_response:
                        logger.info(f"Updated keywords for {photo_uid}")
                        processor.mark_complete(photo_uid)
                        logger.info(f"Marked photo {photo_uid} complete")
                        
                        # Avoid duplicate photo file having different id
                        if os.path.exists(save_path):
                            os.remove(save_path)
            
    else:
        logger.error(f"Error while processing offset {offset}, will stop here")
        break
    
    offset += count
    
