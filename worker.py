import os
import sys
import utils
import constants
from detection import Kosmos2DescriptionGenerator, Florence2DescriptionGenerator, Classifier
from job_queue import PhotoProcessor
from PIL import Image

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize offset and headers for API requests
offset = constants.PHOTO_START_OFFSET

headers = {
    "X-Auth-Token": constants.PHOTOPRISM_TOKEN,
}

# Set batch size and initialize the photo processor
count = 50
processor = PhotoProcessor(worker_id=constants.NODE_NAME)

# Select the appropriate caption generator based on configuration
if constants.CAPTION_MODEL == "florence2":
    caption_processor = Florence2DescriptionGenerator()
elif constants.CAPTION_MODEL == "kosmos2":
    caption_processor = Kosmos2DescriptionGenerator()
else:
    logger.error(f"Invalid caption model {constants.CAPTION_MODEL}")
    sys.exit(-1)

# Initialize the classifier for label detection
yolo_processor = Classifier()

if constants.CLEANUP:
    # Clean up stale tasks if enabled
    processor.cleanup_stale_tasks(constants.CLEANUP_STALE_HOURS)
    logger.info(f"Cleaned up stale tasks older than {constants.CLEANUP_STALE_HOURS} hours")

# Main processing loop
while True:
    # Prepare the payload for fetching photos
    json_payload = {
        "count": count,
        "offset": offset,
        "order": "added",
        "photo": True,
        "primary": True,
    }
    
    # Fetch photo details from the API
    photo_response = utils.get_photos(json_payload, headers)
    logger.info(f"Successfully got photo details with offset {offset}")
    
    if photo_response:
        token = photo_response.headers["X-Download-Token"]
        photos = photo_response.json()
        
        # Stop processing if no photos are returned
        if len(photos) == 0:
            logger.info("No more photos to process, will stop here")
            break
        
        # Process photos in batches
        for i in range(0, len(photos), constants.CAPTION_BATCH_SIZE):
            end = i + constants.CAPTION_BATCH_SIZE
            if end > len(photos):
                end = None
            batch = photos[i:end]
            batch_data = []
            stop_signal = False
            
            # Process each photo in the batch
            for photo in batch:
                photo_uid = photo['UID']
                
                # Skip photos that already have captions unless FULL_SCAN is enabled
                if not constants.FULL_SCAN and photo['Caption']:
                    logger.info(f"Photo {photo_uid} already has caption, assuming all complete, if not, please re-run with env var FULL_SCAN=1")
                    sys.exit(0)
                
                # Try to acquire the photo for processing
                status = processor.try_acquire_photo(photo_uid)
                if not status:
                    # Photo is already being processed by another worker
                    continue
            
                # Download the photo
                photo_hash = photo['Hash']
                filename = os.path.basename(photo['FileName'])
                save_path = os.path.join(constants.TEMP_PHOTO_DIR, filename)
                status = utils.download_image(token, photo_hash, save_path, headers)
                if not status:
                    stop_signal = True
                    processor.mark_complete(photo_uid, "Error")
                    break
                logger.info(f"Image {photo_uid} downloaded and saved to: {save_path}")
                batch_data.append((photo_uid, save_path))
                
            # Skip further processing if there was an error or no valid batch data
            if stop_signal or not batch_data:
                continue
                
            # Generate captions for the batch of images
            images = [Image.open(save_path) for _, save_path in batch_data]
            captions = caption_processor.generate(images)
            if not captions:
                for photo_uid, _ in batch_data:
                    processor.mark_complete(photo_uid, "Error")
                continue
            logger.info(f"Generated caption for {', '.join([photo_uid for photo_uid, _ in batch_data])}")
            
            # Classify images to detect labels
            labels = yolo_processor.classify(images)
            logger.info(f"Detected labels for {', '.join([photo_uid for photo_uid, _ in batch_data])}")
            
            # Update photo details with captions and labels
            for data, caption, label in zip(batch_data, captions, labels):
                photo_uid, save_path = data
                request_data = {
                    "Caption": caption,
                    "CaptionSrc": "manual",
                }
                update_response = utils.update_photo_detail(photo_uid, request_data, headers)
                
                if update_response:
                    logger.info(f"Updated caption for {photo_uid}")
                    detail = update_response.json()['Details']
                    
                    # Append new labels to existing keywords
                    keywords = ','.join(detail['Keywords'].split(',') + label)
                    detail['Keywords'] = keywords
                    detail['KeywordsSrc'] = "manual"
                    
                    request_data = {
                        "Details": detail,
                    }
                    logger.debug(f"Updated keywords for {photo_uid}: {keywords}")
                    
                    update_response = utils.update_photo_detail(photo_uid, request_data, headers)
                    if update_response:
                        logger.info(f"Updated keywords for {photo_uid}")
                        processor.mark_complete(photo_uid)
                        logger.info(f"Marked photo {photo_uid} complete")
                        
                        # Remove the temporary photo file
                        if os.path.exists(save_path):
                            try:
                                os.remove(save_path)
                            except Exception as e:
                                logger.error(f"Error removing file {save_path}: {e}")
            
    else:
        # Log an error and stop processing if the API call fails
        logger.error(f"Error while processing offset {offset}, will stop here")
        break
    
    # Increment the offset for the next batch
    offset += count

