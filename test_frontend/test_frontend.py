import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CosafeSystemTest(unittest.TestCase):
    def setUp(self):
        print("Bắt đầu test case")
        self.driver = webdriver.Chrome()
        self.frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'front_end'))
        if not os.path.exists(self.frontend_path):
            raise FileNotFoundError(f"Thư mục front_end không tồn tại tại: {self.frontend_path}")
        self.results = []  # Danh sách lưu kết quả Pass/Fail của các test case

    def tearDown(self):
        time.sleep(5)  # Đợi 5 giây để quan sát trước khi đóng trình duyệt
        self.driver.quit()
        print("Kết thúc test case\n")

    def test_search_by_text(self):
        print("TC001: Kiểm tra tìm kiếm sản phẩm bằng văn bản")
        homepage_path = f"file://{self.frontend_path}/home-page.html"
        try:
            self.driver.get(homepage_path)
            time.sleep(2)  # Đợi trang tải
            search_input = self.driver.find_element(By.ID, "textSearchBar")
            search_input.send_keys("cream")
            time.sleep(1)  # Đợi sau khi nhập
            search_input.send_keys(Keys.RETURN)
            time.sleep(2)  # Đợi kết quả
            self.assertIn("searching-result.html", self.driver.current_url)
            print("TC001: Pass")
            self.results.append({"test_case": "TC001", "status": "Pass", "message": "Tìm kiếm thành công"})
        except Exception as e:
            print(f"TC001: Fail - Lỗi: {str(e)}")
            self.results.append({"test_case": "TC001", "status": "Fail", "message": f"Lỗi: {str(e)}"})

    def test_search_by_image(self):
        print("TC002: Kiểm tra tìm kiếm sản phẩm bằng hình ảnh")
        homepage_path = f"file://{self.frontend_path}/home-page.html"
        try:
            self.driver.get(homepage_path)
            time.sleep(2)
            open_modal_btn = self.driver.find_element(By.ID, "openImageModal")
            open_modal_btn.click()
            time.sleep(2)
            modal = self.driver.find_element(By.ID, "imageSearchModal")
            self.assertTrue(modal.is_displayed(), "Modal không hiển thị")
            image_input = self.driver.find_element(By.ID, "imageInput")
            image_path = "C:/BaiTap/SoftwareEngineering/project/image_test/image_1.jpg"
            image_input.send_keys(image_path)
            time.sleep(2)
            submit_btn = self.driver.find_element(By.ID, "submitImageSearch")
            submit_btn.click()
            time.sleep(5)
            self.assertIn("searching-result.html", self.driver.current_url)
            print("TC002: Pass")
            self.results.append({"test_case": "TC002", "status": "Pass", "message": "Tìm kiếm bằng hình ảnh thành công"})
        except Exception as e:
            print(f"TC002: Fail - Lỗi: {str(e)}")
            self.results.append({"test_case": "TC002", "status": "Fail", "message": f"Lỗi: {str(e)}"})

    def test_view_product_detail(self):
        print("TC003: Kiểm tra xem chi tiết sản phẩm")
        homepage_path = f"file://{self.frontend_path}/home-page.html"
        try:
            self.driver.get(homepage_path)
            time.sleep(2)
            product_card = self.driver.find_element(By.CLASS_NAME, "product-card")
            product_card.click()
            time.sleep(2)
            self.assertIn("product-detail.html", self.driver.current_url)
            print("TC003: Pass")
            self.results.append({"test_case": "TC003", "status": "Pass", "message": "Xem chi tiết sản phẩm thành công"})
        except Exception as e:
            print(f"TC003: Fail - Lỗi: {str(e)}")
            self.results.append({"test_case": "TC003", "status": "Fail", "message": f"Lỗi: {str(e)}"})

    def test_submit_valid_email(self):
        print("TC004: Kiểm tra gửi email hợp lệ")
        homepage_path = f"file://{self.frontend_path}/home-page.html"
        try:
            self.driver.get(homepage_path)
            time.sleep(2)
            country_select = Select(self.driver.find_element(By.ID, "country"))
            country_select.select_by_value("VN")
            zip_input = self.driver.find_element(By.ID, "zip")
            zip_input.clear()
            zip_input.send_keys("12345")
            email_input = self.driver.find_element(By.ID, "email")
            email_input.clear()
            email_input.send_keys("test@example.com")
            time.sleep(1)
            submit_button = self.driver.find_element(By.CLASS_NAME, "submit-btn")
            submit_button.click()
            notification = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "notification"))
            )
            notification_text = notification.text.strip()
            self.assertTrue("Thanks" in notification_text or "Check your email" in notification_text)
            print("TC004: Pass")
            self.results.append({"test_case": "TC004", "status": "Pass", "message": "Email hợp lệ gửi thành công"})
        except Exception as e:
            print(f"TC004: Fail - Lỗi: {str(e)}")
            self.results.append({"test_case": "TC004", "status": "Fail", "message": f"Lỗi: {str(e)}"})

    def test_submit_invalid_email(self):
        print("TC005: Kiểm tra gửi email không hợp lệ")
        homepage_path = f"file://{self.frontend_path}/home-page.html"
        try:
            self.driver.get(homepage_path)
            time.sleep(2)
            country_select = Select(self.driver.find_element(By.ID, "country"))
            country_select.select_by_value("VN")
            zip_input = self.driver.find_element(By.ID, "zip")
            zip_input.clear()
            zip_input.send_keys("12345")
            email_input = self.driver.find_element(By.ID, "email")
            email_input.clear()
            email_input.send_keys("invalid.email")
            time.sleep(1)
            submit_button = self.driver.find_element(By.CLASS_NAME, "submit-btn")
            submit_button.click()
            notification = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "notification"))
            )
            notification_text = notification.text.strip()
            self.assertIn("Please enter a valid email", notification_text)
            print("TC005: Pass")
            self.results.append({"test_case": "TC005", "status": "Pass", "message": "Email không hợp lệ được xử lý đúng"})
        except Exception as e:
            print(f"TC005: Fail - Lỗi: {str(e)}")
            self.results.append({"test_case": "TC005", "status": "Fail", "message": f"Lỗi: {str(e)}"})

    def test_search_with_invalid_format(self):
        print("TC006: Kiểm tra tìm kiếm với định dạng sai (@###)")
        homepage_path = f"file://{self.frontend_path}/home-page.html"
        try:
            self.driver.get(homepage_path)
            time.sleep(2)
            search_input = self.driver.find_element(By.ID, "textSearchBar")
            search_input.send_keys("@###")
            time.sleep(1)
            search_input.send_keys(Keys.RETURN)
            time.sleep(2)
            if "searching-result.html" in self.driver.current_url:
                no_results = self.driver.find_element(By.CLASS_NAME, "no-results")
                self.assertTrue(no_results.is_displayed())
                print("TC006: Pass")
                self.results.append({"test_case": "TC006", "status": "Pass", "message": "Tìm kiếm với định dạng sai, hiển thị thông báo không có kết quả"})
            else:
                error_message = self.driver.find_element(By.CLASS_NAME, "notification")
                self.assertIn("invalid search term", error_message.text.lower())
                print("TC006: Pass")
                self.results.append({"test_case": "TC006", "status": "Pass", "message": "Tìm kiếm với định dạng sai, hiển thị thông báo lỗi"})
        except Exception as e:
            print(f"TC006: Fail - Lỗi: {str(e)}")
            self.results.append({"test_case": "TC006", "status": "Fail", "message": f"Lỗi: {str(e)}"})

    def tearDown(self):
        time.sleep(5)  # Đợi 5 giây để quan sát trước khi đóng trình duyệt
        self.driver.quit()
        print("Kết thúc test case\n")

        # In báo cáo tổng hợp sau khi tất cả test case hoàn tất
        if len(self.results) == 6:  # Chỉ in báo cáo khi tất cả test case đã chạy xong
            print("--- Báo cáo tổng hợp ---")
            total_pass = sum(1 for r in self.results if r["status"] == "Pass")
            total_fail = sum(1 for r in self.results if r["status"] == "Fail")
            print(f"Tổng số test case: {len(self.results)}")
            print(f"Pass: {total_pass}")
            print(f"Fail: {total_fail}")
            for result in self.results:
                print(f"Test case: {result['test_case']}, Trạng thái: {result['status']}, Thông báo: {result['message']}")

if __name__ == "__main__":
    unittest.main()