from dataorganiser import DataOrganiser
from data_analyzer import DataAnalyzer
from order_manager import OrderManager
import time
import logging  # Added logging for better tracking

class TradingBot:
    def __init__(self, initial_budget):
        # Initialize DataOrganiser, DataAnalyzer, and OrderManager
        self.data_organiser = DataOrganiser()
        self.data_analyzer = DataAnalyzer()
        self.order_manager = OrderManager(
            initial_budget, stop_loss_threshold=0.03, profit_taking_threshold=0.10
        )
        self.current_budget = initial_budget
        self.min_budget_to_buy = 20  # You can adjust this depending on trading rules

    def run_cycle(self):
        """
        Main method to run the trading bot's cycle.
        This will run continuously, checking for buying/selling opportunities.
        """
        logging.info("Starting new trading cycle")

        # Monitor existing holdings for selling opportunities
        self.order_manager.monitor_holdings_and_market_prices()

        # Check if enough budget is available for new trades
        if self.current_budget >= self.min_budget_to_buy:
            logging.info(f"Current budget is sufficient for new trades: ${self.current_budget}")

            # Step 1: Fetch insider trading data
            insider_trades = self.data_organiser.fetch_insider_trading_data()

            # Step 2: Sort and filter the data
            filtered_trades = self.data_analyzer.sort_and_filter_insider_trades(insider_trades)

            # Step 3: Get current stock prices for filtered trades
            self.data_organiser.get_current_stock_prices(filtered_trades)

            # Step 4: Analyze investment opportunities
            investment_opportunities = self.data_analyzer.analyze_investment_opportunities(filtered_trades)

            if investment_opportunities:
                # Step 5: Set buy targets
                self.order_manager.set_buy_targets(investment_opportunities)

                # Step 6: Monitor price changes and execute buy orders
                self.order_manager.monitor_price_changes_and_buy(investment_opportunities)

                # Update the current budget after making any trades
                self.current_budget = self.order_manager.get_remaining_budget()
                logging.info(f"Updated budget after trades: ${self.current_budget}")
            else:
                logging.info("No valid investment opportunities found.")
        else:
            logging.info(f"Not enough budget for new trades. Current budget: ${self.current_budget}")

        # Wait before starting the next cycle (for live trading scenarios)
        time.sleep(1)  # Can adjust this value for longer/shorter cycle waits
