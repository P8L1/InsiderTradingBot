import logging  # For logging trade actions

# Assuming you have these defined in other files
from stock_data import StockData  # Replace with actual file path if necessary
from trade_info import TradeInfo  # Replace with actual file path if necessary

class OrderManager:
    def __init__(self, initial_budget, stop_loss_threshold=0.05, profit_taking_threshold=0.10):
        self.current_budget = initial_budget
        self.holdings = []  # List of stocks currently held
        self.max_position_size = 0.5  # Limit single positions to 50% of the budget
        self.stop_loss_threshold = stop_loss_threshold  # e.g., 5% stop-loss
        self.profit_taking_threshold = profit_taking_threshold  # e.g., 10% profit-taking
        self.min_budget_to_buy = 10  # Minimum budget required to make a new purchase

    def set_buy_targets(self, investment_opportunities):
        """
        Set buy targets for investment opportunities based on position sizing rules.
        """
        for opportunity in investment_opportunities:
            # Calculate position size based on available budget
            position_size = self.current_budget * self.max_position_size
            if opportunity["target_price"] <= position_size:
                opportunity["buy_target"] = opportunity["target_price"]
            else:
                opportunity["buy_target"] = position_size

    def monitor_holdings_and_market_prices(self):
        """
        Monitor holdings and sell when needed (either stop-loss or profit-taking).
        """
        for stock in self.holdings:
            if self.should_sell(stock):
                self.execute_sell(stock)
                self.current_budget += stock.current_price  # Update budget after selling

    def should_sell(self, stock):
        """
        Decide whether to sell based on stop-loss or profit-taking thresholds.
        """
        price_drop = (stock.current_price - stock.target_price) / stock.target_price
        price_increase = (stock.current_price - stock.target_price) / stock.target_price

        # If the stock falls below the stop-loss threshold
        if price_drop <= -self.stop_loss_threshold:
            logging.info(f"Selling stock {stock.symbol} due to stop-loss. Current Price: {stock.current_price}")
            return True

        # If the stock rises above the profit-taking threshold
        elif price_increase >= self.profit_taking_threshold:
            logging.info(f"Selling stock {stock.symbol} due to profit-taking. Current Price: {stock.current_price}")
            return True

        return False

    def execute_buy(self, opportunity):
        """
        Buy the stock and add it to holdings.
        """
        self.holdings.append(opportunity)
        self.current_budget -= opportunity["buy_target"]
        logging.info(f"Bought {opportunity['symbol']} at {opportunity['target_price']}. Remaining budget: {self.current_budget}")

    def execute_sell(self, stock):
        """
        Sell the stock and remove it from holdings.
        """
        self.holdings.remove(stock)
        self.current_budget += stock.current_price
        logging.info(f"Sold stock {stock.symbol} at {stock.current_price}. Updated budget: {self.current_budget}")

    def get_remaining_budget(self):
        return self.current_budget
