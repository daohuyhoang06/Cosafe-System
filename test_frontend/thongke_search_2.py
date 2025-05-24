import pandas as pd
import matplotlib.pyplot as plt

# Dữ liệu từ 10 lần chạy test
data = {
    'Test case': ['image_1.jpg', 'image_2.jpg', 'image_3.jpg', 'image_4.png', 'image_5.jpg', 'image_6.png', 
                  'image_7.jpg', 'image_8.jpg', 'image_9.jpg', 'image_10.jpg', 'image_11.txt', 'image_12.txt'],
    'Lần 1': ['Fail', 'Pass', 'Pass', 'Fail', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Fail', 'Fail', 'Fail'],
    'Lần 2': ['Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Fail', 'Pass', 'Fail', 'Fail'],
    'Lần 3': ['Fail', 'Fail', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Fail', 'Fail'],
    'Lần 4': ['Fail', 'Fail', 'Pass', 'Fail', 'Pass', 'Pass', 'Pass', 'Fail', 'Fail', 'Pass', 'Fail', 'Fail'],
    'Lần 5': ['Fail', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Fail', 'Fail', 'Fail'],
    'Lần 6': ['Fail', 'Pass', 'Pass', 'Fail', 'Fail', 'Fail', 'Pass', 'Pass', 'Pass', 'Pass', 'Fail', 'Fail'],
    'Lần 7': ['Pass', 'Fail', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Fail', 'Fail'],
    'Lần 8': ['Pass', 'Pass', 'Pass', 'Pass', 'Fail', 'Fail', 'Pass', 'Pass', 'Pass', 'Pass', 'Fail', 'Fail'],
    'Lần 9': ['Fail', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Fail', 'Pass', 'Pass', 'Pass', 'Fail', 'Fail'],
    'Lần 10': ['Fail', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Fail', 'Fail', 'Fail']
}

# Tạo DataFrame từ dữ liệu
df = pd.DataFrame(data)
df.set_index('Test case', inplace=True)

# Tính số lần Pass và Fail cho mỗi test case
pass_counts = df.apply(lambda x: (x == 'Pass').sum(), axis=1)
fail_counts = df.apply(lambda x: (x == 'Fail').sum(), axis=1)

# Tạo DataFrame tổng hợp để vẽ biểu đồ
summary_df = pd.DataFrame({
    'Pass': pass_counts,
    'Fail': fail_counts
})

# Vẽ biểu đồ cột
summary_df.plot.bar(
    figsize=(12, 6),  # Kích thước biểu đồ
    color=['green', 'red'],  # Màu cho Pass (xanh) và Fail (đỏ)
    rot=45  # Xoay nhãn trục x để dễ đọc
)

# Thêm tiêu đề và nhãn
plt.title('Thống kê Pass và Fail cho từng test case qua 10 lần chạy')
plt.xlabel('Test case')
plt.ylabel('Số lần')

# Thêm lưới để dễ theo dõi
plt.grid(True)

# Lưu biểu đồ vào file
plt.show()