from rest_framework import serializers
from .models import User, TableData, TrackingStock, StockPrice, AssetPrice, TrackingAsset

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']

class TableDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableData
        fields = ['asset_data', 'stock_data']
        
    def update(self, instance, validated_data):
        # 如果使用者建入的資料 Tacking 裡沒有，就新建入資料庫 
        stock_data_list = validated_data.get('stock_data')
        if stock_data_list != None:
            stock_code_list = [stock_data[0] for stock_data in stock_data_list]
            for code in stock_code_list:
                if code != '' and (len(code) == 5 or len(code) == 4) :
                    TrackingStock.objects.get_or_create(code=code)
        
        asset_data_list = validated_data.get('asset_data')
        if asset_data_list != None:
            asset_name_list = [asset_data[0] for asset_data in asset_data_list]
            for asset_name in asset_name_list:
                if asset_name != '' and len(asset_name) >= 4:
                    TrackingAsset.objects.get_or_create(asset_name=asset_name)

        # 更新模型實例的欄位
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)

        stock_data = ret['stock_data']
        if stock_data == None:
            return ret

        # Table 回傳的資料要經過價格查詢
        update_stock_data = []
        for table_data in stock_data:
            code = table_data[0]
            if code == '':
                continue
            stock = StockPrice.objects.filter(stock__code=code)

            if stock.exists():
                current_price = stock.latest('create_time').price
                amount = table_data[1]
                buying_price = table_data[2]
                profit = round((float(current_price) - float(buying_price)) * int(amount))
            else:
                current_price = 0
                profit = 0

            table_data[4] = current_price
            table_data[5] = profit

            update_stock_data.append(table_data)

        asset_table = ret['asset_data']
        if asset_table == None:
            return ret
        
        update_asset_data = []
        for asset_data in asset_table:
            asset_name = asset_data[0]
            if asset_name == '':
                continue
            asset = AssetPrice.objects.filter(asset__asset_name=asset_name)
            if asset.exists():
                current_price = asset.latest('create_time').price
                amount = asset_data[1]
                buying_price = asset_data[2]
                profit = round((float(current_price) - float(buying_price)) * int(float(amount)))
            else:
                current_price = 0
                profit = 0

            asset_data[4] = current_price
            asset_data[5] = profit

            update_asset_data.append(asset_data)

        ret['asset_data'] = update_asset_data

        return ret
