# Define output structure for gemini 
from pydantic import BaseModel, Field
from typing import Optional

class FoundItem(BaseModel):
    """
    Represents an item recorded on a Found Article Form. 

    Enforces a structured JSON output from the Gemini API when parsing
    handwritten lost and found paperwork. It maps the sections of the physical paper
    to columns of the spreadsheet. 
    """
    is_valid_form: bool = Field(
        description="True if model believes the image was not a Found Item form."
    )
    item_number: Optional[int] = Field(
        description="The number next to 'ARTICLE #'", 
        default=None
    )
    description: Optional[str] = Field(
        description="The text next to 'Description of Found Item' (Do your best to infer a reasonable description if the handwriting is very unclear in places)", 
        default=None
    )
    category: Optional[str] = Field(
        description="Infer a 1-2 word category based on the description (e.g., Electronics, Clothing)", 
        default=None
    )
    location_found: Optional[str] = Field(
        description="The text next to 'Where Found'", 
        default=None
    )
    matched_with_lost_item: Optional[bool] = Field(
        description="True if 'Name', 'Address', 'Day Time Phone', or 'Email' under 'Found Item Belongs To' are filled, otherwise False", 
        default=None
    )
    returned_to_owner: Optional[bool] = Field(
        description="True if 'Name', 'Address', 'Day Time Phone', or 'Email' under 'Found Item Belongs To' are filled, otherwise False", 
        default=None
    )

class LostItem(BaseModel):
    """
    Represents an item recorded on a Lost Article Form. 

    Enforces a structured JSON output from the Gemini API when parsing
    handwritten lost and found paperwork. It maps the sections of the physical paper
    to columns of the spreadsheet. 
    """
    is_valid_form: bool = Field(
        description="True if model believes the image was not a Lost Item form."
    )