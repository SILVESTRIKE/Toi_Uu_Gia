import pandas as pd

def load_data():
    # Tải và xử lý dữ liệu
    sales = pd.read_csv('data/Cafe - Sell Meta Data.csv')
    transactions = pd.read_csv('data/Cafe - Transaction - Store.csv')
    date_info = pd.read_csv('data/DateInfo.csv')
    
    # Xử lý giá trị thiếu
    date_info['HOLIDAY'] = date_info['HOLIDAY'].fillna("No Holiday")
    
    # Gộp dữ liệu
    data1 = pd.merge(sales.drop(['ITEM_ID'], axis=1), 
                    transactions.drop(['SELL_CATEGORY'], axis=1), 
                    on='SELL_ID')
    data1columns = data1.groupby(['SELL_ID', 'SELL_CATEGORY', 'ITEM_NAME', 'CALENDAR_DATE', 'PRICE']).QUANTITY.sum()
    intermediate_data = data1columns.reset_index()
    combined_data = pd.merge(intermediate_data, date_info, on='CALENDAR_DATE')
    
    # Lọc dữ liệu BAU (Business As Usual) với IS_OUTDOOR=1
    bau2_data = combined_data[(combined_data['HOLIDAY'] == 'No Holiday') & 
                             (combined_data['IS_SCHOOLBREAK'] == 0) & 
                             (combined_data['IS_WEEKEND'] == 0) & 
                             (combined_data['IS_OUTDOOR'] == 1)]
    
    return combined_data, bau2_data
