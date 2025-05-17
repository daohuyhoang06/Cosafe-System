import pytest
import httpx
from pydantic import BaseModel

# Định nghĩa SafetyRequest (tương tự server.py)
class SafetyRequest(BaseModel):
    name: str

# URL của server
BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_safety_endpoint_symbiome():
    # Tạo đối tượng SafetyRequest với "Symbiome"
    request_data = SafetyRequest(name="Symbiome")
    
    # Gửi yêu cầu POST đến endpoint /safety
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/safety",
            json=request_data.dict()
        )
    
    # Kiểm tra trạng thái phản hồi
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    # Lấy dữ liệu phản hồi
    data = response.json()
    
    # Kiểm tra trường hợp không tìm thấy sản phẩm
    if "message" in data and data["message"] == "Không tìm thấy sản phẩm":
        assert False, "No products found for 'Symbiome'. Ensure Elasticsearch has relevant data."
    
    # Kiểm tra định dạng phản hồi
    assert "products" in data, "Response should contain 'products' key"
    assert isinstance(data["products"], list), "'products' should be a list"
    
    # Kiểm tra ít nhất một sản phẩm có tên chứa "Symbiome"
    symbiome_products = [p for p in data["products"] if "Symbiome" in p["name"]]
    assert len(symbiome_products) > 0, "At least one product should match 'Symbiome'"
    
    # Kiểm tra cấu trúc của mỗi sản phẩm
    for product in symbiome_products:
        assert "name" in product, "Product should have 'name'"
        assert "score" in product, "Product should have 'score'"
        assert "image" in product, "Product should have 'image'"
        assert isinstance(product["score"], (int, float)), "'score' should be a number"

    print(data)