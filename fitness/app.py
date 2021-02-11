import json
import os
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

# import requests


def lambda_handler(event, context):

    # print(event)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": event,
            # "location": ip.text.replace("\n", "")
        }),
    }
