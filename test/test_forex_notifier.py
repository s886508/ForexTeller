# -*- coding: utf-8 -*-
from forex.forex_notifier import *
from forex.setting.forex_config import CurrencyType, ForexType, PriceType
from test.mock.mock_forex_crawler import ForexCrawlerMock
from test.mock.mock_forex_subscriber import ForexSubscriberMock
import os

class TestNotifier(object):

    def test_NotifySetting(self):
        notifier = ForexNotifier()

        # Case 1: Normal
        ret = notifier.addNotify("0", CurrencyType.USD, 30.0, ForexType.Buy, PriceType.Below)
        assert ret == True

        # Case 2: Wrong price data type
        ret = notifier.addNotify("0", CurrencyType.USD, "30.0", ForexType.Buy, PriceType.Exceed)
        assert ret == False

        # Case 3: None Object
        ret = notifier.addNotify("0", None, "30.0", ForexType.Buy, PriceType.Exceed)
        assert ret == False

        # Case 4: Incorrect type input
        ret = notifier.addNotify("0", CurrencyType.USD, 30.0, PriceType.Exceed, PriceType.Exceed)
        assert ret == False

        ret = notifier.addNotify("0", CurrencyType.USD, 30.0, ForexType.Buy, ForexType.Buy)
        assert ret == False

    def testMatchPrice(self):
        currency_now = {"美元(USD)-%s" % (ForexType.Sell.value): 30.3}
        currency_now2 = {"美元(USD)-%s" % (ForexType.Sell.value): 30.4}

        # Case 1: Not call setNotify
        notify_info = ForexNotifyInfo()
        ret = notify_info.get_matched_notify(currency_now)
        assert len(ret) == 0
        notify_info = None

        # Case 2: Call SetNotify
        notify_info = ForexNotifyInfo()
        key = ForexNotifier.compose_currency_key(CurrencyType.USD, ForexType.Sell, PriceType.Exceed)
        notify_info.add_notify(key, 30.3)
        ret = notify_info.get_matched_notify(currency_now)
        assert len(ret) > 0
        notify_info = None

        notify_info = ForexNotifyInfo()
        key2 = ForexNotifier.compose_currency_key(CurrencyType.USD, ForexType.Sell, PriceType.Below)
        notify_info.add_notify(key2, 30.3)
        ret = notify_info.get_matched_notify(currency_now2)
        assert len(ret) == 0
        notify_info = None

        # Case 3: Incorrect currency
        notify_info = ForexNotifyInfo()
        notify_info.add_notify(key2, "30.3")
        ret = notify_info.get_matched_notify(currency_now)
        assert len(ret) == 0
        notify_info = None

        # Case 4: Continuous check matched
        notify_info = ForexNotifyInfo()
        notify_info.add_notify(key, 30.3)
        ret = notify_info.get_matched_notify(currency_now)
        ret = notify_info.get_matched_notify(currency_now)
        assert len(ret) == 0

    def testRemoveNotify(self):
        notifier = ForexNotifier()

        # Case 1: Normal
        notifier.addNotify("0", CurrencyType.USD, 30.0, ForexType.Buy, PriceType.Below)
        ret = notifier.removeNotify("0", CurrencyType.USD, ForexType.Buy, PriceType.Below)
        assert ret == True

        # Case 2: Wrong forex type or price type
        notifier.addNotify("0", CurrencyType.USD, 30.0, ForexType.Buy, PriceType.Below)
        ret = notifier.removeNotify("0", CurrencyType.USD, ForexType.Sell, PriceType.Below)
        assert ret == False

        ret = notifier.removeNotify("0", CurrencyType.USD, ForexType.Buy, PriceType.Exceed)
        assert ret == False

        # Case 3: None Object
        ret = notifier.removeNotify("0", None, ForexType.Buy, PriceType.Below)
        assert ret == False

    def testSynchronous(self):
        sub = ForexSubscriberMock()

        # Case 1: Normal
        notifier = ForexNotifier(50)
        notifier.addSubscriber(sub)

        notifier.addNotify("0", CurrencyType.USD, 30.9, ForexType.Buy, PriceType.Below)
        assert notifier.start(ForexCrawlerMock()) == True
        assert len(sub.update_msg) == 0
        time.sleep(5)
        assert len(sub.update_msg) > 0

        notifier.stop()

        # Case 2
        notifier = ForexNotifier(1)
        notifier.addSubscriber(sub)

        sub.update_msg = ""
        notifier.start(ForexCrawlerMock())
        notifier.addNotify("0", CurrencyType.USD, 30.9, ForexType.Buy, PriceType.Below)

        notifier.removeNotify("0", CurrencyType.USD, ForexType.Buy, PriceType.Below)
        sub.update_msg = ""
        assert len(sub.update_msg) == 0
        notifier.removeSubscriber(sub)

        # Case 3
        notifier.addNotify("0", CurrencyType.USD, 30.9, ForexType.Buy, PriceType.Below)
        sub2 = ForexSubscriberMock()
        notifier.addSubscriber(sub2)
        time.sleep(10)
        assert len(sub2.update_msg) > 0

        notifier.stop()

