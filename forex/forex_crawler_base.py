# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

class ForexCrawlerBase(metaclass=ABCMeta):

    @abstractmethod
    def retrieveForexData(self, forex_url = None):
        pass

    @abstractmethod
    def getEffectiveTime(self, html_text = None):
        pass

    @abstractmethod
    def getCurrency(self, currency_to_get, html_text = None):
        pass