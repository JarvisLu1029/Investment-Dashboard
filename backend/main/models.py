from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import pytz

taipei_tz = pytz.timezone('Asia/Taipei')        
taipei_tz = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

class User(models.Model):
    id = models.CharField(max_length=10, blank=False, null=False, primary_key=True)
    name = models.CharField(max_length=30)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} {self.name}'


class TableData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    asset_data = models.JSONField(null=True)
    stock_data = models.JSONField(null=True)  # 用於儲存用戶的本地數據
    update_time = models.DateTimeField(auto_now_add=True)


class TrackingAsset(models.Model):
    id = models.AutoField(primary_key=True)
    asset_name = models.CharField(max_length=50, blank=False, null=False, unique=True)
    currency = models.CharField(max_length=10)
    create_time = models.DateTimeField(auto_now_add=True)


class AssetPrice(models.Model):
    id = models.AutoField(primary_key=True)
    asset = models.ForeignKey(TrackingAsset, on_delete=models.DO_NOTHING)
    price = models.FloatField()
    create_time = models.DateTimeField(auto_now_add=True)


class TrackingStock(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, blank=False, null=False, unique=True)
    name = models.CharField(max_length=50)
    market = models.CharField(max_length=10)
    create_time = models.DateTimeField(auto_now_add=True)


class StockPrice(models.Model):
    id = models.IntegerField(primary_key=True)
    stock = models.ForeignKey(TrackingStock, on_delete=models.DO_NOTHING)
    price = models.FloatField()
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        strftime = self.create_time.strftime('%Y-%m-%d %H:%M:%S')

        return f'{strftime} - {self.code.code} : {self.price}'


class ProfitData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset_profit = models.IntegerField()
    stock_profit = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        strftime = self.create_time.strftime('%Y-%m-%d %H:%M:%S')

               # Jarvis Jarvis -29942 0 2024-02-14 07:35:00
        return f'{self.user} {self.stock_profit} {self.asset_profit} {strftime}'
    
    @property
    def total_profit(self):
        return self.asset_profit + self.stock_profit