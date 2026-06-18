import logging
import pytest
from src.services.ai_service import extract_found_item_data
from src.models.llm_schemas import FoundItem


@pytest.fixture
def found_item():
    return FoundItem(
        item_number="001",
        description="Blue umbrella",
        category="Accessories",
        location_found="Gate 4",
        matched_with_lost_item=False,
        returned_to_owner=False,
    )


def test_returns_found_item_on_success(dummy_image, mock_client, found_item):
    mock_client.models.generate_content.return_value.parsed = found_item

    result = extract_found_item_data(dummy_image, client=mock_client)

    assert result == found_item


def test_returns_none_when_parsed_is_none(dummy_image, mock_client, caplog):
    mock_client.models.generate_content.return_value.parsed = None
    mock_client.models.generate_content.return_value.text = "raw response text"

    with caplog.at_level(logging.ERROR, logger="src.services.ai_service"):
        result = extract_found_item_data(dummy_image, client=mock_client)

    assert result is None
    assert "parsed result is None" in caplog.text


def test_returns_none_on_exception(dummy_image, mock_client, caplog):
    mock_client.models.generate_content.side_effect = Exception("API error")

    with caplog.at_level(logging.ERROR, logger="src.services.ai_service"):
        result = extract_found_item_data(dummy_image, client=mock_client)

    assert result is None
    assert "Failed to extract data" in caplog.text
