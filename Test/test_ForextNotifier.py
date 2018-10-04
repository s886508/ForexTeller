import pytest
from ForexPriceNotifier.ForexPriceNotifier import ForexNotifier
from ForexPriceNotifier.ForexPriceNotifier import ForexType
from ForexPriceNotifier.ForexPriceNotifier import PriceType

class TestNotifier(object):
    def test_NotifySetting(self):
        notifier = ForexNotifier()
        notifier.addWantedCurrency("美元(USD)")

        # Case 1: Normal
        ret = notifier.addNotify("美元(USD)", 30.0, ForexType.Buy, PriceType.Below)
        assert ret == True

        # Case 2: Wrong price data type
        ret = notifier.addNotify("美元(USD)", "30.0", ForexType.Buy, PriceType.Exceed)
        assert ret == False

        # Case 3: Empty currency string
        ret = notifier.addNotify("", "30.0", ForexType.Buy, PriceType.Exceed)
        assert ret == False

        # Case 4: Incorrect type input
        ret = notifier.addNotify("美元(USD)", 30.0, PriceType.Exceed, PriceType.Exceed)
        assert ret == False

        ret = notifier.addNotify("美元(USD)", 30.0, ForexType.Buy, ForexType.Buy)
        assert ret == False

    def testMatchPrice(self):
        notifier = ForexNotifier()
        notifier.addWantedCurrency("美元(USD)")

        key = notifier.composeCurrencyKey("美元(USD)", ForexType.Sell, PriceType.Exceed)

        # Case 1: Not call setNotify
        ret = notifier.matchCurrencyPrice(key, 30)
        assert ret == False

        # Case 2: Call SetNotify
        notifier.addNotify("美元(USD)", 30.3, ForexType.Sell, PriceType.Exceed)
        ret = notifier.matchCurrencyPrice(key, 30.4)
        assert ret == True

        key2 = notifier.composeCurrencyKey("美元(USD)", ForexType.Sell, PriceType.Below)
        notifier.addNotify("美元(USD)", 30.3, ForexType.Sell, PriceType.Below)
        ret = notifier.matchCurrencyPrice(key2, 30.4)
        assert ret == False

        # Case 3: Incorrect currency
        ret = notifier.matchCurrencyPrice("(USD)", 30.4)
        assert ret == False

        # Case 4: Incorrect price type
        ret = notifier.matchCurrencyPrice(key, "30.4")
        assert ret == False

    def testRemoveNotify(self):
        notifier = ForexNotifier()
        notifier.addWantedCurrency("美元(USD)")

        # Case 1: Normal
        notifier.addNotify("美元(USD)", 30.0, ForexType.Buy, PriceType.Below)
        ret = notifier.removeNotify("美元(USD)", ForexType.Buy, PriceType.Below)
        assert ret == True

        # Case 2: Wrong forex type or price type
        notifier.addNotify("美元(USD)", 30.0, ForexType.Buy, PriceType.Below)
        ret = notifier.removeNotify("美元(USD)", ForexType.Sell, PriceType.Below)
        assert ret == False

        ret = notifier.removeNotify("美元(USD)", ForexType.Buy, PriceType.Exceed)
        assert ret == False

        # Case 3: Empty currency string or wrong currency string
        ret = notifier.removeNotify("", ForexType.Buy, PriceType.Below)
        assert ret == False

        ret = notifier.removeNotify("(USD)", ForexType.Buy, PriceType.Below)
        assert ret == False