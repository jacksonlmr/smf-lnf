# Define output structure for gemini 
from pydantic import BaseModel, Field

class FoundItem(BaseModel):
    """
    Represents an item recorded on a Found Article Form. 

    Enforces a structured JSON output from the Gemini API when parsing
    handwritten lost and found paperwork. It maps the sections of the physical paper
    to columns of the spreadsheet. 
    """
    item_number: str = Field(description="The number next to 'ARTICLE #'")
    description: str = Field(description="The text next to 'Description of Found Item' (Do your best to infer a reasonable description if the handwriting is very unclear in places)")
    category: str = Field(description="Infer a 1-2 word category based on the description (e.g., Electronics, Clothing)")
    location_found: str = Field(description="The text next to 'Where Found'")
    matched_with_lost_item: bool = Field(description="True if 'Name', 'Address', 'Day Time Phone', or 'Email' under 'Found Item Belongs To' are filled, otherwise False")
    returned_to_owner: bool = Field(description="True if 'Name', 'Address', 'Day Time Phone', or 'Email' under 'Found Item Belongs To' are filled, otherwise False")