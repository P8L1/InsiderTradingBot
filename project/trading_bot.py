from dataorganiser import DataOrganiser
from data_analyzer import DataAnalyzer
from order_manager import OrderManager
import time  # For the time.sleep() function


class TradingBot:
    def __init__(self, initial_budget):
        self.data_organiser = DataOrganiser()
        self.data_analyzer = DataAnalyzer()
        self.order_manager = OrderManager(
            initial_budget, stop_loss_threshold=0.03, profit_taking_threshold=0.10
        )
        self.current_budget = initial_budget
        self.min_budget_to_buy = 20

    def run_cycle(self):
        """
        Main method to run the trading bot's cycle.
        """
        # Monitor holdings for selling opportunities
        self.order_manager.monitor_holdings_and_market_prices()

        # Check if enough budget is available for new trades
        if self.current_budget >= self.min_budget_to_buy:
            # Step 1: Fetch insider trading data (using pre-filtered URL)
            insider_trades = self.data_organiser.fetch_insider_trading_data()

            # Step 2: Sort and filter data
            filtered_trades = self.data_analyzer.sort_and_filter_insider_trades(insider_trades)

            # Step 3: Get current stock prices for filtered trades
            self.data_organiser.get_current_stock_prices(filtered_trades)

            # Step 4: Analyze investment opportunities
            investment_opportunities = self.data_analyzer.analyze_investment_opportunities(filtered_trades)

            # Step 5: Set buy targets
            self.order_manager.set_buy_targets(investment_opportunities)

            # Step 6: Monitor price changes and execute buy orders
            self.order_manager.monitor_price_changes_and_buy(investment_opportunities)

            # Update budget after making trades
            self.current_budget = self.order_manager.get_remaining_budget()

        # Wait between cycles for live trading
        time.sleep(10)  # Only sleep when in live mode
