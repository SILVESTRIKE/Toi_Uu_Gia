Dự án Tối ưu hóa Giá Quán Cà Phê

Dự án này bao gồm một ứng dụng Streamlit để tối ưu hóa giá bán sản phẩm (burger, coke, lemonade, coffee) và một notebook để phân tích dữ liệu bán hàng. Ứng dụng cung cấp các chức năng như tìm giá tối ưu, phân tích tác động giá, tối ưu hóa khuyến mãi, và đề xuất điều chỉnh giá.

Cấu trúc thư mục





app/: Chứa code ứng dụng Streamlit (app.py).



scripts/: Chứa các hàm xử lý (__init__.py).



models/: Chứa các mô hình hồi quy đã train (file .pkl).



data/: Chứa dữ liệu đầu vào (file .csv).



notebooks/: Chứa notebook phân tích gốc.



requirements.txt: Liệt kê các thư viện cần cài đặt.

Yêu cầu hệ thống





Python 3.8 hoặc cao hơn.



pip (để cài đặt thư viện).



Máy tính có ít nhất 8GB RAM (khuyến nghị).

Cài đặt





Cài đặt Python:





Tải và cài đặt Python từ python.org.



Kiểm tra phiên bản:

python --version



Giải nén folder dự án:





Tải và giải nén file project.zip hoặc project.tar.gz.



Đảm bảo thư mục có đầy đủ các file và thư mục như mô tả ở trên.



Tạo môi trường ảo:





Di chuyển vào thư mục dự án:

cd project



Tạo môi trường ảo:

python -m venv venv



Kích hoạt môi trường ảo:

source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows



Cài đặt thư viện:





Trong môi trường ảo, chạy:

pip install -r requirements.txt

Chạy ứng dụng Streamlit





Di chuyển vào thư mục app/:

cd app



Chạy ứng dụng:

streamlit run app.py



Mở trình duyệt và truy cập http://localhost:8501.

Chạy notebook





Trong môi trường ảo, chạy Jupyter Notebook:

jupyter notebook



Mở file trong thư mục notebooks/ (ví dụ: your_notebook.ipynb) và chạy các cell.

Chức năng chính





Giá tối ưu: Hiển thị giá tối ưu và lợi nhuận tối đa cho từng sản phẩm.



Phân tích giá: Thử các mức giá và xem doanh thu/số lượng dự đoán.



Khuyến mãi: Phân tích tác động của giảm giá đến số lượng bán và lợi nhuận.



Đề xuất điều chỉnh giá: Liệt kê sản phẩm cần tăng/giảm giá.



Phân tích bổ sung: Biểu đồ về mối quan hệ giá-nhu cầu, tác động giảm giá, và yếu tố ngoại lai.

Xử lý lỗi thường gặp





Thiếu file .pkl hoặc .csv: Kiểm tra thư mục models/ và data/. Nếu thiếu, chạy lại notebook trong notebooks/ để tạo file .pkl.



Lỗi đường dẫn: Đảm bảo cấu trúc thư mục đúng như mô tả. Sửa đường dẫn trong app.py hoặc scripts/__init__.py nếu cần.



Lỗi thư viện: Chạy lại pip install -r requirements.txt. Nếu lỗi vẫn xảy ra, kiểm tra phiên bản Python (python --version) và liên hệ người gửi.



Lỗi Python không tìm thấy: Đảm bảo Python được cài đặt và thêm vào PATH. Hoặc dùng lệnh python3 thay vì python.

Liên hệ





Nếu cần hỗ trợ, liên hệ [your_email@example.com].

Tác giả





[Your Name]# Toi_Uu_Gia
