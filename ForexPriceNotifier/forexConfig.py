from enum import Enum

class ForexType(Enum):
    Buy = "Buy"
    Sell = "Sell"

class PriceType(Enum):
    Below = "Below"
    Exceed = "Exceed"

class CurrencyType(Enum):
    USD = "美元(USD)"
    JPY = "日圓(JPY)"