import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os

def integrated_test():
    # Khởi tạo trình duyệt Chrome
    driver = webdriver.Chrome()
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'front_end'))
    
    try:
        # Bước 1: Mở trang chủ
        homepage_path = f"file://{frontend_path}/home-page.html"
        driver.get(homepage_path)
        print("Đã mở trang chủ")
        time.sleep(2)  # Chờ 2 giây để quan sát
        
        # Bước 2: Tìm kiếm sản phẩm
        search_input = driver.find_element(By.ID, "textSearchBar")
        search_input.send_keys("cream")
        search_input.send_keys(Keys.RETURN)
        print("Đã tìm kiếm sản phẩm 'cream'")
        time.sleep(2)  # Chờ 2 giây để quan sát
        
        # Bước 3: Nhấn nút tô màu lần 1 trên trang kết quả tìm kiếm
        color_btn_result = driver.find_element(By.ID, "activateBtn")  # Giả định ID là activateBtn
        color_btn_result.click()
        print("Đã nhấn nút tô màu lần 1 trên trang kết quả")
        time.sleep(2)  # Chờ 2 giây để quan sát
        
        # Bước 4: Nhấn nút tô màu lần 2 trên trang kết quả tìm kiếm trước khi chọn sản phẩm
        color_btn_result.click()
        print("Đã nhấn nút tô màu lần 2 trên trang kết quả")
        time.sleep(2)  # Chờ 2 giây để quan sát
        
        # Bước 5: Chọn sản phẩm đầu tiên từ kết quả
        product_card = driver.find_element(By.CLASS_NAME, "product-card")
        product_card.click()
        print("Đã chọn sản phẩm đầu tiên")
        time.sleep(2)  # Chờ 2 giây để quan sát
        
        # Bước 6: Kiểm tra trang chi tiết sản phẩm
        product_name = driver.find_element(By.ID, "productName")
        assert product_name.is_displayed(), "Tên sản phẩm không hiển thị"
        print("Đã kiểm tra tên sản phẩm hiển thị")
        time.sleep(2)  # Chờ 2 giây để quan sát
        
        # Bước 7: Nhấn nút tô màu lần 3 trên trang chi tiết sản phẩm
        color_btn_detail = driver.find_element(By.ID, "activateBtn")  # Giả định ID là activateBtn
        color_btn_detail.click()
        print("Đã nhấn nút tô màu lần 3 trên trang chi tiết")
        time.sleep(2)  # Chờ 2 giây để quan sát
        
        # Bước 8: Cuộn trang xuống một chút để quan sát thành phần
        driver.execute_script("window.scrollTo(0, 500);")  # Cuộn xuống 500px
        print("Đã cuộn trang xuống một chút để quan sát thành phần")
        time.sleep(2)  # Chờ 2 giây để quan sát
        
        print("Kiểm thử thành công!")
        
    except Exception as e:
        print(f"Lỗi trong quá trình kiểm thử: {str(e)}")
    finally:
        time.sleep(2)  # Chờ 2 giây trước khi đóng
        driver.quit()

if __name__ == "__main__":
    integrated_test()


