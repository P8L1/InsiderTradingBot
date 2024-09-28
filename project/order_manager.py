from stock_data import StockData

class OrderManager:
    def __init__(self, initial_budget):
        self.current_budget = initial_budget
        self.holdings = []  # List of stocks currently held

    def set_buy_targets(self, investment_opportunities):
        # Set buy targets based on available budget
        pass

    def monitor_price_changes_and_buy(self, investment_opportunities):
        # Monitor price changes and execute buy orders
        for opportunity in investment_opportunities:
            if self.current_budget >= opportunity.target_price:
                self.execute_buy(opportunity)
                self.current_budget -= opportunity.target_price

    def monitor_holdings_and_market_prices(self):
        # Monitor holdings and sell when needed (e.g., when stock increases by 10% or insider sells)
        for stock in self.holdings:
            if self.should_sell(stock):
                self.execute_sell(stock)
                self.current_budget += stock.current_price  # Update budget after selling

    def should_sell(self, stock):
        # Logic to decide whether to sell the stock
        return stock.current_price >= stock.target_price * 1.1  # Example: Sell when price is 10% higher

    def execute_buy(self, opportunity):
        # Buy the stock and add to holdings
        self.holdings.append(opportunity)
        print(f"Bought stock: {opportunity.symbol} at {opportunity.target_price}")

    def execute_sell(self, stock):
        # Sell the stock and remove from holdings
        self.holdings.remove(stock)
        print(f"Sold stock: {stock.symbol} at {stock.current_price}")

    def get_remaining_budget(self):
        return self.current_budget
