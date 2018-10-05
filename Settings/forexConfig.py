from enum import Enum

class ForexType(Enum,):
    Buy = "買入"
    Sell = "賣出"

    @staticmethod
    def get_type(token):
        if token == "買入":
            return ForexType.Buy
        elif token == "賣出":
            return ForexType.Sell
        return None

class PriceType(Enum):
    Below = "低於"
    Exceed = "高於"

    @staticmethod
    def get_type(token):
        if token == "高於":
            return PriceType.Exceed
        elif token == "低於":
            return PriceType.Below
        return None

class CurrencyType(Enum):
    USD = "美元(USD)"
    JPY = "日圓(JPY)"

    @staticmethod
    def get_type(token):
        if "美元" in token:
            return CurrencyType.USD
        elif "日圓" in token:
            return CurrencyType.JPY
        return None