# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from .setting.forex_config import *
from .forex_crawler_base import ForexCrawlerBase
import requests

ESUN_FOREX_URL = "http://www.esunbank.com.tw/bank/personal/deposit/rate/forex/foreign-exchange-rates"

class ESunForexCrawler(ForexCrawlerBase):

    def __init__(self):
        self.url_ = ESUN_FOREX_URL
        self.html_text_ = ""

    def retrieveForexData(self, forex_url = None):
        """Open ESun Bank forex site and get its html content.
        Args:
            forex_url (str): The website to get forex data.

        Returns:
             Return True if html content get successfully.
        """
        if forex_url is None:
            forex_url = self.url_

        respone = requests.get(forex_url)
        self.html_text_ = respone.text
        return len(self.html_text_) > 0

    def getEffectiveTime(self, html_text = None):
        """Get currency effective date and time.

        Args: html_text (str) :Forex site html content.

        Returns:
            Return the time string if parsed. Otherwise, return empty string.

        """
        if html_text is None:
            html_text = self.html_text_

        soup = BeautifulSoup(html_text, "html.parser")
        time = soup.find("span", id="LbQuoteTime")
        if time is None:
            return ""
        return time.text

    def getCurrency(self, currency_to_get, html_text = None):
        """Open ESun Bank forex site and get its html content.

        Args:
            currency_to_get(list(str)): Currency string list to filter the data
            html_text (str): Forex site html content.

        Returns:
            dict(str): Contains currency price of buy and sell.
            {'美元(USD)-Buy': 30.535, '美元(USD)-Sell': 30.565}

        """
        if html_text is None:
            html_text = self.html_text_

        currency_dict = {}
        soup = BeautifulSoup(html_text, "html.parser")
        for html_str in soup.find_all("tr", class_="tableContent-light"):
            list_currency = html_str.text.strip().split("\n")
            if len(list_currency) < 5:
                print("The html content may be changed. Please modify the parsing rules")
                break
            if list_currency[0] in currency_to_get:
                currency_dict["%s-%s" % (list_currency[0], ForexType.Buy.value)] = float(list_currency[3])
                currency_dict["%s-%s" % (list_currency[0], ForexType.Sell.value)] = float(list_currency[4])

        if len(currency_dict) == 0:
            print("Cannot match given currency.")

        return currency_dict