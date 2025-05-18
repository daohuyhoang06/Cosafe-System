# Chuyển đổi file JSON thành file NDJSON


import json

# Mở file JSON gốc (giả sử đang ở dạng list [])
with open("D:\Face_and_Body_Face_product_bulk.ndjson", "r", encoding="utf-8") as f:
     products = [json.loads(line) for line in f if line.strip()]

# Tạo file NDJSON đúng định dạng
with open("D:\\bulk_fixed2.json", "w", encoding="utf-8") as f:
    for product in products:
        f.write(json.dumps({ "index": { "_index": "cs_products_data" } }) + "\n")
        f.write(json.dumps(product) + "\n")
