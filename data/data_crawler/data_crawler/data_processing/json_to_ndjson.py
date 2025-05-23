import json


# Đọc file JSON đã chỉnh sửa
with open('Face_and_Body_Face_product_fixed.json', 'r', encoding='utf-8') as f:
    products = json.load(f)


# Chuyển đổi dữ liệu thành định dạng NDJSON
# Mỗi dòng là một JSON object
with open('Face_and_Body_Face_product_fixed_bulk_01.ndjson', 'w', encoding='utf-8') as f:
    for product in products:
        f.write(json.dumps({ "index": { "_index": "products" } }) + '\n')
        f.write(json.dumps(product, ensure_ascii=False) + '\n')
        #cs_products_data
