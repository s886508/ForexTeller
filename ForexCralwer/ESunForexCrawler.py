import requests

def retrieveForexData():
    url_esun_forex = "https://www.esunbank.com.tw/bank/personal/deposit/rate/forex/foreign-exchange-rates"
    respones = requests.get(url_esun_forex, verify = False)
    return respones.text

if __name__ == "__main__":
    html_text = retrieveForexData()
    print(html_text)
