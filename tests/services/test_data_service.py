import pandas as pd
import pytest

from src.models.llm_schemas import FoundItem
from src.services.data_service import COLUMNS, to_dataframe


def make_item(item_number: str = "1", description: str = "A wallet", category: str = "Accessories",
              location_found: str = "Lobby", matched: bool = False, returned: bool = False) -> FoundItem:
    return FoundItem(
        item_number=item_number,
        description=description,
        category=category,
        location_found=location_found,
        matched_with_lost_item=matched,
        returned_to_owner=returned,
    )


def test_empty_list_returns_empty_dataframe_with_columns():
    df = to_dataframe([])
    assert list(df.columns) == COLUMNS
    assert len(df) == 0


def test_all_none_returns_empty_dataframe_with_columns():
    df = to_dataframe([None, None, None])
    assert list(df.columns) == COLUMNS
    assert len(df) == 0


def test_single_item_maps_fields_correctly():
    item = make_item(item_number="42", description="Blue umbrella", category="Accessories",
                     location_found="Gate B", matched=True, returned=False)
    df = to_dataframe([item])
    assert len(df) == 1
    row = df.iloc[0]
    assert row["Item Number"] == "42"
    assert row["Description"] == "Blue umbrella"
    assert row["Category"] == "Accessories"
    assert row["Location Found"] == "Gate B"
    assert row["Matched with Lost Item"] == True
    assert row["Returned to Owner"] == False


def test_mixed_list_skips_none_and_preserves_order():
    item_a = make_item(item_number="1")
    item_b = make_item(item_number="2")
    df = to_dataframe([item_a, None, item_b, None])
    assert len(df) == 2
    assert df.iloc[0]["Item Number"] == "1"
    assert df.iloc[1]["Item Number"] == "2"
