import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import os

def get_image_files():
    image_dir = r"C:\BaiTap\SoftwareEngineering\project\Cosafe-System\image_test"
    image_files = []
    for i in range(1, 13):  # Chỉ lấy từ image1 đến image10
        jpg_path = os.path.join(image_dir, f"image_{i}.jpg")
        png_path = os.path.join(image_dir, f"image_{i}.png")
        txt_path = os.path.join(image_dir, f"image_{i}.txt")
        if os.path.exists(jpg_path):
            image_files.append(jpg_path)
        elif os.path.exists(png_path):
            image_files.append(png_path)
        elif os.path.exists(txt_path):
            image_files.append(txt_path)
        else:
            print(f"File image{i} không tồn tại với đuôi .jpg hoặc .png")
    return image_files

def test_image_search(image_path):
    driver = webdriver.Chrome()
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'front_end'))
    
    try:
        # Mở trang chủ
        homepage_path = f"file://{frontend_path}/home-page.html"
        driver.get(homepage_path)
        print(f"Đã mở trang chủ cho test case {os.path.basename(image_path)}")
        time.sleep(2)
        
        # Nhấp vào nút mở modal
        open_modal_btn = driver.find_element(By.ID, "openImageModal")
        open_modal_btn.click()
        print("Đã nhấp vào nút mở modal")
        time.sleep(2)
        
        # Kiểm tra modal hiển thị
        modal = driver.find_element(By.ID, "imageSearchModal")
        assert modal.is_displayed(), "Modal không hiển thị"
        print("Modal đã hiển thị")
        time.sleep(2)
        
        # Chọn file hình ảnh
        image_input = driver.find_element(By.ID, "imageInput")
        image_input.send_keys(image_path)
        print(f"Đã chọn file hình ảnh: {image_path}")
        time.sleep(2)
        
        # # Nhấp nút gửi
        # submit_btn = driver.find_element(By.ID, "submitImageSearch")
        # submit_btn.click()
        # print("Đã nhấp nút gửi")
        # time.sleep(5)  # Chờ trang tải
        
        # Kiểm tra URL sau khi gửi
        current_url = driver.current_url
        if "searching-result.html" in current_url:
            print(f"Test case {os.path.basename(image_path)}: Pass")
            return True
        else:
            print(f"Test case {os.path.basename(image_path)}: Fail - Không chuyển đến trang kết quả")
            return False
    except Exception as e:
        print(f"Lỗi trong test case {os.path.basename(image_path)}: {str(e)}")
        return False
    finally:
        time.sleep(10)
        driver.quit()

def run_all_tests():
    image_files = get_image_files()
    results = []
    for image_path in image_files:
        success = test_image_search(image_path)
        results.append((image_path, success))
    
    # Báo cáo tổng hợp
    print("\n--- Báo cáo tổng hợp ---")
    for image_path, success in results:
        status = "Pass" if success else "Fail"
        print(f"Test case {os.path.basename(image_path)}: {status}")
    print(f"Tổng số test case: {len(results)}")
    print(f"Số test case Pass: {sum(1 for _, s in results if s)}")
    print(f"Số test case Fail: {sum(1 for _, s in results if not s)}")

if __name__ == "__main__":
    run_all_tests()