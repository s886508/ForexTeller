from flask import Flask, request, abort
from LineBot.LineBot import ForexNotifierLineBot
from ForexPriceNotifier.ForexPriceNotifier import ForexType, PriceType
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
def handle_message(self, event):
    #line_bot.line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
    if "Start" in event.message.text:
        line_bot.addUserId(event.source.user_id)
        line_bot.run()
        line_bot.replyMessage(event.reply_token, "Start: user_id = %s" % (event.source.user_id))
    elif "Stop" in event.message.text:
        line_bot.stop()
        line_bot.replyMessage(event.reply_token, "Stop: user_id = %s" % (event.source.user_id))


if __name__ == "__main__":
    line_bot.addNotifyCurrency("美元(USD)", 30.6, ForexType.Sell, PriceType.Exceed)
    #line_bot.run()
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 5000))
    line_bot.stop()