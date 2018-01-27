from googlefinance import getQuotes
from config import STOCK_SYMBOLS

class StockHandler(object):
    def get_quote(self, symbol):
        result = getQuotes(symbol)
        quote = 0
        if result:
            quote = float(result[0]['LastTradePrice'])

        return quote

    def get_stockprice(self, company):
        quote = 0
        if company.lower() in STOCK_SYMBOLS:
            symbol = STOCK_SYMBOLS[company.lower()]
            quote = self.get_quote(symbol)
        return self._format_result(company, quote)

    def _format_result(self, company, quote):
        if quote > 0:
            response = 'Stock price of {company} is {quote}'
            response = response.format(company=company.title(), quote=quote)
        else:
            response = 'Stock price not found for {company}'
            response = response.format(company=company.title())

        return response

