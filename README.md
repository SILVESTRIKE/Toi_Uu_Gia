# Dự án Tối ưu hóa Giá Quán Cà Phê

Dự án này bao gồm một ứng dụng Streamlit để tối ưu hóa giá bán sản phẩm (burger, coke, lemonade, coffee) và một notebook để phân tích dữ liệu bán hàng. Ứng dụng cung cấp các chức năng như tìm giá tối ưu, phân tích tác động giá, tối ưu hóa khuyến mãi, và đề xuất điều chỉnh giá.

## Cấu trúc thư mục
- `app/`: Chứa code ứng dụng Streamlit (`app.py`).
- `scripts/`: Chứa các hàm xử lý (`__init__.py`).
- `models/`: Chứa các mô hình hồi quy đã train (file `.pkl`).
- `data/`: Chứa dữ liệu đầu vào (file `.csv`).
- `notebooks/`: Chứa notebook phân tích gốc.
- `requirements.txt`: Liệt kê các thư viện cần cài đặt.

## Yêu cầu hệ thống
- Python 3.8 hoặc cao hơn.
- pip (để cài đặt thư viện).
- Máy tính có ít nhất 8GB RAM (khuyến nghị).

## Cài đặt
1. **Cài đặt Python**:
   - Tải và cài đặt Python từ [python.org](https://www.python.org/downloads/).
   - Kiểm tra phiên bản:
     ```bash
     python --version
     ```

2. **Tạo môi trường ảo** (khuyến nghị):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Cài đặt thư viện**:
   ```bash
   pip install -r requirements.txt
   ```

## Chạy ứng dụng Streamlit
1. Di chuyển vào thư mục `app/`:
   ```bash
   cd app
   ```
2. Chạy ứng dụng:
   ```bash
   streamlit run app.py
   ```
3. Mở trình duyệt và truy cập `http://localhost:8501`.

## Chạy notebook
1. Cài đặt Jupyter (đã bao gồm trong `requirements.txt`).
2. Chạy Jupyter Notebook:
   ```bash
   jupyter notebook
   ```
3. Mở file trong thư mục `notebooks/` (ví dụ: `your_notebook.ipynb`) và chạy các cell.

## Chức năng chính
- **Giá tối ưu**: Hiển thị giá tối ưu và lợi nhuận tối đa cho từng sản phẩm.
- **Phân tích giá**: Thử các mức giá và xem doanh thu/số lượng dự đoán.
- **Khuyến mãi**: Phân tích tác động của giảm giá đến số lượng bán và lợi nhuận.
- **Đề xuất điều chỉnh giá**: Liệt kê sản phẩm cần tăng/giảm giá.
- **Phân tích bổ sung**: Biểu đồ về mối quan hệ giá-nhu cầu, tác động giảm giá, và yếu tố ngoại lai.

## Lưu ý
- Đảm bảo các file `.pkl` và `.csv` nằm đúng trong thư mục `models/` và `data/`.
- Nếu gặp lỗi về đường dẫn, kiểm tra và sửa trong `app.py` hoặc `scripts/__init__.py`.
- Liên hệ [your_email@example.com] nếu cần hỗ trợ.

## Tác giả
- [Your Name]