import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from main import app  # thay main bằng tên file app của bạn

@pytest.fixture
def client():
    """Khởi tạo TestClient cho FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_elasticsearch(monkeypatch):
    """Mock Elasticsearch client async cho các test."""
    mock = MagicMock()
    mock.search = AsyncMock()
    # Thay "main.es_client" thành đúng biến Elasticsearch client trong app bạn
    monkeypatch.setattr("main.es", mock)
    return mock

def test_ner_success(client, mock_elasticsearch):
    """Kiểm tra phân tích thành phần khi dữ liệu trả về thành công từ Elasticsearch."""
    mock_elasticsearch.search.return_value = {
        "hits": {
            "hits": [
                {"_source": {"ingredients": {"MUỐI": {"score": 90}}}},
                {"_source": {"ingredients": {"ĐƯỜNG": {"score": 80}}}}
            ]
        }
    }
    response = client.post("/api/ner/name-entity-recognition", json={"content": "muối, đường"})
    assert response.status_code == 200

def test_ner_elasticsearch_error(client, mock_elasticsearch):
    """Kiểm tra phản hồi khi Elasticsearch xảy ra lỗi (ví dụ: exception)."""
    mock_elasticsearch.search.side_effect = Exception("Elasticsearch error")
    response = client.post("/api/ner/name-entity-recognition", json={"content": "muối"})
    assert response.status_code == 200

def test_ner_empty_content(client):
    """Kiểm tra phản hồi khi nội dung đầu vào là chuỗi rỗng."""
    response = client.post("/api/ner/name-entity-recognition", json={"content": ""})
    assert response.status_code == 200

def test_ner_no_ingredients(client, mock_elasticsearch):
    """Kiểm tra trường hợp văn bản không chứa thành phần nào trong kết quả tìm kiếm."""
    mock_elasticsearch.search.return_value = {"hits": {"hits": []}}
    response = client.post("/api/ner/name-entity-recognition", json={"content": "abc xyz"})
    assert response.status_code == 200

def test_ner_special_chars_content(client, mock_elasticsearch):
    """Kiểm tra xử lý nội dung chứa ký tự đặc biệt mà không có thành phần."""
    mock_elasticsearch.search.return_value = {"hits": {"hits": []}}
    response = client.post("/api/ner/name-entity-recognition", json={"content": "@#$%"})
    assert response.status_code == 200

def test_ner_long_content(client, mock_elasticsearch):
    """Kiểm tra xử lý văn bản rất dài (lặp lại từ nhiều lần)."""
    long_content = "muối " * 1000
    mock_elasticsearch.search.return_value = {
        "hits": {"hits": [{"_source": {"ingredients": {"MUỐI": {"score": 90}}}}]}
    }
    response = client.post("/api/ner/name-entity-recognition", json={"content": long_content})
    assert response.status_code == 200

def test_ner_non_english_content(client, mock_elasticsearch):
    """Kiểm tra xử lý văn bản tiếng nước ngoài không có thành phần trong kết quả."""
    mock_elasticsearch.search.return_value = {"hits": {"hits": []}}
    response = client.post("/api/ner/name-entity-recognition", json={"content": "salt, sugar"})
    assert response.status_code == 200
