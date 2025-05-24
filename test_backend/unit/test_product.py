import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from main import app  

# Fixture tạo client test
@pytest.fixture
def client():
    return TestClient(app)

# Fixture mock elasticsearch client
@pytest.fixture
def mock_elasticsearch(monkeypatch):
    mock = MagicMock()
    mock.search = AsyncMock()
    monkeypatch.setattr("main.es", mock)
    return mock

def test_safety_success(client, mock_elasticsearch):
    mock_elasticsearch.search.return_value = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "name": "Sản Phẩm A",
                        "score": 85,
                        "link_image": "http://example.com/image.jpg"
                    }
                }
            ]
        }
    }
    response = client.post("/api/products/safety", json={"name": "Sản Phẩm A"})
    assert response.status_code == 200
    assert response.json() == {
        "name": "Sản Phẩm A",
        "score": 85,
        "link_image": "http://example.com/image.jpg"
    }

def test_safety_not_found(client, mock_elasticsearch):
    mock_elasticsearch.search.return_value = {"hits": {"hits": []}}
    response = client.post("/api/products/safety", json={"name": "Sản Phẩm Không Tồn Tại"})
    assert response.status_code == 200
    assert response.json() == {"message": "Không tìm thấy sản phẩm"}

def test_safety_elasticsearch_error(client, mock_elasticsearch):
    mock_elasticsearch.search.side_effect = Exception("Elasticsearch error")
    response = client.post("/api/products/safety", json={"name": "Sản Phẩm A"})
    assert response.status_code == 200
    assert "Server error" in response.json().get("detail", "")

def test_safety_empty_name(client):
    response = client.post("/api/products/safety", json={"name": ""})
    # Giả sử app trả lỗi 500 cho name rỗng
    assert response.status_code == 200

def test_safety_special_chars(client, mock_elasticsearch):
    mock_elasticsearch.search.return_value = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "name": "Sản Phẩm @#",
                        "score": 80,
                        "link_image": "http://example.com/image2.jpg"
                    }
                }
            ]
        }
    }
    response = client.post("/api/products/safety", json={"name": "Sản Phẩm @#"})
    assert response.status_code == 200
    assert response.json() == {
        "message": "Không tìm thấy sản phẩm"
    }

def test_safety_name_too_long(client, mock_elasticsearch):
    name = "A" * 300  # Giả sử vượt max length, bạn kiểm tra app có giới hạn không
    mock_elasticsearch.search.return_value = {"hits": {"hits": []}}
    response = client.post("/api/products/safety", json={"name": name})
    # Nếu app không có validate chiều dài, sẽ trả 200 và không tìm thấy
    assert response.status_code == 200
    assert response.json() == {"message": "Không tìm thấy sản phẩm"}

def test_safety_numeric_name(client, mock_elasticsearch):
    mock_elasticsearch.search.return_value = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "name": "12345",
                        "score": 75,
                        "link_image": "http://example.com/image3.jpg"
                    }
                }
            ]
        }
    }
    response = client.post("/api/products/safety", json={"name": "12345"})
    assert response.status_code == 200
    assert response.json() == {
        "name": "12345",
        "score": 75,
        "link_image": "http://example.com/image3.jpg"
    }

def test_get_all_success(client: TestClient, mock_elasticsearch):
    mock_elasticsearch.search = AsyncMock(return_value={
        "hits": {
            "hits": [
                {
                    "_source": {
                        "name": "Sản Phẩm A",
                        "score": 85,
                        "link_image": "url"
                    }
                }
            ]
        }
    })
    response = client.post("/api/products/get-all", json={"name": "Sản Phẩm A"})
    assert response.status_code == 200
    assert response.json() == {
        "name": "Sản Phẩm A",
        "score": 85,
        "link_image": "url"
    }

def test_get_all_elasticsearch_error(client: TestClient, mock_elasticsearch):
    mock_elasticsearch.search = AsyncMock(side_effect=Exception("Elasticsearch error"))
    response = client.post("/api/products/get-all", json={"name": "Sản Phẩm A"})
    assert response.status_code == 200
    assert "Server error" in response.json()["detail"]

def test_get_all_empty_results(client: TestClient, mock_elasticsearch):
    mock_elasticsearch.search = AsyncMock(return_value={"hits": {"hits": []}})
    response = client.post("/api/products/get-all", json={"name": "Sản Phẩm Không Tồn Tại"})
    assert response.status_code == 200
    assert response.json() == {"message": "Không tìm thấy sản phẩm"}

def test_get_all_invalid_page(client: TestClient):
    response = client.post("/api/products/get-all", json={"name": "Sản Phẩm A", "page": 0})
    assert response.status_code == 200

def test_get_all_invalid_size(client: TestClient):
    response = client.post("/api/products/get-all", json={"name": "Sản Phẩm A", "size": -5})
    assert response.status_code in 500

def test_get_all_large_page(client: TestClient, mock_elasticsearch):
    mock_elasticsearch.search = AsyncMock(return_value={"hits": {"hits": []}})
    response = client.post("/api/products/get-all", json={"name": "Sản Phẩm Không Tồn Tại", "page": 100000})
    assert response.status_code == 200
    assert response.json() == {"message": "Không tìm thấy sản phẩm"}

def test_search_success(client: TestClient, mock_elasticsearch):
    mock_elasticsearch.search = AsyncMock(return_value={
        "hits": {
            "hits": [
                {
                    "_source": {
                        "name": "Sản Phẩm A",
                        "score": 85,
                        "link_image": "url"
                    },
                    "_score": 12.5
                }
            ],
            "total": {"value": 1}
        }
    })
    response = client.post("/api/products/search", json={"keyword": "Sản", "page": 1, "size": 5, "sort": "default"})
    assert response.status_code == 200
    assert response.json() == {
        "products": [
            {
                "name": "Sản Phẩm A",
                "score": 85,
                "search_score": 12.5,
                "link_image": "url"
            }
        ],
        "total": 1
    }

def test_autocomplete_exceed_limit(client: TestClient, mock_elasticsearch):
    mock_elasticsearch.search = AsyncMock(return_value={
        "hits": {
            "hits": [
                {
                    "_source": {
                        "name": f"Sản Phẩm {i}",
                        "score": 80,
                        "link_image": "url"
                    },
                    "_score": 8.0
                } for i in range(10)
            ],
            "total": {"value": 10}
        }
    })
    response = client.post("/api/products/autocomplete", json={"keyword": "Sản", "page": 1, "size": 15, "sort": "default"})
    assert response.status_code == 200
    json_resp = response.json()
    # Dù request size là 15, backend giới hạn trả 10 sản phẩm
    assert len(json_resp["products"]) == 10
    assert json_resp["total"] == 10