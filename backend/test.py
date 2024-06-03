from django.utils import timezone
from main.models import User, TableData, TrackingStock, ProfitData, TrackingAsset, AssetPrice
from datetime import timedelta

now = timezone.now()
# 取得今天開始的時間（即午夜 00:00:00 的時間）
start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
end_of_today = start_of_today + timedelta(days=1) - timedelta(seconds=1)

user = User.objects.get(id='Jarvis')
data = TableData.objects.get(user=user)

print(data.asset_data)
# data_list = data.asset_data
# for data in data_list:
#     TrackingAsset.objects.create(asset_name=data[0])

data_obj = TableData.objects.get(user=user)
asset_data = data_obj.asset_data
for index, data in enumerate(asset_data):
    tracking = TrackingAsset.objects.get(asset_name=data[0])
    try:
        tracking_current_obj = AssetPrice.objects.get(asset_name=tracking, create_time__range=(start_of_today, end_of_today))
    
    except AssetPrice.DoesNotExist:
        asset_data[index][4] = 0
        asset_data[index][5] = 0
        continue
    
    tracking_current_price = tracking_current_obj.price
    tracking_buying_price = float(data[2])
    tracking_ammount = float(data[1])
    asset_data[index][4] = tracking_current_price
    asset_data[index][5] = int((tracking_current_price - tracking_buying_price) * tracking_ammount)

data_obj.save()

print(tracking_current_price)
