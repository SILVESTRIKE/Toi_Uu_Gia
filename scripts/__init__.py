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

def recommend_price_adjustments(data, models, buying_prices_dict):
    recommendations = []

    for product, model in models.items():
        try:
            item_name, sell_id = product.split('_')
            item_name = item_name.upper()
            sell_id = int(sell_id)

            product_data = data[(data['ITEM_NAME'].str.upper() == item_name) & 
                                (data['SELL_ID'] == sell_id)]

            if product_data.empty or product_data['PRICE'].nunique() < 2:
                raise ValueError("Không đủ dữ liệu hoặc giá không đa dạng")

            current_price = product_data['PRICE'].mean()
            buying_price = buying_prices_dict.get(product, current_price * 0.8)

            optimal_price = find_optimal_price(product_data, model, buying_price)['PRICE'].iloc[0]

            model_fit = ols("QUANTITY ~ PRICE", data=product_data).fit()
            elasticity = model_fit.params['PRICE']

            adjustment = optimal_price - current_price

            recommendations.append({
                'Sản phẩm': product,
                'Giá hiện tại': round(current_price, 2),
                'Giá tối ưu': round(optimal_price, 2),
                'Độ co giãn': round(elasticity, 2),
                'Đề xuất': 'Tăng' if adjustment > 0 else 'Giảm',
                'Thay đổi': round(abs(adjustment), 2)
            })
        except Exception as e:
            recommendations.append({
                'Sản phẩm': product,
                'Giá hiện tại': None,
                'Giá tối ưu': None,
                'Độ co giãn': None,
                'Đề xuất': f'Lỗi: {str(e)}',
                'Thay đổi': None
            })

    return pd.DataFrame(recommendations)

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