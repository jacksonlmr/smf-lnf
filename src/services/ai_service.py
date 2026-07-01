import logging
import PIL.Image
from PIL.ImageFile import ImageFile
from google import genai
from google.genai import types
from google.genai.errors import ClientError
import asyncio
from typing import Callable, List, Any, Awaitable, Dict, cast

from src.core.config import GEMINI_API_KEY, GEMINI_MODEL
from src.models.llm_schemas import FoundItem, LostItem

logger = logging.getLogger(__name__)
async_client = genai.Client(api_key=GEMINI_API_KEY).aio

# Retry config for 429 status codes
global_retry_options = types.HttpRetryOptions(
                        initial_delay=1.0,
                        attempts=5,
                        http_status_codes=[429]
                    )

# Need to add logic to keep track of what images returned None so they can be further processed. 
async def process_images_concurrently(
    processing_func: Callable[[ImageFile, Any], Awaitable[Any]],
    images: List[ImageFile],
    client: genai.client.AsyncClient = async_client,
) -> Dict[str, List[FoundItem | LostItem | None] | List[ImageFile]]:
    """
    Asynchronously processes a list of images using the provided async function. Intended to populate FoundItem and LostItem objects. 
    
    Parameters
    ----------
    processing_func : Callable[[PIL.Image.ImageFile.ImageFile, Any], Awaitable[Any]]
        The async function to apply to each image.
    images : List[PIL.Image.ImageFile.ImageFile]
        List of PIL images to process.
    client: genai.client.AsyncClient
        The API client to pass to the processing function.
        
    Returns:
        A dict with the following key value pairs: 
        'results': List of successfully populated objects returned from processing_func. 

        'invalid_images': List of images unable to be processed correctly by processing_func.
    """

    # Dispatch all tasks
    tasks = [processing_func(img, client) for img in images]
    completed_tasks = await asyncio.gather(*tasks)
        
    # Extract images that were not correctly processed by processing_func
    invalid_images = []
    for i, img in enumerate(images):
        if completed_tasks[i] is None or not completed_tasks[i].is_valid_form:
            invalid_images.append(img)
    
    # asyncio.gather preserves the order of the inputs
    return {"results": completed_tasks, "invalid_images": invalid_images}

async def extract_found_item_data(image: ImageFile, client: genai.client.AsyncClient = async_client) -> FoundItem | None:
    """
    Takes an image file path, sends it to Gemini, and returns a validated FoundItem object.

    Parameters
    ----------
    image : ImageFile
        The image to be processed. 
    client : genai.Client
        The client to send requests to. 

    Returns 
    -------
    FoundItem
        FoundItem object with fields populated from the image, if successful. 
    None
        Returns None if the request was not executed, or the model returned an invalid format. 
    """
    try:
        # could potentially error if google removes support for the gemini model in GEMINI_MODEL
        response = await client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                "Analyze the image. If it is a 'Found Article Form', set 'is_valid_form' to True"
                "and extract the handwritten information according to the schema."
                "If the image is NOT a 'Found Article Form', (e.g., a random object, a landscape, or a different type of form)"
                "set 'is_valid_form' to False and leave the remaining fields null",
                image
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FoundItem,
                temperature=0.0,
                http_options=types.HttpOptions(
                    retry_options=global_retry_options
                )
            )
        )

        if response.parsed is None:
            raw = response.text
            logger.error("Gemini returned a response but parsed result is None. Raw response: %s", raw)
            return None
        
        return cast(FoundItem, response.parsed)

    except Exception as e:
        logger.exception("Failed to extract data from image: %s", e)
        return None
