from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from linebot.models import TemplateSendMessage, ButtonsTemplate, PostbackAction, MessageAction, URIAction
from linebot.models import CarouselTemplate, CarouselColumn

import requests, os

line_bot_api = LineBotApi(settings.LINEBOT_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINEBOT_CHANNEL_SECRET)

@csrf_exempt
@api_view(['POST'])
def callback(request):
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.body.decode('utf-8')
    print(f'request body: {body}')    

    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        return JsonResponse({'detail': 'Invalid signature.'}, status=400)

    return HttpResponse('OK')


@api_view(['GET'])
def get_profit_image(request):
    image_path = os.path.join('./static/', 'images', 'profit_image.png')
    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    else:
        raise JsonResponse({'detail': 'Invalid image.'}, status=400)