from typing import List

import pandas as pd

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
    rows: list[dict[str, str | bool]] = [
        {
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
