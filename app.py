import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scripts import (
    load_model,
    find_optimal_price,
    predict_revenue,
    analyze_discount,
    recommend_price_adjustments,
    plot_price_quantity,
    plot_discount_impact,
    plot_elasticity_factors
)
from scripts.CSV import load_data
# Thiết lập cấu hình Streamlit
st.set_page_config(page_title="Tối ưu hóa Giá Quán Cà Phê", layout="wide")

# Tải dữ liệu và mô hình
@st.cache_data
def get_data_and_models():
    combined_data, bau2_data = load_data()
    models = {
        'burger_1070': load_model('models/burger_1070.pkl'),
        'burger_2051': load_model('models/burger_2051.pkl'),
        'burger_2052': load_model('models/burger_2052.pkl'),
        'burger_2053': load_model('models/burger_2053.pkl'),
        'coke_2051': load_model('models/coke_2051.pkl'),
        'coke_2053': load_model('models/coke_2053.pkl'),
        'lemonade_2052': load_model('models/lemonade_2052.pkl'),
        'coffee_2053': load_model('models/coffee_2053.pkl')
    }
    return combined_data, bau2_data, models

combined_data, bau2_data, models = get_data_and_models()

# Sidebar
st.sidebar.title("Điều hướng")
page = st.sidebar.radio("Chọn chức năng", [
    "Giá tối ưu",
    "Phân tích giá",
    "Khuyến mãi",
    "Đề xuất điều chỉnh giá",
    "Phân tích bổ sung"
])

# Trang 1: Giá tối ưu
if page == "Giá tối ưu":
    st.title("Giá Tối ưu cho Từng Sản phẩm")
    buying_price = st.number_input("Nhập giá mua (buying price)", min_value=0.0, value=9.0, step=0.1)
    
    optimal_prices = []
    for product, model in models.items():
        product_data = combined_data[(combined_data['ITEM_NAME'] == product.split('_')[0].upper()) & 
                                    (combined_data['SELL_ID'] == int(product.split('_')[1]))]
        result = find_optimal_price(product_data, model, buying_price)
        optimal_prices.append({
            'Sản phẩm': product,
            'Giá tối ưu': round(result['PRICE'].iloc[0], 2),
            'Số lượng dự đoán': round(result['QUANTITY'].iloc[0], 2),
            'Lợi nhuận tối đa': round(result['PROFIT'].iloc[0], 2)
        })
    
    st.table(pd.DataFrame(optimal_prices))


# Trang 2: Phân tích giá
elif page == "Phân tích giá":
    st.title("Phân tích Tác động của Giá đến Doanh thu")
    data_choice = st.radio("Chọn dữ liệu", ["Toàn bộ dữ liệu (combined_data)", "Dữ liệu ngày thường (bau2_data)"])
    data_to_use = combined_data if data_choice == "Toàn bộ dữ liệu (combined_data)" else bau2_data
    
    product = st.selectbox("Chọn sản phẩm", list(models.keys()))
    product_data = data_to_use[(data_to_use['ITEM_NAME'] == product.split('_')[0].upper()) & 
                              (data_to_use['SELL_ID'] == int(product.split('_')[1]))]
    
    # Bộ lọc bổ sung
    st.subheader("Bộ lọc dữ liệu")
    holidays = ['Tất cả'] + list(data_to_use['HOLIDAY'].unique())
    holiday_filter = st.selectbox("Lọc theo ngày lễ", holidays)
    weekend_filter = st.selectbox("Lọc theo cuối tuần", ['Tất cả', 'Có', 'Không'])
    schoolbreak_filter = st.selectbox("Lọc theo kỳ nghỉ học", ['Tất cả', 'Có', 'Không'])
    
    filtered_data = product_data.copy()
    if holiday_filter != 'Tất cả':
        filtered_data = filtered_data[filtered_data['HOLIDAY'] == holiday_filter]
    if weekend_filter != 'Tất cả':
        filtered_data = filtered_data[filtered_data['IS_WEEKEND'] == (1 if weekend_filter == 'Có' else 0)]
    if schoolbreak_filter != 'Tất cả':
        filtered_data = filtered_data[filtered_data['IS_SCHOOLBREAK'] == (1 if schoolbreak_filter == 'Có' else 0)]
    
    if filtered_data.empty:
        st.warning("Không có dữ liệu sau khi áp dụng bộ lọc. Vui lòng thay đổi bộ lọc.")
    else:
        test_price = st.slider("Chọn giá thử nghiệm", 
                              min_value=float(filtered_data['PRICE'].min()),
                              max_value=float(filtered_data['PRICE'].max()),
                              value=float(filtered_data['PRICE'].mean()))
        
        revenue, quantity = predict_revenue(filtered_data, models[product], test_price)
        
        st.write(f"**Giá thử nghiệm**: {test_price:.2f}")
        st.write(f"**Số lượng dự đoán**: {quantity:.2f}")
        st.write(f"**Doanh thu dự đoán**: {revenue:.2f}")
        
        # Vẽ biểu đồ
        fig = plot_price_quantity(filtered_data, models[product])
        st.plotly_chart(fig)


