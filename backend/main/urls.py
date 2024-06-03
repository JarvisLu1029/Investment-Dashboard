from django.urls import path
from main import user_data, linebot

urlpatterns = [
    path('user_data', user_data.table_data),
    path('serializer_table_data/<str:user>', user_data.serializer_table_data),
    path('table_profit', user_data.count_stock_profit),
    path('line_profit_chart/<str:user>', user_data.get_line_profit_chart),
    path('doughnut_profit_chart/<str:user>', user_data.get_doughnut_profit_chart),
    path('investment_list/<str:user>', user_data.get_user_investment_list),
    path('investment_price/<str:investment>', user_data.get_investment_price),
]
