import pytest
from ForexPriceNotifier.ForexPriceNotifier import ForexNotifier
from ForexPriceNotifier.ForexPriceNotifier import ForexType

class TestNotifier(object):
    def test_NotifySetting(self):
        notifier = ForexNotifier(["美元(USD)"])

        # Case 1: Normal
        ret = notifier.setNotify("美元(USD)", 30.0, ForexType.Buy)
        assert ret == True

        # Case 2: Wrong price data type
        ret = notifier.setNotify("美元(USD)", "30.0", ForexType.Buy)
        assert ret == False

        # Case 3: Empty currency string
        ret = notifier.setNotify("", "30.0", ForexType.Buy)
        assert ret == False
