import json
from collections import defaultdict

# Đọc file JSON gốc
with open('output.json', 'r') as f:
    original_data = json.load(f)

# Bước 1: Nhóm dữ liệu theo (tag, section)
grouped = defaultdict(lambda: {
    "tag": None,
    "section": None,
    "link": None,
    "product_links": []
})

for item in original_data:
    key = (item["tag"], item["section"])
    
    # Gán giá trị cố định cho các trường tag/section/link
    if not grouped[key]["tag"]:
        grouped[key]["tag"] = item["tag"]
        grouped[key]["section"] = item["section"]
        grouped[key]["link"] = item["link"]  # Lấy link từ phần tử đầu tiên
    
    # Gộp product_links
    grouped[key]["product_links"].extend(item["product_links"])

# Bước 2: Ghi thành các file riêng
for key, data in grouped.items():
    # Tạo tên file (thay thế ký tự đặc biệt)
    filename = f"{data['tag'].replace(' ', '_').replace('&', 'and')}_{data['section'].replace(' ', '_')}.json"
    
    # Ghi file JSON
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

print("Đã xử lý xong!") 
