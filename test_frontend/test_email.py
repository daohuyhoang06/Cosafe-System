import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def send_email_test(json_file_path, html_file_path):
    # Đọc danh sách email từ file JSON
    with open(json_file_path, 'r', encoding='utf-8') as file:
        emails = json.load(file)

    # Khởi tạo trình duyệt Chrome
    driver = webdriver.Chrome()

    # Danh sách lưu kết quả
    results = []

    try:
        # Mở trang HTML
        driver.get(f"file:///{html_file_path}")

        # Duyệt qua từng email trong danh sách
        for email in emails:
            # Chọn quốc gia (giả sử là "Vietnam")
            country_select = Select(driver.find_element(By.ID, "country"))
            country_select.select_by_value("VN")

            # Nhập mã ZIP (giả sử là 12345)
            zip_input = driver.find_element(By.ID, "zip")
            zip_input.clear()
            zip_input.send_keys("12345")

            # Nhập email
            email_input = driver.find_element(By.ID, "email")
            email_input.clear()
            email_input.send_keys(email)

            # Delay 1 giây để đảm bảo dữ liệu được nhập
            time.sleep(1)

            # Nhấn nút gửi
            submit_button = driver.find_element(By.CLASS_NAME, "submit-btn")
            submit_button.click()

            # Đợi tối đa 10 giây để kiểm tra thông báo
            try:
                # Đợi phần tử notification xuất hiện
                notification = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "notification"))
                )
                notification_text = notification.text.strip()

                # Kiểm tra nội dung thông báo dựa trên mã JavaScript
                if "Thanks" in notification_text or "Check your email" in notification_text:
                    # Trường hợp gửi email thành công
                    results.append({"email": email, "status": "Pass", "message": notification_text})
                    print(f"Email: {email} - Pass ({notification_text})")
                elif "Please enter a valid email" in notification_text:
                    # Trường hợp email không hợp lệ
                    results.append({"email": email, "status": "Fail", "message": notification_text})
                    print(f"Email: {email} - Fail ({notification_text})")
                elif "problem sending" in notification_text:
                    # Trường hợp lỗi server hoặc gửi email thất bại
                    results.append({"email": email, "status": "Fail", "message": notification_text})
                    print(f"Email: {email} - Fail ({notification_text})")
                else:
                    # Trường hợp thông báo không rõ ràng
                    results.append({"email": email, "status": "Fail", "message": "Thông báo không rõ ràng"})
                    print(f"Email: {email} - Fail (Thông báo không rõ ràng: {notification_text})")


            except:
                # Không có thông báo xuất hiện sau 10 giây
                results.append({"email": email, "status": "Fail", "message": "Không có phản hồi từ trang"})
                print(f"Email: {email} - Fail (Không có phản hồi từ trang)")

            # Đợi 1 giây để đảm bảo trang ổn định trước khi thử email tiếp theo
            time.sleep(5)

    finally:
        # Đóng trình duyệt
        driver.quit()

        # In báo cáo tổng hợp
        print("\n--- Báo cáo tổng hợp ---")
        for result in results:
            print(f"Email: {result['email']}, Trạng thái: {result['status']}, Thông báo: {result['message']}")

# Đường dẫn đến file JSON và HTML
json_file_path = "C:/BaiTap/SoftwareEngineering/project/Cosafe-System/email_test/mail_demo.json"
html_file_path = "C:/BaiTap/SoftwareEngineering/project/Cosafe-System/front_end/home-page.html"

# Gọi hàm kiểm thử
send_email_test(json_file_path, html_file_path)