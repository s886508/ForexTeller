from enum import Enum

class ForexType(Enum):
    Buy = "Buy"
    Sell = "Sell"

    def getType(self, token):
        if token == "買入":
            return ForexType.Buy
        elif token == "賣出":
            return ForexType.Sell
        return None

class PriceType(Enum):
    Below = "Below"
    Exceed = "Exceed"

    def getType(self, token):
        if token == "高於":
            return PriceType.Exceed
        elif token == "低於":
            return PriceType.Below
        return None

class CurrencyType(Enum):
    USD = "美元(USD)"
    JPY = "日圓(JPY)"

    def getType(self, token):
        if token == "美元":
            return CurrencyType.USD
        elif token == "日圓":
            return CurrencyType.JPY
        return None