import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from main import app  
from routers.image import genai

@pytest.fixture
def client():
    """Khởi tạo TestClient cho FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_elasticsearch(monkeypatch):
    """Mock Elasticsearch client async."""
    mock = MagicMock()
    mock.search = AsyncMock()
    monkeypatch.setattr("main.es", mock)  
    return mock

@pytest.fixture
def mock_gemini(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("google.generativeai", mock)  
    return mock

@pytest.fixture
def sample_image():
    # Ví dụ file ảnh nhị phân giả lập (bạn thay bằng ảnh thật nếu cần)
    return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00"

def test_search_and_safety_flow(client, mock_elasticsearch):
    """Kiểm tra luồng tìm kiếm và kiểm tra sản phẩm."""
    mock_elasticsearch.search.side_effect = [
        {
            "hits": {
                "hits": [{"_source": {"name": "Sản Phẩm A", "score": 85}, "_score": 12.5}],
                "total": {"value": 1}
            }
        },  # /search
        {
            "hits": {
                "hits": [{"_source": {"name": "Sản Phẩm A", "score": 85, "link_image": "url"}}]
            }
        }   # /safety
    ]
    search_response = client.post("/api/products/search", json={"keyword": "Sản", "page": 1, "size": 5})
    assert search_response.status_code == 200
    assert search_response.json()["products"][0]["name"] == "Sản Phẩm A"
    
    safety_response = client.post("/api/products/safety", json={"name": "Sản Phẩm A"})
    assert safety_response.status_code == 200
    assert safety_response.json()["name"] == "Sản Phẩm A"

def test_image_and_ner_flow(client, mock_gemini, mock_elasticsearch, sample_image):
    """Kiểm tra luồng nhận diện ảnh và phân tích thành phần."""
    mock_model = MagicMock()
    mock_model.generate_content.return_value = MagicMock(
        text='[{"description": "Muối, Đường", "score": 0.95}]'
    )
    mock_gemini.return_value = mock_model
    mock_elasticsearch.search.return_value = {
        "hits": {"hits": [{"_source": {"ingredients": {"MUỐI": {"score": 90}}}}]}
    }
    
    image_response = client.post(
        "/api/image/image-process",
        files={"file": ("test.jpg", sample_image, "image/jpeg")}
    )
    assert image_response.status_code == 200
    
    ner_response = client.post("/api/ner/name-entity-recognition", json={"content": "Muối, Đường"})
    assert ner_response.status_code == 200

def test_search_and_safety_search_fails(client, mock_elasticsearch):
    """Kiểm tra luồng khi /search thất bại."""
    mock_elasticsearch.search.side_effect = Exception("Elasticsearch error")
    search_response = client.post("/api/products/search", json={"keyword": "Sản", "page": 1, "size": 5})
    assert search_response.status_code == 500

def test_image_and_ner_image_fails(client, mock_gemini, sample_image):
    """Kiểm tra luồng khi /image-process thất bại."""
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("Gemini API error")
    mock_gemini.return_value = mock_model
    
    image_response = client.post(
        "/api/image/image-process",
        files={"file": ("test.jpg", sample_image, "image/jpeg")}
    )
    assert image_response.status_code == 500
