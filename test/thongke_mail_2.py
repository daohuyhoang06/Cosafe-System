import pandas as pd
import matplotlib.pyplot as plt

# Danh sách email
emails = [
    "lehunglep@gmail.com", "babyh21007@gmail.com", "changngu2005@gmail.com", 
    "23020669@vnu.edu.vn", "tungtam262005@gmail.com", "babycute123cc@gmail.com", 
    "2302065@vnu.edu.vn", "ducdung005bn@gmail.com", "qp1ul@dcpa.net", 
    "23020666@vnu.edu.vn", "23020667@vnu.edu.vn", "kov7b@dcpa.net", 
    "fac2o@dcpa.net", "babycute", "lemanhhungdeptrai.cc", 
    "cutecute.tl", "cc.tuan", ""
]

# Kết quả của 10 lần chạy test (từ Mẫu 1 đến Mẫu 10)
results = [
    ["Pass", "Fail", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Fail"],
    ["Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Fail", "Pass", "Fail", "Pass", "Fail", "Pass", "Pass", "Pass", "Pass", "Pass", "Fail"],
    ["Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Fail", "Pass", "Pass", "Pass", "Pass", "Fail", "Fail", "Pass", "Pass", "Fail"],
    ["Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Fail", "Pass", "Pass", "Pass", "Pass", "Pass", "Fail", "Pass", "Pass", "Pass", "Fail"],
    ["Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Fail", "Pass", "Fail", "Pass", "Pass", "Pass", "Fail"],
    ["Pass", "Pass", "Pass", "Pass", "Fail", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Fail", "Pass", "Pass", "Pass", "Fail"],
    ["Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Fail", "Pass", "Pass", "Fail", "Pass", "Pass", "Pass", "Fail"],
    ["Pass", "Pass", "Pass", "Fail", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Fail", "Pass", "Pass", "Pass", "Fail"],
    ["Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Fail", "Fail", "Pass", "Pass", "Pass", "Fail"],
    ["Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Pass", "Fail", "Pass", "Pass", "Pass", "Fail", "Pass", "Pass", "Pass", "Fail"]
]

# Tạo DataFrame từ kết quả
df = pd.DataFrame(results, columns=emails)

# Tính số lần Pass và Fail cho mỗi email
pass_counts = df.apply(lambda x: (x == "Pass").sum())
fail_counts = df.apply(lambda x: (x == "Fail").sum())

# Tạo DataFrame tổng hợp
summary_df = pd.DataFrame({
    'Pass': pass_counts,
    'Fail': fail_counts
}, index=emails)

# Vẽ biểu đồ cột
summary_df.plot.bar(
    figsize=(14, 6),  # Kích thước biểu đồ
    color=['green', 'red'],  # Màu xanh cho Pass, đỏ cho Fail
    rot=90  # Xoay nhãn trục x để dễ đọc
)

# Thêm tiêu đề và nhãn
plt.title('Thống kê Pass và Fail cho từng email qua 10 lần chạy test')
plt.xlabel('Email')
plt.ylabel('Số lần')

# Thêm lưới để dễ theo dõi
plt.grid(True)

# Lưu biểu đồ vào file
plt.show()