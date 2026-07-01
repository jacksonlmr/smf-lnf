from typing import List
import zipfile
import io

import pandas as pd
from PIL.ImageFile import ImageFile

from src.models.llm_schemas import FoundItem

COLUMNS = [
    "Item Number",
    "Description",
    "Category",
    "Location Found",
    "Matched with Lost Item",
    "Returned to Owner",
]


def to_dataframe(items: List[FoundItem | None]) -> pd.DataFrame:
    rows: list[dict[str, str | bool | int | None]] = [
        {
            "Is Valid Form": item.is_valid_form,
            "Item Number": item.item_number,
            "Description": item.description,
            "Category": item.category,
            "Location Found": item.location_found,
            "Matched with Lost Item": item.matched_with_lost_item,
            "Returned to Owner": item.returned_to_owner,
        }
        for item in items
        if item is not None
    ]
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=COLUMNS)

def generate_img_zip(imgs: List[ImageFile]):
    """
    Generates a zip file from a list of PIL images
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for i, pil_image in enumerate(imgs):
            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format="JPEG")
            img_bytes = img_buffer.getvalue()

            zip_file.writestr(f"invalid_img_{i}.jpg", img_bytes)

    zip_buffer.seek(0)
    return zip_buffer

