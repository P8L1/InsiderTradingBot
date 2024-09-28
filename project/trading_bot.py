import time
from dataorganiser import DataOrganiser
from data_analyzer import DataAnalyzer
from order_manager import OrderManager
from stock_data import StockData
from trade_info import TradeInfo

class TradingBot:
    def __init__(self):
        self.data_organiser = DataOrganiser()
        self.data_analyzer = DataAnalyzer()
        self.order_manager = OrderManager()

    import time
from dataorganiser import DataOrganiser
from data_analyzer import DataAnalyzer
from order_manager import OrderManager

class TradingBot:
    def __init__(self, initial_budget):
        self.data_organiser = DataOrganiser()
        self.data_analyzer = DataAnalyzer()
        self.order_manager = OrderManager(initial_budget)
        self.current_budget = initial_budget  # Available money to invest
        self.min_budget_to_buy = 20  # Resume buying when at least $20 is available

    def run_cycle(self):
        # Step 10: Always monitor holdings and market prices for selling opportunities
        self.order_manager.monitor_holdings_and_market_prices()

        # Check if enough budget is available to buy more stocks
        if self.current_budget >= self.min_budget_to_buy:
            # Step 1: Fetch insider trading data
            insider_trades = self.data_organiser.fetch_insider_trading_data()

            # Step 2: Sort and filter data
            filtered_trades = self.data_analyzer.sort_and_filter_insider_trades(insider_trades)

            # Step 3: Get current stock prices
            self.data_organiser.get_current_stock_prices(filtered_trades)

            # Step 4: Analyze investment opportunities
            investment_opportunities = self.data_analyzer.analyze_investment_opportunities(filtered_trades)

            # Step 5: Set buy targets
            self.order_manager.set_buy_targets(investment_opportunities)

            # Step 6: Monitor price changes and execute buy orders
            self.order_manager.monitor_price_changes_and_buy(investment_opportunities)

            # Adjust budget after buying stocks
            self.current_budget = self.order_manager.get_remaining_budget()

        # Step 14: Wait and repeat
        time.sleep(10)  # Wait for 10 seconds before repeating the cycle

