# -*- coding: utf-8 -*-
from flask import Flask, request, abort
from bot.line_bot import ForexNotifierLineBot
from bot.settings import config
from forex.forex_notifier import ForexNotifier
from forex.esun_forex_crawler import ESunForexCrawler
from forex.setting.forex_config import ForexType, PriceType, CurrencyType
from drama_come.drama_crawler import JPDramaCrawler
from drama_come.drama_info import DramaInfo
import os

from linebot import WebhookHandler
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage
)

app = Flask(__name__)

webhook_handler = WebhookHandler(config.line_token_secret)
line_bot = ForexNotifierLineBot()
forex_notifier = ForexNotifier()
forex_crawler = ESunForexCrawler()

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
        line_bot.addUserId(event.source.user_id)
        if line_bot.get_notify_user_count() > 0:
            if forex_notifier.start(forex_crawler):
                line_bot.replyMessage(event.reply_token, "開始偵測價格與通知")
            else:
                line_bot.replyMessage(event.reply_token, "正在偵測價格與通知")
    elif "停止" == event.message.text:
        line_bot.removeUserId(event.source.user_id)
        if line_bot.get_notify_user_count() == 0:
            if forex_notifier.stop():
                line_bot.replyMessage(event.reply_token, "停止偵測價格與通知")
            else:
                line_bot.replyMessage(event.reply_token, "偵測與通知尚未啟動")
    elif event.message.text.startswith("設定"):
        handle_add_setting(event)
    elif event.message.text.startswith("取消"):
        handle_remove_setting(event)
    elif "目前設定" in event.message.text:
        handle_current_setting(event)
    elif "日劇" in event.message.text:
        handle_jp_drame_come(event)


def handle_add_setting(event):
    """Handle add setting messages.
    :param
        event (object): Messages Event from Line Server
    """
    forex_type, currency_type, price_type, price = None, None, None, None
    tokens = event.message.text.split(" ")
    if len(tokens) >= 5:
        forex_type = ForexType.get_type(tokens[1])
        currency_type = CurrencyType.get_type(tokens[2])
        price_type = PriceType.get_type(tokens[3])
        price = float(tokens[4])

    if forex_type is None or currency_type is None or price_type is None or price is None:
        line_bot.replyMessage(event.reply_token, "設定格式錯誤\n範例: '設定 買入 美元 低於 30.4'")
    elif forex_notifier.addNotify(event.source.user_id, currency_type, price, forex_type, price_type):
        line_bot.replyMessage(event.reply_token, "成功設定-通知")
    else:
        line_bot.replyMessage(event.reply_token, "設定失敗")

def handle_remove_setting(event):
    """Handle remove setting messages.
    :param
        event (object): Messages Event from Line Server
    """
    forex_type, currency_type, price_type = None, None, None
    tokens = event.message.text.split(" ")
    if len(tokens) >= 4:
        forex_type = ForexType.get_type(tokens[1])
        currency_type = CurrencyType.get_type(tokens[2])
        price_type = PriceType.get_type(tokens[3])

    if forex_type is None or currency_type is None or price_type is None:
        line_bot.replyMessage(event.reply_token, "設定格式錯誤\n範例: '取消 買入 美元 低於'")
    elif forex_notifier.removeNotify(event.source.user_id, currency_type, forex_type, price_type):
        line_bot.replyMessage(event.reply_token, "成功設定-不通知")
    else:
        line_bot.replyMessage(event.reply_token, "設定失敗")

def handle_current_setting(event):
    """Display current currency setting.
    :param
        event (object): Messages Event from Line Server
    """
    info = forex_notifier.get_notify_currency_info(event.source.user_id)
    line_bot.replyMessage(event.reply_token, info)

def handle_jp_drame_come(event):
    """Get latest drama information and push to user.
    :param
        event (object): Messages Event from Line Server
    """
    crawler = JPDramaCrawler()
    crawler.retrieve_url()
    dramas = crawler.get_dramas()

    str = DramaInfo.get_info_str(dramas)
    line_bot.replyMessage(event.reply_token, str)

if __name__ == "__main__":
    forex_notifier.addSubscriber(line_bot)
    forex_notifier.load_setting()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    forex_notifier.stop()