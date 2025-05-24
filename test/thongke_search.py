# Import các thư viện cần thiết
import pandas as pd
import matplotlib.pyplot as plt

# Tạo dữ liệu cho DataFrame
data = {
    'Lần chạy test': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'Pass': [7, 9, 8, 5, 8, 6, 9, 8, 8, 8],
    'Fail': [5, 3, 4, 7, 4, 6, 3, 4, 4, 4]
}

# Tạo DataFrame từ dữ liệu
df = pd.DataFrame(data)

# Vẽ biểu đồ cột
ax = df.set_index('Lần chạy test').plot.bar(
    rot=45,            # Xoay nhãn trục x 45 độ để dễ đọc
    figsize=(10, 6),   # Kích thước biểu đồ (rộng 10, cao 6)
    color=['green', 'red']  # Màu xanh cho Pass, đỏ cho Fail
)

# Thêm tiêu đề và nhãn cho biểu đồ
plt.title('Thống kê Pass và Fail cho từng lần chạy test')
plt.xlabel('Lần chạy test')
plt.ylabel('Số lượng test case')

# Thêm lưới để dễ theo dõi giá trị
plt.grid(True)

# Hiển thị biểu đồ
plt.show()