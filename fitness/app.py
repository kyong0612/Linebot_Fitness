import json
import os
# import requests
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)


def lambda_handler(event, context):

    # 環境変数取得
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
    # ok_json = os.environ["ok_json"]
    # error_json = os.environ["error_json"]

    line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(YOUR_CHANNEL_SECRET)

    # get X-Line-Signature header value
    signature = event["headers"]['x-line-signature']
    # get request body as text
    body = event["body"]
    print("Request body: " + body)

    @handler.add(MessageEvent, message=TextMessage)
    def message(line_event):
        text = line_event.message.text
        line_bot_api.reply_message(
            line_event.reply_token, TextSendMessage(text=text))

    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
        # return error_json
    except InvalidSignatureError:
        logger.error("sending message happen error")
        # return error_json
    # return ok_json
