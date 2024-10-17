class Backtester:
    def __init__(self, initial_budget, start_date, end_date):
        self.initial_budget = initial_budget
        self.start_date = start_date
        self.end_date = end_date
        self.budget = initial_budget
        self.holdings = []
        self.performance_log = []

    def run_backtest(self, trading_bot):
        """
        Run the backtest over the specified date range using the trading bot's logic.
        """
        current_date = self.start_date
        while current_date <= self.end_date:
            print(f"Running backtest for {current_date}")
            # Fetch insider trading data for the current date
            insider_trades = trading_bot.data_organiser.fetch_insider_trading_data(
                start_date=current_date, end_date=current_date
            )

            # Apply trading bot's logic to make trades
            filtered_trades = trading_bot.data_analyzer.sort_and_filter_insider_trades(
                insider_trades
            )
            trading_bot.data_organiser.get_current_stock_prices(filtered_trades)

            investment_opportunities = (
                trading_bot.data_analyzer.analyze_investment_opportunities(
                    filtered_trades
                )
            )
            trading_bot.order_manager.set_buy_targets(investment_opportunities)

            # Simulate the buying process in backtesting
            trading_bot.order_manager.monitor_price_changes_and_buy(
                investment_opportunities
            )

            # Update budget after making trades
            self.budget = trading_bot.order_manager.get_remaining_budget()

            # Log the performance at the end of the day
            self.performance_log.append(
                {
                    "date": current_date,
                    "budget": self.budget,
                    "holdings": len(trading_bot.order_manager.holdings),
                }
            )

            # Move to the next day
            current_date += timedelta(days=1)

        # At the end of the backtest, print performance summary
        self._print_performance_summary()

    def _print_performance_summary(self):
        """
        Print the summary of the backtesting results.
        """
        print("\nBacktest Summary:")
        print(f"Initial Budget: {self.initial_budget}")
        print(f"Final Budget: {self.budget}")
        for log in self.performance_log:
            print(
                f"Date: {log['date']}, Budget: {log['budget']}, Holdings: {log['holdings']}"
            )
