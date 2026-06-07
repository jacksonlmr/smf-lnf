import logging
import PIL.Image
from google import genai
from google.genai import types
import typing

from src.core.config import GEMINI_API_KEY
from src.models.llm_schemas import FoundItem

logger = logging.getLogger(__name__)
client = genai.Client(api_key=GEMINI_API_KEY)

def extract_found_item_data(image_path: str) -> FoundItem | None:
    """
    Takes an image file path, sends it to Gemini, and returns a validated FoundItem object.
    """
    try:
        image = PIL.Image.open(image_path)

        response = client.models.generate_content(
            model='gemini-2.5-flash',
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
            raw = response.text if hasattr(response, 'text') else str(response)
            logger.error("Gemini returned a response but parsed result is None. Raw response: %s", raw)
            return None

        return typing.cast(FoundItem, response.parsed)

    except Exception as e:
        logger.exception("Failed to extract data from image: %s", e)
        return None
