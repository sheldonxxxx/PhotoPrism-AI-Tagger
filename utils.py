import constants
import requests
import logging

logger = logging.getLogger(__name__)

def get_photos(json_payload, headers=None):
    """
    Makes a GET request to the given API URL with a JSON payload.

    Args:
        api_url (str): The URL of the API endpoint (e.g., '/api/v1/photos').
        json_payload (dict): The JSON data to send with the GET request.
        headers (dict): Optional HTTP headers to include in the request.

    Returns:
        Response: The response object from the request.
    """
    try:
        # Make the GET request with JSON payload
        api_url = f"{constants.PHOTOPRISM_ROOT_URL}{constants.PHOTOPRISM_PHOTO_API}"
        response = requests.get(api_url, headers=headers, params=json_payload)

        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Return the response object
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while getting photo details: {e}")
        return None
        
def download_image(token, hash, save_path, headers=None):
    """
    Download an image from PhotoPrism.
    """
    download_url = f"{constants.PHOTOPRISM_ROOT_URL}{constants.PHOTOPRISM_DL_API.format(hash=hash)}"
    
    try:
        response = requests.get(download_url, params={"t": token}, headers=headers, stream=True)
        response.raise_for_status()

        # Save the image locally
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while downloading image {photo_uid}: {e}")
        return False

def update_photo_detail(photo_uid, json_payload, headers=None):
    """
    Makes a GET request to the given API URL with a JSON payload.

    Args:
        json_payload (dict): The JSON data to send with the GET request.
        headers (dict): Optional HTTP headers to include in the request.

    Returns:
        Response: The response object from the request.
    """
    try:
        # Make the POST request with JSON payload
        api_url = f"{constants.PHOTOPRISM_ROOT_URL}{constants.PHOTOPRISM_PHOTO_API}/{photo_uid}"
        response = requests.put(api_url, headers=headers, json=json_payload)

        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Return the response object
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while updating photo details: {e}")
        return None