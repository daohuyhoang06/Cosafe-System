import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

@pytest.mark.asyncio
async def test_image_process_success(client: TestClient, mock_gemini, sample_image):
    """Kiểm tra nhận diện ảnh thành công."""
    mock_model = MagicMock()
    mock_model.generate_content.return_value = MagicMock(
        text='[{"description": "Nước khoáng Lavie", "score": 0.95}]'
    )
    mock_gemini.return_value = mock_model
    response = client.post(
        "/api/image/image-process",
        files={"file": ("test.jpg", sample_image, "image/jpeg")}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_image_process_invalid_file(client: TestClient):
    """Kiểm tra lỗi khi file không phải ảnh."""
    response = client.post(
        "/api/image/image-process",
        files={"file": ("test.txt", b"not_an_image", "text/plain")}
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_image_process_gemini_error(client: TestClient, mock_gemini, sample_image):
    """Kiểm tra lỗi khi Gemini thất bại."""
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("Gemini API error")
    mock_gemini.return_value = mock_model
    response = client.post(
        "/api/image/image-process",
        files={"file": ("test.jpg", sample_image, "image/jpeg")}
    )
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_image_process_empty_file(client: TestClient):
    """Kiểm tra lỗi khi file ảnh rỗng."""
    response = client.post(
        "/api/image/image-process",
        files={"file": ("empty.jpg", b"", "image/jpeg")}
    )
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_image_process_large_file(client: TestClient):
    """Kiểm tra lỗi khi file ảnh quá lớn."""
    large_image = b"fake_image_data" * 1000000  # Giả lập file 10MB
    response = client.post(
        "/api/image/image-process",
        files={"file": ("large.jpg", large_image, "image/jpeg")}
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_image_process_invalid_json(client: TestClient, mock_gemini, sample_image):
    """Kiểm tra lỗi khi Gemini trả về JSON không hợp lệ."""
    mock_model = MagicMock()
    mock_model.generate_content.return_value = MagicMock(text="invalid_json")
    mock_gemini.return_value = mock_model
    response = client.post(
        "/api/image/image-process",
        files={"file": ("test.jpg", sample_image, "image/jpeg")}
    )
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_image_process_no_labels(client: TestClient, mock_gemini, sample_image):
    """Kiểm tra khi Gemini không tìm thấy nhãn."""
    mock_model = MagicMock()
    mock_model.generate_content.return_value = MagicMock(text="[]")
    mock_gemini.return_value = mock_model
    response = client.post(
        "/api/image/image-process",
        files={"file": ("test.jpg", sample_image, "image/jpeg")}
    )
    assert response.status_code == 200