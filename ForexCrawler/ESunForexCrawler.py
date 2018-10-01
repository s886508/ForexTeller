from bs4 import BeautifulSoup

import requests

def retrieveForexData():
    """Open ESun Bank forex site and get its html content."""
    url_esun_forex = "https://www.esunbank.com.tw/bank/personal/deposit/rate/forex/foreign-exchange-rates"
    respones = requests.get(url_esun_forex, verify = False)

    return respones.text

#
def getCurrency(html_text, currency_to_get):
    """Open ESun Bank forex site and get its html content.

    Args:
        html_text (str): Forex site html content.
        currency_to_get(list(str)): Currency string list to filter the data

    Returns:
        dict(str): Contains currency price of buy and sell.
        {'美元(USD)-Buy': 30.535, '美元(USD)-Sell': 30.565}

    """
    currency_dict = {}
    soup = BeautifulSoup(html_text, "html.parser")
    for html_str in soup.find_all("tr", class_="tableContent-light"):
        list_currency = html_str.text.strip().split("\n")
        if len(list_currency) < 5:
            print("The html content may be changed. Please modify the parsing rules")
            break
        if list_currency[0] in currency_to_get:
            currency_dict[list_currency[0] + "-Buy"] = float(list_currency[3])
            currency_dict[list_currency[0] + "-Sell"] = float(list_currency[4])

    return currency_dict


if __name__ == "__main__":
    html_text = retrieveForexData()
    #print(html_text)
    currency_dict = getCurrency(html_text, ["美元(USD)", "日圓(JPY)"])
    #print(currency_dict)

