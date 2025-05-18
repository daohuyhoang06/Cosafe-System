
import re

def extract_ingredients(content):
    # Tách thành phần theo dấu phẩy, "và", "hoặc"
    ingredients = re.split(r',|\s+và\s+|\s+hoặc\s+', content)
    # Làm sạch chuỗi và loại bỏ phần rỗng
    ingredients = [item.strip() for item in ingredients if item.strip()]
    return ingredients

if __name__ == "__main__":
    # Nhập chuỗi từ bàn phím
    test_input = input("Nhập danh sách thành phần:\n> ")
    
    result = extract_ingredients(test_input)
    
    print(" Các thành phần đã tách:")
    for i, ingredient in enumerate(result, 1):
        print(f"{i}. {ingredient}")
