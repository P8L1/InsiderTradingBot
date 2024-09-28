from trading_bot import TradingBot

def main():
    # Initialize the trading bot
    bot = TradingBot()

    # Run the trading bot in a loop
    while True:
        bot.run_cycle()

if __name__ == "__main__":
    main()
