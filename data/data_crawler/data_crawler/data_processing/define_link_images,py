import json

def remove_2x_from_image_links(input_file_path, output_file_path):
    """
    Mở file JSON, xóa chuỗi ' 2x' ở cuối các link_image, và lưu kết quả vào file mới.
    
    Args:
        input_file_path (str): Đường dẫn đến file JSON gốc
        output_file_path (str): Đường dẫn để lưu file JSON đã chỉnh sửa
    """
    try:
        # Đọc file JSON
        print(f"Đang đọc file từ {input_file_path}...")
        with open(input_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Đếm số sản phẩm ban đầu
        total_products = len(data)
        modified_count = 0
        
        # Duyệt qua từng sản phẩm và chỉnh sửa link_image
        for product in data:
            link_image = product.get('link_image', '')
            if link_image and link_image.endswith(' 2x'):
                product['link_image'] = link_image[:-3]  # Xóa 3 ký tự cuối ' 2x'
                modified_count += 1
        
        # Ghi dữ liệu đã chỉnh sửa vào file mới
        print(f"Đang lưu dữ liệu đã chỉnh sửa vào {output_file_path}...")
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"Hoàn tất! Đã xử lý {total_products} sản phẩm, chỉnh sửa {modified_count} link_image.")
        
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{input_file_path}'")
    except json.JSONDecodeError:
        print(f"Lỗi: File '{input_file_path}' không phải là JSON hợp lệ")
    except Exception as e:
        print(f"Lỗi không xác định: {str(e)}")

# Sử dụng hàm
if __name__ == "__main__":
    remove_2x_from_image_links('Face_and_Body_Face_product.json', 'Face_and_Body_Face_product_fixed.json')
