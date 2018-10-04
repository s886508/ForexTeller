from ForexPriceNotifier.ForexPriceNotifier import ForexNotifier
from Settings.forexConfig import CurrencyType, ForexType, PriceType

class TestNotifier(object):
    def test_NotifySetting(self):
        notifier = ForexNotifier()

        # Case 1: Normal
        ret = notifier.addNotify(0, CurrencyType.USD, 30.0, ForexType.Buy, PriceType.Below)
        assert ret == True

        # Case 2: Wrong price data type
        ret = notifier.addNotify(0, CurrencyType.USD, "30.0", ForexType.Buy, PriceType.Exceed)
        assert ret == False

        # Case 3: None Object
        ret = notifier.addNotify(0, None, "30.0", ForexType.Buy, PriceType.Exceed)
        assert ret == False

        # Case 4: Incorrect type input
        ret = notifier.addNotify(0, CurrencyType.USD, 30.0, PriceType.Exceed, PriceType.Exceed)
        assert ret == False

        ret = notifier.addNotify(0, CurrencyType.USD, 30.0, ForexType.Buy, ForexType.Buy)
        assert ret == False

    def testMatchPrice(self):
        notifier = ForexNotifier()

        key = notifier.composeCurrencyKey(CurrencyType.USD, ForexType.Sell, PriceType.Exceed)
        d = {"美元(USD)-Sell-Exceed": 30.3}

        # Case 1: Not call setNotify
        ret = notifier.matchCurrencyPrice(d, key, 30)
        assert ret == False

        # Case 2: Call SetNotify
        notifier.addNotify(0, CurrencyType.USD, 30.3, ForexType.Sell, PriceType.Exceed)
        ret = notifier.matchCurrencyPrice(d, key, 30.4)
        assert ret == True

        key2 = notifier.composeCurrencyKey(CurrencyType.USD, ForexType.Sell, PriceType.Below)
        notifier.addNotify(0, CurrencyType.USD, 30.3, ForexType.Sell, PriceType.Below)
        ret = notifier.matchCurrencyPrice(d, key2, 30.4)
        assert ret == False

        # Case 3: Incorrect currency
        ret = notifier.matchCurrencyPrice(d, "(USD)", 30.4)
        assert ret == False

        # Case 4: Incorrect price type
        ret = notifier.matchCurrencyPrice(d, key, "30.4")
        assert ret == False

    def testRemoveNotify(self):
        notifier = ForexNotifier()

        # Case 1: Normal
        notifier.addNotify(0, CurrencyType.USD, 30.0, ForexType.Buy, PriceType.Below)
        ret = notifier.removeNotify(0, CurrencyType.USD, ForexType.Buy, PriceType.Below)
        assert ret == True

        # Case 2: Wrong forex type or price type
        notifier.addNotify(0, CurrencyType.USD, 30.0, ForexType.Buy, PriceType.Below)
        ret = notifier.removeNotify(0, CurrencyType.USD, ForexType.Sell, PriceType.Below)
        assert ret == False

        ret = notifier.removeNotify(0, CurrencyType.USD, ForexType.Buy, PriceType.Exceed)
        assert ret == False

        # Case 3: None Object
        ret = notifier.removeNotify(0, None, ForexType.Buy, PriceType.Below)
        assert ret == False