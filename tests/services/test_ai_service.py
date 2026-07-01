from typing import cast
import logging

import pytest
from unittest.mock import AsyncMock, MagicMock
from pytest_mock import MockerFixture
from google import genai
import PIL.Image
import PIL.ImageFile
from src.models.llm_schemas import FoundItem
from src.services.ai_service import extract_found_item_data


@pytest.fixture
def mock_client(mocker: MockerFixture) -> genai.client.AsyncClient:
    client = mocker.MagicMock()
    client.models.generate_content = AsyncMock()
    return cast(genai.client.AsyncClient, client)

@pytest.fixture
def dummy_image() -> PIL.ImageFile.ImageFile:
    return cast(PIL.ImageFile.ImageFile, PIL.Image.new("RGB", (100, 100), color="white"))

@pytest.fixture
def dummy_found_item() -> FoundItem: 
    return FoundItem (
        is_valid_form=True,
        item_number=69,
        description="Black hat with SF Giants Logo",
        category="Accessories",
        location_found="Music Meadow",
        matched_with_lost_item=False,
        returned_to_owner=False
    )

@pytest.fixture
def dummy_invalid_found_item() -> FoundItem:
    return FoundItem(
        is_valid_form=False,
    )

@pytest.mark.asyncio
async def test_efid_returns_correct_found_item(mock_client, dummy_found_item, dummy_image):
    """
    Ensures that extract_found_item_data returns a properly populated FoundItem object when executed successfully. 
    """
    mock_response = MagicMock()
    mock_response.parsed = dummy_found_item

    mock_client.models.generate_content.return_value = mock_response

    result = await extract_found_item_data(dummy_image, mock_client)

    assert result == dummy_found_item

@pytest.mark.asyncio
async def test_efid_returns_none_if_response_parsed_none(mock_client, dummy_image, caplog):
    """
    Tests that extract_found_item_data returns None if response.parsed is None
    """
    response_text = "Simulated raw API response"

    mock_response = MagicMock()
    mock_response.parsed = None
    mock_response.text = response_text

    mock_client.models.generate_content.return_value = mock_response

    with caplog.at_level(logging.ERROR):
        result = await extract_found_item_data(dummy_image, mock_client)

    assert result == None

    # ensure raw response is logged if parsed output is None
    assert "Gemini returned a response but parsed result is None. Raw response:" in caplog.text
    assert response_text in caplog.text

@pytest.mark.asyncio
async def test_efid_returns_none_on_exception(mock_client, dummy_image, caplog):
    """
    Tests that extract_found_item_data returns None if an exception is raised during the API call.
    """
    # Set the side_effect to raise an Exception when the mocked method is awaited
    error_message = "Simulated API failure"
    mock_client.models.generate_content.side_effect = Exception(error_message)

    with caplog.at_level(logging.ERROR):
        result = await extract_found_item_data(dummy_image, mock_client)

    assert result is None

    # ensure error is properly logged
    assert "Failed to extract data from image:" in caplog.text
    assert error_message in caplog.text

@pytest.mark.asyncio
async def test_efid_returns_invalid_form_object(mock_client, dummy_invalid_found_item, dummy_image):
    """
    Tests that the LLM determines the image is not a Found Article Form, the function
    returns the FoundItem object with is_valid_form=False. 
    """

    mock_response = MagicMock()
    mock_response.parsed = dummy_invalid_found_item

    mock_client.models.generate_content.return_value = mock_response

    result = await extract_found_item_data(dummy_image, mock_client)

    assert result == dummy_invalid_found_item

# test that process_images_concurrently returns a list of images that is_valid_form was False, or that returned None from extract_found_item_data