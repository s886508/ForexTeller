import pytest
from ForexPriceNotifier.ForexPriceNotifier import ForexNotifier
from ForexPriceNotifier.ForexPriceNotifier import ForexType
from ForexPriceNotifier.ForexPriceNotifier import PriceType

class TestNotifier(object):
    def test_NotifySetting(self):
        notifier = ForexNotifier(["美元(USD)"])

        # Case 1: Normal
        ret = notifier.setNotify("美元(USD)", 30.0, ForexType.Buy, PriceType.Below)
        assert ret == True

        # Case 2: Wrong price data type
        ret = notifier.setNotify("美元(USD)", "30.0", ForexType.Buy, PriceType.Exceed)
        assert ret == False

        # Case 3: Empty currency string
        ret = notifier.setNotify("", "30.0", ForexType.Buy, PriceType.Exceed)
        assert ret == False

    def testMatchPrice(self):
        notifier = ForexNotifier(["美元(USD)"])

        key = notifier.composeCurrencyKey("美元(USD)", ForexType.Sell, PriceType.Exceed)

        # Case 1: Not call setNotify
        ret = notifier.matchCurrencyPrice(key, 30)
        assert ret == False

        # Case 2: Call SetNotify
        notifier.setNotify("美元(USD)", 30.3, ForexType.Sell, PriceType.Exceed)
        ret = notifier.matchCurrencyPrice(key, 30.4)
        assert ret == True

        key2 = notifier.composeCurrencyKey("美元(USD)", ForexType.Sell, PriceType.Below)
        notifier.setNotify("美元(USD)", 30.3, ForexType.Sell, PriceType.Below)
        ret = notifier.matchCurrencyPrice(key2, 30.4)
        assert ret == False

        # Case 3: Incorrect currency
        ret = notifier.matchCurrencyPrice("(USD)", 30.4)
        assert ret == False

        # Case 3: Incorrect price type
        ret = notifier.matchCurrencyPrice(key, "30.4")
        assert ret == False