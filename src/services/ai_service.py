import logging
import PIL.Image
from google import genai
from google.genai import types
import asyncio
from typing import Callable, List, Any, Awaitable
import typing

from src.core.config import GEMINI_API_KEY, GEMINI_MODEL
from src.models.llm_schemas import FoundItem

logger = logging.getLogger(__name__)
async_client = genai.Client(api_key=GEMINI_API_KEY).aio

# Need to add logic to keep track of what images returned None so they can be further processed. 
async def process_images_concurrently(
    processing_func: Callable[[PIL.Image.ImageFile.ImageFile, Any], Awaitable[Any]],
    images: List[PIL.Image.ImageFile.ImageFile],
    client: genai.client.AsyncClient = async_client,
    max_concurrent: int = 5
) -> List[Any | None]:
    """
    Asynchronously processes a list of images using the provided async function.
    
    Args:
        processing_func: The async function to apply to each image.
        images: List of PIL images to process.
        client: The API client to pass to the processing function.
        max_concurrent: Maximum number of active, simultaneous API calls.
        
    Returns:
        A list of results in the exact same order as the input images.
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def _safe_execute(img: PIL.Image.ImageFile.ImageFile) -> Any | None:
        async with semaphore:
            # Await the function directly; the SDK handles 429 retries
            return await processing_func(img, client)

    # Dispatch all tasks
    tasks = [_safe_execute(img) for img in images]
    
    # asyncio.gather preserves the order of the inputs
    return await asyncio.gather(*tasks)

async def extract_found_item_data(image: PIL.Image.ImageFile.ImageFile, client: genai.client.AsyncClient = async_client) -> FoundItem | None:
    """
    Takes an image file path, sends it to Gemini, and returns a validated FoundItem object.

    Parameters
    ----------
    image : PIL.Image.ImageFile.ImageFile
        The image to be processed. 
    client : genai.Client
        The client to send requests to. 

    Returns 
    -------
    FoundItem
        FoundItem object with fields populated from the image. 
    """
    try:
        # could potentially error if google removes support for the gemini model in GEMINI_MODEL
        response = await client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                "Extract the handwritten information from this 'Found Article Form' according to the schema.",
                image
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FoundItem,
                temperature=0.3
            )
        )

        if response.parsed is None:
            raw = response.text
            logger.error("Gemini returned a response but parsed result is None. Raw response: %s", raw)
            return None

        return typing.cast(FoundItem, response.parsed)

    except Exception as e:
        logger.exception("Failed to extract data from image: %s", e)
        return None
