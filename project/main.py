from trading_bot import TradingBot
from backtester import Backtester
from datetime import datetime

def main():
    # Initialize the trading bot with an initial budget (e.g., $10,000)
    initial_budget = 10000
    bot = TradingBot(initial_budget)

    # Choose whether to run live trading or backtesting
    mode = input("Enter 'live' for live trading or 'backtest' for backtesting: ").strip().lower()

    if mode == 'live':
        # Live trading mode
        while True:
            bot.run_cycle()

    elif mode == 'backtest':
        # Backtesting mode
        start_date_str = input("Enter the start date for backtesting (YYYY-MM-DD): ")
        end_date_str = input("Enter the end date for backtesting (YYYY-MM-DD): ")

        # Convert the input strings to datetime objects
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # Initialize the backtester with the trading bot and the date range
        backtester = Backtester(initial_budget, start_date, end_date)

        # Run the backtest
        backtester.run_backtest(bot)

    else:
        print("Invalid mode selected. Please enter 'live' or 'backtest'.")

if __name__ == "__main__":
    main()
