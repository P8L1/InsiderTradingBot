class TradeInfo:
    def __init__(self, insider_name, stock_symbol, trade_type, trade_price, trade_date):
        self.insider_name = insider_name
        self.stock_symbol = stock_symbol
        self.trade_type = trade_type  # e.g., 'buy' or 'sell'
        self.trade_price = trade_price
        self.trade_date = trade_date
