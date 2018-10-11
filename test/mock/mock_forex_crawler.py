# -*- coding: utf-8 -*-
from forexcrawler.forex_crawler_base import ForexCrawlerBase

class ForexCrawlerMock(ForexCrawlerBase):

    def retrieveForexData(self, forex_url = None):
        return True

    def getEffectiveTime(self, html_text = None):
        return "2018/10/09 09:00:00"

    def getCurrency(self, currency_to_get, html_text = None):
        return {"美元(USD)-買入" : 30.8, "美元(USD)-賣出" : 30.9}