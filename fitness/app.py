import json
import os
import requests
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,)

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials


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
    print("Webhook Request body: " + body)

    # add handler method
    @handler.add(MessageEvent)
    def text_message(line_event):
        if (line_event.message.type == 'image'):
            print("画像を受信")
            message_id = line_event.message.id
            message_content = line_bot_api.get_message_content(message_id)
            with open(file_path, 'wb') as fd:
                for chunk in message_content.iter_content():
                    fd.write(chunk)
        else:
            text = f'「{line_event.message.text}」\n画像を送信してね'
            line_bot_api.reply_message(
                line_event.reply_token, TextSendMessage(text=text))

    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
    except InvalidSignatureError:
        logger.error("sending message happen error")


# Google Driveに保存
def uploadFileToGoogleDrive():
    print("start upload to Google Drive")
    try:
        # ext = os.path.splitext(localFilePath.lower())[1][1:]
        # if ext == "jpg":
        #     ext = "jpeg"
        # mimeType = "image/" + ext

        service = getGoogleService()
        file_metadata = {"name": fileName, "mimeType": mimeType,
                         "parents": ["1P4of3548yOXKgygy2a-FwIkIN8Qx3yvr"]}
        media = MediaFileUpload(
            localFilePath, mimetype=mimeType, resumable=True)
        file = service.files().create(body=file_metadata,
                                      media_body=media, fields='id').execute()

    except Exception as e:
        logger.exception(e)


def getGoogleService():
    scope = ['https://www.googleapis.com/upload/drive/v3/files']
    keyFile = 'linebot-304913-1e5bdbc415f8.json'

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        keyFile, scopes=scope)
    return build("drive", "v3", credentials=credentials, cache_discovery=False)
