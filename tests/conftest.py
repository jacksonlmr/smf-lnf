import os
os.environ.setdefault("GEMINI_API_KEY", "fake-test-key")

import pytest
import PIL.Image


@pytest.fixture
def dummy_image():
    return PIL.Image.new("RGB", (100, 100), color="white")


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()
