import os
os.environ.setdefault("GEMINI_API_KEY", "fake-test-key")

import pytest
import PIL.Image
import PIL.ImageFile
from typing import cast
from unittest.mock import AsyncMock
from pytest_mock import MockerFixture
from google import genai


@pytest.fixture
def dummy_image() -> PIL.ImageFile.ImageFile:
    return cast(PIL.ImageFile.ImageFile, PIL.Image.new("RGB", (100, 100), color="white"))


@pytest.fixture
def mock_client(mocker: MockerFixture) -> genai.client.AsyncClient:
    client = mocker.MagicMock()
    client.models.generate_content = AsyncMock()
    return cast(genai.client.AsyncClient, client)
