import os
import pytest
from unittest.mock import AsyncMock, patch, mock_open
import elasticsearch
# Mock AsyncElasticsearch globally before any import
elasticsearch.AsyncElasticsearch = AsyncMock

# Provide default env vars to prevent errors in main.py
os.environ.setdefault("ES_CLOUD_URL", "http://localhost:9200")
os.environ.setdefault("ES_API_KEY", "dummy_key")

from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_elasticsearch():
    mock_es = AsyncMock()
    with patch("routers.product.es", mock_es), \
         patch("routers.ner.es", mock_es):
        yield mock_es

@pytest.fixture
def mock_gemini():
    with patch("routers.image.genai.GenerativeModel") as mock:
        yield mock

@pytest.fixture
def mock_smtp():
    with patch("smtplib.SMTP") as mock:
        yield mock

@pytest.fixture
def mock_pdf():
    with patch("builtins.open", new_callable=mock_open, read_data=b"fake_pdf_data") as mock:
        yield mock

@pytest.fixture
def sample_image():
    return b"fake_image_data"
