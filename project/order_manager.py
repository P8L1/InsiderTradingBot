# Import the necessary modules
from stock_data import StockData  # Assuming StockData is used for stock-related info
from trade_info import TradeInfo  # Assuming TradeInfo is used for trade execution info
import alpaca_trade_api as tradeapi  # Alpaca API for executing trades
import logging

class OrderManager:
    def __init__(self, stop_loss_threshold=0.05, profit_taking_threshold=0.10):
        self.holdings = []  # List of stocks currently held
        self.max_position_size = 0.5  # Limit single positions to 50% of the budget
        self.stop_loss_threshold = stop_loss_threshold  # e.g., 5% stop-loss
        self.profit_taking_threshold = profit_taking_threshold  # e.g., 10% profit-taking

        # Initialize Alpaca API (replace with your actual API keys)
        self.api = tradeapi.REST('PK4K9SP88IAHUVS9NF5W', '3i3QPY79HRKNN9t9sol0U88watyhNsQpFc3r6dHa', base_url='https://paper-api.alpaca.markets/v2')

    def get_available_budget(self):
        """
        Fetch the available cash balance from the Alpaca account.
        """
        account = self.api.get_account()
        return float(account.cash)  # Returns the available cash in the account

    def set_buy_targets(self, investment_opportunities):
        """
        Set buy targets for investment opportunities based on position sizing rules.
        """
        available_budget = self.get_available_budget()  # Dynamic budget from Alpaca
        for opportunity in investment_opportunities:
            position_size = available_budget * self.max_position_size
            if opportunity["target_price"] <= position_size:
                opportunity["buy_target"] = opportunity["target_price"]
            else:
                opportunity["buy_target"] = position_size

    def monitor_holdings_and_market_prices(self):
        """
        Monitor holdings and sell when needed (either stop-loss, profit-taking, or price monitoring).
        """
        for stock in self.holdings:
            current_price = self.get_stock_price(stock.symbol)
            
            # Monitor for a 3% price increase and start tracking
            price_increase = (current_price - stock.purchase_price) / stock.purchase_price

            # If the price has increased by 3%, start monitoring every minute
            if price_increase >= 0.03 and not stock.monitoring:
                logging.info(f"Stock {stock.symbol} has increased by 3%. Starting minute-to-minute monitoring.")
                stock.monitoring = True
                stock.highest_price = current_price

            # If the stock is being monitored, check every minute if it starts falling
            if stock.monitoring:
                logging.info(f"Monitoring stock {stock.symbol}. Current price: {current_price}, Highest price: {stock.highest_price}")
                
                # Update the highest price during the monitoring
                if current_price > stock.highest_price:
                    stock.highest_price = current_price
                
                # If the stock starts falling from the highest price, sell it
                elif current_price < stock.highest_price:
                    logging.info(f"Stock {stock.symbol} has started falling. Selling at {current_price}.")
                    self.execute_sell(stock)
                    stock.monitoring = False

    def get_stock_price(self, symbol):
        """
        Fetch the current stock price using Alpaca API.
        """
        barset = self.api.get_barset(symbol, 'minute', 1)
        return barset[symbol][0].c  # The current price

    def execute_buy(self, opportunity):
        """
        Buy the stock using Alpaca paper trading and add it to holdings.
        """
        try:
            available_budget = self.get_available_budget()
            symbol = opportunity['symbol']
            qty = available_budget // opportunity['target_price']  # Calculate quantity to buy

            if qty > 0:
                self.api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                # Add to holdings with monitoring set to False initially
                stock_data = {
                    'symbol': symbol,
                    'qty': qty,
                    'purchase_price': opportunity['target_price'],
                    'monitoring': False,  # Will monitor if price increases by 3%
                    'highest_price': opportunity['target_price']  # Track highest price when monitoring
                }
                self.holdings.append(stock_data)
                logging.info(f"Bought {symbol} at {opportunity['target_price']}.")
            else:
                logging.warning(f"Not enough budget to buy {symbol}.")
        except Exception as e:
            logging.error(f"Error executing buy order for {opportunity['symbol']}: {e}")

    def execute_sell(self, stock):
        """
        Sell the stock using Alpaca paper trading and remove it from holdings.
        """
        try:
            symbol = stock['symbol']
            qty = stock['qty']  # Quantity of the stock to sell
            
            self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='gtc'
            )
            # Remove from holdings
            self.holdings.remove(stock)
            logging.info(f"Sold {symbol} at {self.get_stock_price(symbol)}.")
        except Exception as e:
            logging.error(f"Error executing sell order for {stock['symbol']}: {e}")
