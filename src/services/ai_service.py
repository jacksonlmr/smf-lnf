import PIL.Image
from google import genai
from google.genai import types

from src.core.config import GEMINI_API_KEY
from src.models.llm_schemas import FoundItem

# Initialize ai client
client = genai.Client(api_key=GEMINI_API_KEY)

def extract_found_item_data(image: PIL.Image.Image) -> FoundItem | None:
    """
    Takes an image file path, sends it to Gemini, and returns a validated FoundItem object.
    """
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
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
        
        # response.parsed contains the populated FoundItem Python object
        return response.parsed
        
    except Exception as e:
        print(f"Failed to extract data from image: {e}")
        return None