# Trang 3: Khuyến mãi
elif page == "Khuyến mãi":
    st.title("Tối ưu hóa Chương trình Khuyến mãi")
    product = st.selectbox("Chọn sản phẩm", list(models.keys()))
    discount_percent = st.slider("Mức giảm giá (%)", min_value=0, max_value=50, value=10)
    buying_price = st.number_input("Nhập giá mua", min_value=0.0, value=9.0, step=0.1)
    
    product_data = combined_data[(combined_data['ITEM_NAME'] == product.split('_')[0].upper()) & 
                                (combined_data['SELL_ID'] == int(product.split('_')[1]))]
    result = analyze_discount(product_data, models[product], discount_percent, buying_price)
    
    st.write(f"**Giá sau giảm {discount_percent}%**: {result['discounted_price']:.2f}")
    st.write(f"**Số lượng dự đoán**: {result['quantity']:.2f}")
    st.write(f"**Lợi nhuận dự đoán**: {result['profit']:.2f}")
    
    # Vẽ biểu đồ
    fig = plot_discount_impact(product_data, models[product], buying_price)
    st.plotly_chart(fig)

# Trang 4: Đề xuất điều chỉnh giá
elif page == "Đề xuất điều chỉnh giá":
    st.title("Đề xuất Điều chỉnh Giá")
    buying_price = st.number_input("Nhập giá mua", min_value=0.0, value=9.0, step=0.1)
    
    recommendations = recommend_price_adjustments(combined_data, models, buying_price)
    st.table(recommendations)

# Trang 5: Phân tích bổ sung
elif page == "Phân tích bổ sung":
    st.title("Phân tích Bổ sung")
    data_choice = st.radio("Chọn dữ liệu", ["Toàn bộ dữ liệu (combined_data)", "Dữ liệu ngày thường (bau2_data)"])
    data_to_use = combined_data if data_choice == "Toàn bộ dữ liệu (combined_data)" else bau2_data
    
    analysis_type = st.selectbox("Chọn loại phân tích", [
        "Mối quan hệ giá-nhu cầu",
        "Tác động của giảm giá",
        "Yếu tố ảnh hưởng đến độ co giãn giá"
    ])
    
    product = st.selectbox("Chọn sản phẩm", list(models.keys()))
    product_data = data_to_use[(data_to_use['ITEM_NAME'] == product.split('_')[0].upper()) & 
                              (data_to_use['SELL_ID'] == int(product.split('_')[1]))]
    
    # Bộ lọc bổ sung cho dữ liệu
    st.subheader("Bộ lọc dữ liệu")
    holidays = ['Tất cả'] + list(data_to_use['HOLIDAY'].unique())
    holiday_filter = st.selectbox("Lọc theo ngày lễ", holidays)
    weekend_filter = st.selectbox("Lọc theo cuối tuần", ['Tất cả', 'Có', 'Không'])
    schoolbreak_filter = st.selectbox("Lọc theo kỳ nghỉ học", ['Tất cả', 'Có', 'Không'])
    
    filtered_data = product_data.copy()
    if holiday_filter != 'Tất cả':
        filtered_data = filtered_data[filtered_data['HOLIDAY'] == holiday_filter]
    if weekend_filter != 'Tất cả':
        filtered_data = filtered_data[filtered_data['IS_WEEKEND'] == (1 if weekend_filter == 'Có' else 0)]
    if schoolbreak_filter != 'Tất cả':
        filtered_data = filtered_data[filtered_data['IS_SCHOOLBREAK'] == (1 if schoolbreak_filter == 'Có' else 0)]
    
    if filtered_data.empty:
        st.warning("Không có dữ liệu sau khi áp dụng bộ lọc. Vui lòng thay đổi bộ lọc.")
    else:
        if analysis_type == "Mối quan hệ giá-nhu cầu":
            fig = plot_price_quantity(filtered_data, models[product])
            st.plotly_chart(fig)
        elif analysis_type == "Tác động của giảm giá":
            buying_price = st.number_input("Nhập giá mua", min_value=0.0, value=9.0, step=0.1)
            fig = plot_discount_impact(filtered_data, models[product], buying_price)
            st.plotly_chart(fig)
        elif analysis_type == "Yếu tố ảnh hưởng đến độ co giãn giá":
            fig = plot_elasticity_factors(data_to_use, product=product)
            st.plotly_chart(fig)