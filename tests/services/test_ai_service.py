import logging
import pytest
import PIL.ImageFile
from typing import Callable, Awaitable, Any, cast
from unittest.mock import AsyncMock
from google import genai
from src.services.ai_service import extract_found_item_data, process_images_concurrently
from src.models.llm_schemas import FoundItem

ProcessingFunc = Callable[[PIL.ImageFile.ImageFile, Any], Awaitable[FoundItem | None]]


@pytest.fixture
def found_item() -> FoundItem:
    return FoundItem(
        item_number="001",
        description="Blue umbrella",
        category="Accessories",
        location_found="Gate 4",
        matched_with_lost_item=False,
        returned_to_owner=False,
    )


class TestExtractFoundItemData:
    async def test_returns_found_item_on_success(
        self,
        dummy_image: PIL.ImageFile.ImageFile,
        mock_client: genai.client.AsyncClient,
        found_item: FoundItem,
    ) -> None:
        gen_content = cast(AsyncMock, mock_client.models.generate_content)
        gen_content.return_value.parsed = found_item

        result = await extract_found_item_data(dummy_image, client=mock_client)

        assert result == found_item

    async def test_returns_none_when_parsed_is_none(
        self,
        dummy_image: PIL.ImageFile.ImageFile,
        mock_client: genai.client.AsyncClient,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        gen_content = cast(AsyncMock, mock_client.models.generate_content)
        gen_content.return_value.parsed = None
        gen_content.return_value.text = "raw response text"

        with caplog.at_level(logging.ERROR, logger="src.services.ai_service"):
            result = await extract_found_item_data(dummy_image, client=mock_client)

        assert result is None
        assert "parsed result is None" in caplog.text

    async def test_returns_none_on_exception(
        self,
        dummy_image: PIL.ImageFile.ImageFile,
        mock_client: genai.client.AsyncClient,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        gen_content = cast(AsyncMock, mock_client.models.generate_content)
        gen_content.side_effect = Exception("API error")

        with caplog.at_level(logging.ERROR, logger="src.services.ai_service"):
            result = await extract_found_item_data(dummy_image, client=mock_client)

        assert result is None
        assert "Failed to extract data" in caplog.text


class TestProcessImagesConcurrently:
    async def test_empty_list_returns_empty(self, mock_client: genai.client.AsyncClient) -> None:
        mock_func = cast(ProcessingFunc, AsyncMock(return_value=None))
        result = await process_images_concurrently(mock_func, [], client=mock_client)
        assert result == []

    async def test_single_image_returns_single_result(
        self,
        mock_client: genai.client.AsyncClient,
        dummy_image: PIL.ImageFile.ImageFile,
        found_item: FoundItem,
    ) -> None:
        mock_func = cast(ProcessingFunc, AsyncMock(return_value=found_item))
        result = await process_images_concurrently(mock_func, [dummy_image], client=mock_client)
        assert result == [found_item]

    async def test_multiple_images_results_in_order(
        self,
        mock_client: genai.client.AsyncClient,
        dummy_image: PIL.ImageFile.ImageFile,
    ) -> None:
        item_a = FoundItem(
            item_number="001",
            description="Red scarf",
            category="Clothing",
            location_found="Lobby",
            matched_with_lost_item=False,
            returned_to_owner=False,
        )
        item_b = FoundItem(
            item_number="002",
            description="Black wallet",
            category="Accessories",
            location_found="Gate 7",
            matched_with_lost_item=True,
            returned_to_owner=True,
        )
        raw_mock = AsyncMock(side_effect=[item_a, item_b])
        mock_func = cast(ProcessingFunc, raw_mock)
        result = await process_images_concurrently(mock_func, [dummy_image, dummy_image], client=mock_client)
        assert result == [item_a, item_b]

    async def test_partial_failure_preserves_none(
        self,
        mock_client: genai.client.AsyncClient,
        dummy_image: PIL.ImageFile.ImageFile,
        found_item: FoundItem,
    ) -> None:
        mock_func = cast(ProcessingFunc, AsyncMock(side_effect=[found_item, None]))
        result = await process_images_concurrently(mock_func, [dummy_image, dummy_image], client=mock_client)
        assert result == [found_item, None]

    async def test_client_passed_to_processing_func(
        self,
        mock_client: genai.client.AsyncClient,
        dummy_image: PIL.ImageFile.ImageFile,
        found_item: FoundItem,
    ) -> None:
        raw_mock = AsyncMock(return_value=found_item)
        mock_func = cast(ProcessingFunc, raw_mock)
        await process_images_concurrently(mock_func, [dummy_image], client=mock_client)
        raw_mock.assert_called_once_with(dummy_image, mock_client)
