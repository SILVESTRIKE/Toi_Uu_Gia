import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.formula.api import ols

def load_model(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def find_optimal_price(data, model, buying_price):
    start_price = data.PRICE.min() - 1
    end_price = data.PRICE.min() + 10
    test = pd.DataFrame(columns=["PRICE", "QUANTITY"])
    test['PRICE'] = np.arange(start_price, end_price, 0.01)
    test['QUANTITY'] = model.predict(test['PRICE'])
    test['PROFIT'] = (test["PRICE"] - buying_price) * test["QUANTITY"]
    ind = np.where(test['PROFIT'] == test['PROFIT'].max())[0][0]
    return test.iloc[[ind]]

def predict_revenue(data, model, test_price):
    quantity = model.predict(pd.DataFrame({'PRICE': [test_price]}))[0]
    revenue = test_price * quantity
    return revenue, quantity

def analyze_discount(data, model, discount_percent, buying_price):
    current_price = data.PRICE.mean()
    discounted_price = current_price * (1 - discount_percent / 100)
    quantity = model.predict(pd.DataFrame({'PRICE': [discounted_price]}))[0]
    profit = (discounted_price - buying_price) * quantity
    return {
        'discounted_price': discounted_price,
        'quantity': quantity,
        'profit': profit
    }

def recommend_price_adjustments(data, model, buying_price, product_key=None):
    """
    Recommend price adjustments for a single product based on a predictive model.
    
    Parameters:
    - data: DataFrame with historical sales data (e.g., ITEM_NAME, SELL_ID, PRICE, QUANTITY).
    - model: A trained statsmodels model for the product.
    - buying_price: Float, the cost price of the product.
    - product_key: String, product identifier (e.g., 'item_name_lower_sell_id'), optional.
    
    Returns:
    - DataFrame with recommended price adjustments and metrics.
    """
    # Extract product name and SELL_ID from product_key if provided
    if product_key:
        product_name = product_key.split('_')[0].upper()
        sell_id = int(product_key.split('_')[1])
        product_data = data[(data['ITEM_NAME'] == product_name) & (data['SELL_ID'] == sell_id)]
    else:
        product_data = data
    
    # Calculate current price (mean of historical prices)
    current_price = product_data['PRICE'].mean() if 'PRICE' in product_data and not product_data['PRICE'].empty else buying_price * 1.2
    
    # Get optimal price using find_optimal_price
    try:
        optimal_result = find_optimal_price(product_data, model, buying_price)
        optimal_price = optimal_result['PRICE'].iloc[0] if 'PRICE' in optimal_result else buying_price * 1.2
    except Exception:
        optimal_price = buying_price * 1.2  # Fallback if find_optimal_price fails
    
    # Calculate price elasticity using OLS
    try:
        model_fit = ols("QUANTITY ~ PRICE", data=product_data).fit()
        elasticity = model_fit.params['PRICE'] if 'PRICE' in model_fit.params else 0.0
    except Exception:
        elasticity = 0.0  # Fallback if OLS fails
    
    # Calculate adjustment
    adjustment = optimal_price - current_price
    recommendation = {
        'Sản phẩm': product_key if product_key else 'Unknown Product',
        'Giá hiện tại': round(current_price, 2),
        'Giá tối ưu': round(optimal_price, 2),
        'Độ co giãn': round(elasticity, 2),
        'Đề xuất': 'Tăng' if adjustment > 0 else 'Giảm' if adjustment < 0 else 'Giữ nguyên',
        'Thay đổi': round(abs(adjustment), 2)
    }
    
    return pd.DataFrame([recommendation])
def plot_price_quantity(data, model):
    prices = np.arange(data.PRICE.min() - 1, data.PRICE.min() + 10, 0.01)
    quantities = model.predict(pd.DataFrame({'PRICE': prices}))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.PRICE, y=data.QUANTITY, mode='markers', 
                            name='Dữ liệu thực tế', opacity=0.3))
    fig.add_trace(go.Scatter(x=prices, y=quantities, mode='lines', 
                            name='Dự đoán hồi quy'))
    fig.update_layout(title='Mối quan hệ Giá - Số lượng',
                     xaxis_title='Giá', yaxis_title='Số lượng')
    return fig

def plot_discount_impact(data, model, buying_price):
    discounts = np.arange(0, 51, 5)
    current_price = data.PRICE.mean()
    quantities = []
    profits = []
    
    for discount in discounts:
        price = current_price * (1 - discount / 100)
        quantity = model.predict(pd.DataFrame({'PRICE': [price]}))[0]
        profit = (price - buying_price) * quantity
        quantities.append(quantity)
        profits.append(profit)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=discounts, y=quantities, name='Số lượng'))
    fig.add_trace(go.Scatter(x=discounts, y=profits, name='Lợi nhuận', 
                            yaxis='y2'))
    fig.update_layout(
        title='Tác động của Giảm giá',
        xaxis_title='Mức giảm giá (%)',
        yaxis_title='Số lượng',
        yaxis2=dict(title='Lợi nhuận', overlaying='y', side='right')
    )
    return fig

def plot_elasticity_factors(data, product=None):
    # Nếu có sản phẩm cụ thể, lọc dữ liệu theo sản phẩm
    if product:
        product_name = product.split('_')[0].upper()
        sell_id = int(product.split('_')[1])
        filtered_data = data[(data['ITEM_NAME'] == product_name) & (data['SELL_ID'] == sell_id)]
    else:
        filtered_data = data
    
    # Tạo boxplot so sánh QUANTITY theo HOLIDAY, IS_WEEKEND, IS_SCHOOLBREAK
    fig = go.Figure()
    
    # Boxplot theo HOLIDAY
    for holiday in filtered_data['HOLIDAY'].unique():
        subset = filtered_data[filtered_data['HOLIDAY'] == holiday]
        fig.add_trace(go.Box(y=subset['QUANTITY'], name=f'Ngày lễ: {holiday}',
                             boxpoints='all', jitter=0.3, pointpos=-1.8))
    
    # Boxplot theo IS_WEEKEND
    for weekend in [0, 1]:
        subset = filtered_data[filtered_data['IS_WEEKEND'] == weekend]
        fig.add_trace(go.Box(y=subset['QUANTITY'], name=f'Cuối tuần: {"Có" if weekend else "Không"}',
                             boxpoints='all', jitter=0.3, pointpos=-1.8))
    
    # Boxplot theo IS_SCHOOLBREAK
    for schoolbreak in [0, 1]:
        subset = filtered_data[filtered_data['IS_SCHOOLBREAK'] == schoolbreak]
        fig.add_trace(go.Box(y=subset['QUANTITY'], name=f'Kỳ nghỉ học: {"Có" if schoolbreak else "Không"}',
                             boxpoints='all', jitter=0.3, pointpos=-1.8))
    
    fig.update_layout(
        title='Ảnh hưởng của Ngày lễ, Cuối tuần, Kỳ nghỉ học đến Số lượng bán',
        yaxis_title='Số lượng bán',
        xaxis_title='Yếu tố',
        boxmode='group'
    )
    return fig