from flask import Flask, request, abort
from LineBot.LineBot import ForexNotifierLineBot
from ForexPriceNotifier.forexConfig import *
import Settings.config
import os

from linebot import WebhookHandler
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, sources
)

app = Flask(__name__)

webhook_handler = WebhookHandler(Settings.config.line_token_secret)
line_bot = ForexNotifierLineBot()

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        webhook_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@webhook_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if "啟動" == event.message.text:
        line_bot.replyMessage(event.reply_token, "開始偵測資料與推送")
        line_bot.addUserId(event.source.user_id)
        line_bot.run()
    elif "停止" == event.message.text:
        line_bot.replyMessage(event.reply_token, "停止偵測資料與推送")
        line_bot.stop()


if __name__ == "__main__":
    line_bot.addNotifyCurrency(CurrencyType.USD, 30.6, ForexType.Sell, PriceType.Exceed)
    #line_bot.run()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    line_bot.stop()