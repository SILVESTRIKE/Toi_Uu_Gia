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
from statsmodels.formula.api import ols

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
    st.title("Giá Tối ưu cho Từng Sản phẩm và Combo")
    
    # Nhóm sản phẩm thành combo dựa trên SELL_ID
    sell_ids = combined_data['SELL_ID'].unique()
    single_products = []
    combos = {}
    
    for sell_id in sell_ids:
        # Lấy dữ liệu cho SELL_ID
        sell_data = combined_data[combined_data['SELL_ID'] == sell_id]
        items = sell_data['ITEM_NAME'].unique()
        if len(items) > 1:  # Nếu có nhiều hơn 1 sản phẩm, là combo
            combos[sell_id] = list(items)
        else:  # Nếu chỉ có 1 sản phẩm, là bán lẻ
            single_products.append(f"{items[0].lower()}_{sell_id}")
    
    # Hiển thị sản phẩm bán lẻ
    st.subheader("Sản phẩm bán lẻ")
    single_results = []
    for product in single_products:
        buying_price = st.number_input(f"Nhập giá mua cho {product}", min_value=0.0, value=9.0, step=0.1, key=f"buying_price_{product}")
        product_data = combined_data[(combined_data['ITEM_NAME'] == product.split('_')[0].upper()) & 
                                    (combined_data['SELL_ID'] == int(product.split('_')[1]))]
        result = find_optimal_price(product_data, models[product], buying_price)
        single_results.append({
            'Sản phẩm': product,
            'Giá tối ưu': round(result['PRICE'].iloc[0], 2),
            'Số lượng dự đoán': round(result['QUANTITY'].iloc[0], 2),
            'Lợi nhuận tối đa': round(result['PROFIT'].iloc[0], 2)
        })
    st.table(pd.DataFrame(single_results))
    
    # Hiển thị combo
    st.subheader("Combo")
    combo_results = []
    for sell_id, items in combos.items():
        # Nhập giá mua cho từng sản phẩm trong combo
        buying_prices = {}
        for item in items:
            product_key = f"{item.lower()}_{sell_id}"
            buying_prices[product_key] = st.number_input(f"Nhập giá mua cho {product_key} trong combo {sell_id}", 
                                                        min_value=0.0, value=9.0, step=0.1, key=f"buying_price_{product_key}")
        
        # Tính giá tối ưu và lợi nhuận cho combo
        total_price = 0
        total_quantity = 0
        total_profit = 0
        for item in items:
            product_key = f"{item.lower()}_{sell_id}"
            product_data = combined_data[(combined_data['ITEM_NAME'] == item.upper()) & 
                                        (combined_data['SELL_ID'] == sell_id)]
            result = find_optimal_price(product_data, models[product_key], buying_prices[product_key])
            total_price += result['PRICE'].iloc[0]
            total_quantity += result['QUANTITY'].iloc[0]
            total_profit += result['PROFIT'].iloc[0]
        
        combo_results.append({
            'Combo': f"Combo {sell_id}: {', '.join(items)}",
            'Tổng giá tối ưu': round(total_price, 2),
            'Tổng số lượng dự đoán': round(total_quantity, 2),
            'Tổng lợi nhuận tối đa': round(total_profit, 2)
        })
    st.table(pd.DataFrame(combo_results))

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
    st.title("📊 Đề xuất Điều chỉnh Giá")

    st.markdown("### 💰 Nhập giá mua riêng cho từng sản phẩm (nếu không có, sẽ dùng giá mặc định)")

    buying_price_default = st.number_input("Giá mua mặc định", min_value=0.0, value=9.0, step=0.1)

    # Tách sản phẩm thành sản phẩm đơn và combo
    sell_ids = combined_data['SELL_ID'].unique()
    single_products = []
    combos = {}

    for sell_id in sell_ids:
        sell_data = combined_data[combined_data['SELL_ID'] == sell_id]
        items = sell_data['ITEM_NAME'].unique()
        if len(items) > 1:
            combos[sell_id] = list(items)
        else:
            product_key = f"{items[0].lower()}_{sell_id}"
            single_products.append(product_key)

    # Nhập giá mua riêng cho từng sản phẩm đơn
    buying_prices = {}
    with st.expander("🔧 Nhập giá mua từng sản phẩm đơn"):
        for product_key in single_products:
            item_name, sell_id = product_key.split('_')
            item_data = combined_data[(combined_data['ITEM_NAME'] == item_name.upper()) & 
                                      (combined_data['SELL_ID'] == int(sell_id))]
            default_price = round(item_data['PRICE'].mean() * 0.8, 2)
            buying_prices[product_key] = st.number_input(
                f"Giá mua cho {item_name.upper()} (SELL_ID {sell_id})",
                value=default_price,
                min_value=0.0,
                step=0.1,
                key=f"bp_{product_key}"
            )

    # 👉 Nếu thiếu giá riêng => dùng giá mặc định
    for product in single_products:
        if product not in buying_prices:
            buying_prices[product] = buying_price_default

    # Đề xuất cho sản phẩm đơn
    st.subheader("🛍️ Đề xuất cho sản phẩm bán lẻ")
    single_recommendations = recommend_price_adjustments(combined_data, models, buying_prices)
    st.dataframe(single_recommendations, use_container_width=True)

    # Đề xuất cho combo
    st.subheader("🧃 Đề xuất cho Combo sản phẩm")

    combo_recommendations = []
    for sell_id, items in combos.items():
        combo_name = f"Combo {sell_id}: {', '.join(items)}"
        total_current_price = 0
        total_optimal_price = 0
        total_elasticity = 0
        total_adjustment = 0
        valid_items = 0

        for item in items:
            product_key = f"{item.lower()}_{sell_id}"
            product_data = combined_data[(combined_data['ITEM_NAME'] == item.upper()) & 
                                         (combined_data['SELL_ID'] == sell_id)]

            if product_key not in models or product_data.empty:
                continue

            # Lấy giá mua riêng hoặc mặc định
            buying_price = buying_prices.get(product_key, buying_price_default)

            optimal_result = find_optimal_price(product_data, models[product_key], buying_price)
            optimal_price = optimal_result['PRICE'].iloc[0]
            current_price = product_data['PRICE'].mean()
            model_fit = ols("QUANTITY ~ PRICE", data=product_data).fit()
            elasticity = model_fit.params['PRICE']

            total_current_price += current_price
            total_optimal_price += optimal_price
            total_elasticity += elasticity
            total_adjustment += abs(optimal_price - current_price)
            valid_items += 1

        if valid_items > 0:
            combo_recommendations.append({
                'Combo': combo_name,
                'Tổng giá hiện tại': round(total_current_price, 2),
                'Tổng giá tối ưu': round(total_optimal_price, 2),
                'Tổng độ co giãn': round(total_elasticity, 2),
                'Đề xuất': 'Tăng' if total_optimal_price > total_current_price else 'Giảm',
                'Tổng thay đổi': round(total_adjustment, 2)
            })

    st.dataframe(pd.DataFrame(combo_recommendations), use_container_width=True)


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