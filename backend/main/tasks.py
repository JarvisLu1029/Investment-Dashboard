from main.crawl_price import multithread_stock_price, get_asset_price_from_fubonlife, \
    get_stock_price_from_yahoo, get_fund_price_from_yahoo, get_usd_price_from_yahoo
from main.models import TrackingStock, StockPrice, User, TableData, ProfitData, TrackingAsset, AssetPrice

from django.utils import timezone
from django.conf import settings

from celery import shared_task
from celery.utils.log import get_task_logger

from datetime import timedelta
import matplotlib.pyplot as plt
import requests, json

logger = get_task_logger(__name__)

now = timezone.now()
# 取得今天開始的時間（即午夜 00:00:00 的時間）
start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
end_of_today = start_of_today + timedelta(days=1) - timedelta(seconds=1)

@shared_task
def update_stock_price():
    logger.info('Update Stock Price.')
    stock_set = TrackingStock.objects.all()
    stock_list = stock_set.values_list('code', flat=True)
    
    # stock_price = multithread_stock_price(None, stock_list)
    for code in stock_list:
        try:
            if code == 'USD':
                price = get_usd_price_from_yahoo()
            else:
                price = get_stock_price_from_yahoo(code)
        except:
            logger.info(f'[ERROR] - {code} Update failed')

        stock_id = TrackingStock.objects.get(code=code).id
        StockPrice.objects.create(stock_id=stock_id, price=price)

    # for code, price in stock_price.items():
    #     price = get_stock_price_from_openapi(stock.code)
    #     price = get_stock_price_from_cnyes(code)
    #     code_obj = TrackingStock.objects.get(code=code)
    #     StockPrice.objects.create(code=code_obj, price=price)
    #     n += 1

@shared_task
def update_asset_price():
    tracking_asset = TrackingAsset.objects.all()

    for asset in tracking_asset:
        asset_name = asset.asset_name
        if '基金' in asset_name:
            price = get_fund_price_from_yahoo(asset_name)
            AssetPrice.objects.create(asset_id=asset.id, price=price)
        else:
            price = get_asset_price_from_fubonlife(asset_name)
            AssetPrice.objects.create(asset_id=asset.id, price=price)

@shared_task
def update_stock_profit():
    logger.info('Update Stock and Asset Profit.')
    user_set = User.objects.all()

    # Get All User
    for user in user_set:
        table_data = TableData.objects.get(user=user)
        stock_data_list = table_data.stock_data
        asset_data_list = table_data.asset_data

        # Get user's stock profit
        today_stock_profit = 0
        for stock in stock_data_list:
            stock_code = stock[0]
            if stock_code == '':
                continue
            amount = stock[1]
            invest_price = stock[2]
            stock_price = StockPrice.objects.filter(stock_id__code=stock_code).latest('create_time').price
            stock_profit = round((float(stock_price) - float(invest_price)) * int(amount))
            today_stock_profit += stock_profit

        # Get user's asset profit
        today_asset_profit = 0
        for asset_data in asset_data_list:
            asset_name = asset_data[0]
            if asset_name == '':
                continue
            tracking_asset_currency = TrackingAsset.objects.get(asset_name=asset_name).currency
            asset = AssetPrice.objects.filter(asset_id__asset_name=asset_name).latest('create_time')
            asset_current_price = asset.price

            asset_amount = asset_data[1]
            asset_buying_price = asset_data[2]
            asset_profit = round((float(asset_current_price) - float(asset_buying_price))* float(asset_amount))
            if tracking_asset_currency == 'USD':
                exchange_rate = StockPrice.objects.filter(stock_id__code='USD').latest('create_time').price
                asset_profit = asset_profit * exchange_rate
            today_asset_profit += asset_profit

        ProfitData.objects.create(user=user, stock_profit=today_stock_profit, asset_profit=today_asset_profit)


def send_profit_to_linebot():
    # 設定LINE Messaging API的API端點
    API_URL = 'https://api.line.me/v2/bot/message/push'

    # 設定訊息物件
    message = {
        'type': 'text',
        'text': 'Hello, World!'
    }

    # 設定收件者的LINE使用者ID
    user_id = settings.LINEBOT_USER_ID

    # 將訊息和收件者打包成JSON格式的資料
    data = {
        "to": user_id,
        "messages": [{
            "type": "image",
            "originalContentUrl": 'https://6e44-114-36-114-46.ngrok-free.app/get_profit_image',
            "previewImageUrl": 'https://6e44-114-36-114-46.ngrok-free.app/get_profit_image',
        }]
    }

    # 將JSON資料轉換為字串
    payload = json.dumps(data)

    # 設定HTTP標頭
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + settings.LINEBOT_ACCESS_TOKEN
    }

    # 發送HTTP POST請求
    response = requests.post(API_URL, data=payload, headers=headers)


def create_profit_image(user):
    profit_datas = ProfitData.objects.filter(user=user)
    chart_dict = {'date': [], 'profit': []}
    for profit_data in profit_datas:
        chart_dict['date'].append(profit_data.create_time.date())
        chart_dict['profit'].append(profit_data.asset_profit + profit_data.stock_profit)

    print(chart_dict)
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(chart_dict['date'], chart_dict['profit'], marker='o', linestyle='-', color='b')
    plt.title('Profit Trend Over Time')
    plt.xlabel('Date')
    plt.ylabel('Profit')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    # Save the figure
    file_path = './static/images/profit_image.png'
    plt.savefig(file_path)

if __name__ == 'django.core.management.commands.shell':
    # print(start_of_today)
    # print(timezone.now() - timedelta(days=1))

    # update_stock_price()
    # update_asset_price()

    update_stock_profit()
    # update_asset_profit()

    # get_stock_price()
    # get_profit_data()

    # delete_wrong_data()

    # create_profit_image('Jarvis')
    # send_profit_to_linebot()