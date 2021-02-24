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

    # 環境変数取得
    YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
    YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

    line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(YOUR_CHANNEL_SECRET)

    # get X-Line-Signature header value
    signature = event["headers"]['x-line-signature']
    # get request body as text
    requestBody = event["body"]

    # add handler method
    @handler.add(MessageEvent)
    def text_message(line_event):
        if (line_event.message.type == 'image'):
            print("画像を受信")
            message_id = line_event.message.id
            message_content = line_bot_api.get_message_content(message_id)
            # # tempfileに書き込み()
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as fp:
                tempfile_name = fp.name
                for chunk in message_content.iter_content():
                    fp.write(chunk)

            # リファクタリングしないと...
            googleDrive_path = "https://drive.google.com/drive/folders/1P4of3548yOXKgygy2a-FwIkIN8Qx3yvr"
            text = f'画像の保存に成功\n{googleDrive_path}'
            line_bot_api.reply_message(
                line_event.reply_token, TextSendMessage(text=text))

            uploadFileToGoogleDrive(tempfile_name)

        else:
            text = f'「{line_event.message.text}」\n画像を送信してね'
            line_bot_api.reply_message(
                line_event.reply_token, TextSendMessage(text=text))

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
        logger.error(e)


# Google Driveに保存
def uploadFileToGoogleDrive(file_name):
    print("start upload to Google Drive")
    try:
        mimeType = "image/jpeg"
        fileName = datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y/%m/%d_%H:%M:%S')

        # print("googleSeviceインスタンス化")
        service = getGoogleService()
        body = {"name": fileName, "mimeType": mimeType,
                "parents": ["1P4of3548yOXKgygy2a-FwIkIN8Qx3yvr"]}

        media_body = MediaFileUpload(
            file_name,  mimetype=mimeType, resumable=True)

        file = service.files().create(body=body,
                                      media_body=media_body, fields='id').execute()

    except Exception as e:
        logger.exception(e)


def getGoogleService():
    print("start create googleAPI service")
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    keyFile = 'googleDriveSecretKey.json'

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        keyFile, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)
