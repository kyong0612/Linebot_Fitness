import json
import os
import requests
import datetime
import logging
import tempfile
import pickle
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client.service_account import ServiceAccountCredentials


logger = logging.getLogger()


def lambda_handler(event, context):

    # LINE_USER_INFO
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

    line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(YOUR_CHANNEL_SECRET)

    # get X-Line-Signature header value
    signature = event["headers"]['x-line-signature']
    # get request body as text
    requestBody = event["body"]

    print("***GET REQUEST***\n", event)

    # add handler method
    @handler.add(MessageEvent)
    def text_message(line_event):
        try:
            if (line_event.message.type == 'image'):
                print("***画像を受信***")
                message_id = line_event.message.id
                message_content = line_bot_api.get_message_content(message_id)
                # # tempfileに受け付けた画像を書き込み
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as fp:
                    tempfile_name = fp.name
                    for chunk in message_content.iter_content():
                        fp.write(chunk)

                googleDrive_path = "https://drive.google.com/drive/folders/1P4of3548yOXKgygy2a-FwIkIN8Qx3yvr"
                message = f'ナイスファイト!ダァーー!\n{googleDrive_path}'

                line_bot_api.reply_message(
                    line_event.reply_token, TextSendMessage(text=message))

                # tempfileの画像をgoogleDriveに転送
                sendMessage = uploadFileToGoogleDrive(tempfile_name)

            else:
                # 受付メッセージをおうむ返し
                text = f'「{line_event.message.text}」\n画像を送信しろ!!'
                line_bot_api.reply_message(
                    line_event.reply_token, TextSendMessage(text=text))

        except Exception as e:
            line_bot_api.reply_message(
                line_event.reply_token, TextSendMessage(text=e))

    try:
        handler.handle(requestBody, signature)
    except LineBotApiError as e:
        logger.error(
            "Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
    except InvalidSignatureError:
        logger.error("sending message happen error")
    except Exception as e:
        logger.error("handler error\n", e)


# Google Driveに保存
def uploadFileToGoogleDrive(file_name):
    mimeType = "image/jpeg"
    fileName = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y/%m/%d_%H:%M:%S')

    service = getGoogleService()
    body = {"name": fileName, "mimeType": mimeType,
            "parents": ["1P4of3548yOXKgygy2a-FwIkIN8Qx3yvr"]}

    media_body = MediaFileUpload(
        file_name, mimetype=mimeType, resumable=True)

    print("***WRITE FILE TO GOOGLE DRIVE***")

    # ここで処理が終わる
    file = service.files().create(body=body,
                                  media_body=media_body, fields='id').execute()


def getGoogleService():
    print("***CREATE GOOGLE CREDENTIALS***")
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    keyFile = 'googleDriveSecretKey.json'

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        keyFile, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)
