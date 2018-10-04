from flask import Flask, request, abort
from LineBot.LineBot import ForexNotifierLineBot
from Settings.forexConfig import *
import Settings.config
import os

from linebot import WebhookHandler
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage
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
        line_bot.replyMessage(event.reply_token, "開始偵測價格與通知")
        line_bot.addUserId(event.source.user_id)
        if line_bot.get_notify_user_count() > 0:
            line_bot.run()
    elif "停止" == event.message.text:
        line_bot.replyMessage(event.reply_token, "停止偵測價格與通知。")
        if line_bot.get_notify_user_count() == 0:
            line_bot.stop()
    elif event.message.text.startswith("設定"):
        handle_setting_message(event)


def handle_setting_message(event):
    """Parse setting messages.
    :param
        event (object): Messages Event from Line Server
    """
    tokens = event.message.text.split(" ")
    if len(tokens) >= 5:
        forex_type = ForexType.getType(tokens[1].strip())
        currency_type = CurrencyType.getType(tokens[2].strip())
        price_type = PriceType.getType(tokens[3].strip())
        price = float(tokens[4].strip())

    if forex_type is None or currency_type is None or price_type is None or price is None:
        line_bot.replyMessage(event.reply_token, "設定格式錯誤\n範例: '設定 買入 美元 低於 30.4'")
    elif line_bot.addNotifyCurrency(currency_type, price, forex_type, price_type):
        line_bot.replyMessage(event.reply_token, "成功設定通知")
    else:
        line_bot.replyMessage(event.reply_token, "設定通知失敗")

if __name__ == "__main__":
    #line_bot.addNotifyCurrency(CurrencyType.USD, 30.6, ForexType.Sell, PriceType.Exceed)
    line_bot.run()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    line_bot.stop()