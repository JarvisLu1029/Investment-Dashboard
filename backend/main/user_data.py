from django.http import JsonResponse
from django.core.cache import cache
from django.utils import timezone

from rest_framework.decorators import api_view
from rest_framework import viewsets

from .models import User, TableData, TrackingStock, TrackingAsset, AssetPrice, StockPrice, ProfitData
from .serializers import TableDataSerializer

from datetime import timedelta
import json

now = timezone.now()
# 取得今天開始的時間（即午夜 00:00:00 的時間）
start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
end_of_today = start_of_today + timedelta(days=1) - timedelta(seconds=1)

@api_view(['POST', 'GET'])
def table_data(request):
    if request.method == 'POST':
        # 獲取請求中的 user
        user = request.data.get('user')
        asset_data = request.data.get('asset_data')
        stock_data = request.data.get('stock_data')

        user_id = User.objects.get(id=user)

        table_data, created = TableData.objects.get_or_create(user=user_id)

        if asset_data != None:
            table_data.asset_data = asset_data
        elif stock_data != None:
            table_data.stock_data = stock_data

        table_data.save()
        return JsonResponse({'message': 'Data saved successfully'}, status=201)
        
    elif request.method == 'GET':
        user = User.objects.get(id='Jarvis')
        # 從資料庫中獲取所有資料
        table_data, created = TableData.objects.get_or_create(user=user)

        # 將資料序列化
        # serializer = TableDataSerializer(data)
        table_data_dict = {
            'asset_data': table_data.asset_data,
            'stock_data': table_data.stock_data
        }

        # 回傳序列化後的資料
        return JsonResponse(table_data_dict , safe=False)


@api_view(['POST', 'GET'])
def serializer_table_data(request, user):
    if request.method == 'POST':
        # 獲取請求中的 user
        user = request.data.get('user')

        user = User.objects.get(id=user)
        table_data, created = TableData.objects.get_or_create(user=user)

        # 只更新某幾個欄位
        table_serializer = TableDataSerializer(instance=table_data, data=request.data, partial=True)
        
        if table_serializer.is_valid():
            table_serializer.save()
            return JsonResponse({'message': 'Data saved successfully'}, status=201)
        else:
            return JsonResponse({'message': 'Error'}, status=400)


    elif request.method == 'GET':
        user = User.objects.get(id=user)
        try:
            table_data = TableData.objects.get(user=user)
        except:
            table_data = TableData.objects.create(user=user)

        table_serializer = TableDataSerializer(table_data)

        return JsonResponse(table_serializer.data, safe=False)


@api_view(['GET'])
def count_stock_profit(request):
    # 獲取請求中的 user
    # user = request.data.get('user')
    user_id = User.objects.get(id='Jarvis')

    profit_data_in_redis = cache.get(f'{user_id}')
    
    if profit_data_in_redis != None:
        print(profit_data_in_redis)
        return JsonResponse(profit_data_in_redis, safe=False)
    
    # 從資料庫中獲取所有資料
    table_data_list = TableData.objects.get(user=user_id).stock_data

    if table_data_list == None:
        return JsonResponse({'price': [0], 'profit': [0]}, safe=False)

    price_list = []
    profit_list = []
    # 計算損益
    for table_data in table_data_list: 
        stock_code = table_data[0]
        if stock_code != '':
            stock_price = StockPrice.objects.filter(code=stock_code).latest('create_time').price
            amount = table_data[1]
            buying_price = table_data[2]
            
            price_list.append(stock_price)
            if amount != '' and buying_price != '':
                profit = round((float(stock_price) - float(buying_price)) * int(amount))
            else:
                profit = ''
            profit_list.append(profit)

    cache.set(f'{user_id}', {'price': price_list, 'profit': profit_list}, timeout=10)
    # 回傳序列化後的資料
    return JsonResponse({'price': price_list, 'profit': profit_list}, safe=False)


@api_view(['GET'])
def get_line_profit_chart(request, user):
    profit_datas = ProfitData.objects.filter(user=user)

    chart_dict = {'date': [], 'profit': []}
    for profit_data in profit_datas:
        chart_dict['date'].append(profit_data.create_time.date())
        chart_dict['profit'].append(profit_data.asset_profit + profit_data.stock_profit)

    return JsonResponse(chart_dict, safe=False)


@api_view(['GET'])
def get_doughnut_profit_chart(request, user):
    table_data = TableData.objects.get(user=user)
    profit_data = ProfitData.objects.filter(user=user).latest('create_time')

    total_asset = 0
    for data in table_data.asset_data:
        amount = data[1]
        buying_price = data[2]
        if amount == '':
            continue
        
        currency = TrackingAsset.objects.get(asset_name=data[0]).currency
        if currency == 'USD':
            usd_price = StockPrice.objects.filter(stock__code='USD').latest('create_time').price
            total_asset += round(float(amount) * float(buying_price) * usd_price)

        total_asset += round(float(amount) * float(buying_price))

    total_stock = 0
    for data in table_data.stock_data:
        amount = data[1]
        buying_price = data[2]
        if amount == '':
            continue
        total_stock += round(float(amount) * float(buying_price))
    

    chart_dict = {
            'total_investment': total_asset + total_stock, 
            'profit': profit_data.asset_profit + profit_data.stock_profit,
            'total_asset': total_asset,
            'total_stock': total_stock,
        }
    
    return JsonResponse(chart_dict, safe=False)


api_view(['GET'])
def get_user_investment_list(request, user):
    table_data = TableData.objects.get(user=user)

    investment_list = []

    for asset in table_data.asset_data:
        if asset[0] != '':
            investment_list.append(asset[0])
    
    for code in table_data.stock_data:
        if code[0] != '':
            investment_list.append(code[0])

    # print(investment_list)
    return JsonResponse({'data': investment_list}, safe=False)


api_view(['GET'])
def get_investment_price(request, investment):
    investment_data = AssetPrice.objects.filter(asset__asset_name=investment)

    if investment_data.exists() == False:
        investment_data = StockPrice.objects.filter(stock__code=investment)
    
    price_dict = {'price': [], 'create_time': []}
    for data in investment_data:
        price_dict['price'].append(data.price)
        price_dict['create_time'].append(data.create_time.date())
    
    return JsonResponse(price_dict, safe=False)
