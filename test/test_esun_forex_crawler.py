# -*- coding: utf-8 -*-
from forex.esun_forex_crawler import ESunForexCrawler
from forex.setting.forex_config import *

class TestCrawler(object):
    def test_retrieveForexData(self):
        url = "http://www.esunbank.com.tw/bank/personal/deposit/rate/forex/foreign-exchange-rates"

        crawler = ESunForexCrawler()
        # Case 1
        ret = crawler.retrieveForexData(url)
        assert ret == True

        # Case 2
        ret = crawler.retrieveForexData("http://www.esunbank.com.tw")
        assert ret == True

        # Case 3
        #ret = crawler.retrieveForexData("")
        #assert ret == False

    def test_getCurrency(self):
        html_text = """<tr class="tableContent-light" align="center">
                            <td data-name="外幣類型" class="itemTtitle">
                            <img src="-/media/esunbank/images/common/flags/usd.png" border="0" width="23" height="15">
                            <a href="/bank/personal/deposit/rate/forex/exchange-rate-chart?Currency=USD/TWD">美元(USD)
                            <img class="rc" src="/bank/images/esunbank/deposit/icon_rc.png" alt="走勢圖"></a></td>
                            <td data-name="即期買入匯率" class="odd">30.49</td>
                            <td data-name="即期賣出匯率" class="even">30.59</td>
                            <td data-name="網路銀行/App優惠匯率買入匯率" class="odd">30.525</td>
                            <td data-name="網路銀行/App優惠匯率賣出匯率" class="even">30.555</td>
                            <td data-name="現金買入匯率" class="odd">30.29</td>
                            <td data-name="現金賣出匯率" class="even lastTd">30.79</td></tr>"""

        crawler = ESunForexCrawler()

        currency_buy = "%s-%s" % (CurrencyType.USD.value, ForexType.Buy.value)
        currency_sell = "%s-%s" % (CurrencyType.USD.value, ForexType.Sell.value)

        # Case 1
        ret = crawler.getCurrency(["美元(USD)"], html_text)
        assert len(ret) == 2
        assert currency_buy in ret
        assert currency_sell in ret

        # Case 2
        ret = crawler.getCurrency(["美元(USD)", "人民幣(CNY)"], html_text)
        assert len(ret) == 2
        assert currency_buy in ret
        assert currency_sell in ret

        # Case 3
        ret = crawler.getCurrency(["美元"], html_text)
        assert len(ret) == 0
        assert currency_buy not in ret
        assert currency_sell not in ret

        # Case 4
        ret = crawler.getCurrency([""], html_text)
        assert len(ret) == 0
        assert currency_buy not in ret
        assert currency_sell not in ret

    def test_getTime(self):
        # Case 1: Normal
        html_text = """<div id="layout_0_rightcontent_2_ph_tabcontent_0_timeBlock" class="timeBlock">
                        <img src="/bank/images/esunbank/public/icon_time.png" border="0">生效日期：<span id="LbQuoteTime">2018年10月02日 09:06:13</span>
                        <a id="layout_0_rightcontent_2_ph_tabcontent_0_HlkForeignExchangeRates" class="green linkover" href="/bank/personal/deposit/rate/forex/foreign-exchange-rates" style="padding-left:15px;">更新報價</a>
                        </div>"""

        crawler = ESunForexCrawler()
        time = crawler.getEffectiveTime(html_text)
        assert time == "2018年10月02日 09:06:13"

        # Case 2: No span tag
        html_text = """<div id="layout_0_rightcontent_2_ph_tabcontent_0_timeBlock" class="timeBlock">
                                <img src="/bank/images/esunbank/public/icon_time.png" border="0">生效日期：
                                <a id="layout_0_rightcontent_2_ph_tabcontent_0_HlkForeignExchangeRates" class="green linkover" href="/bank/personal/deposit/rate/forex/foreign-exchange-rates" style="padding-left:15px;">更新報價</a>
                                </div>"""

        time = crawler.getEffectiveTime(html_text)
        assert len(time) == 0

        # Case 3: Empty html text
        time = crawler.getEffectiveTime("")
        assert len(time) == 0