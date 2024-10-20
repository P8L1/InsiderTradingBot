import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime
import alpaca_trade_api as tradeapi
import time
import logging
import json
import threading

# Set up logging
logging.basicConfig(
    filename="trading_bot.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)

# Load config from JSON file
with open("config.json") as config_file:
    config = json.load(config_file)

# Alpaca API settings
API_KEY = config["alpaca_api_key"]
SECRET_KEY = config["alpaca_secret_key"]
BASE_URL = config["alpaca_base_url"]
MIN_VALUE = config["min_value"]
MIN_INSIDERS = config["min_insiders"]
GAIN_THRESHOLD = config["gain_threshold"]
DROP_THRESHOLD = config["drop_threshold"]
MIN_OWN_CHANGE = config["min_own_change"]
# Lock for thread-safe operations
lock = threading.Lock()

# Define a list to store trade history
trade_history = []


def record_trade(trade_type, ticker, quantity, price):
    """
    Records a trade in the trade history.

    Args:
        trade_type (str): The type of trade, either 'buy' or 'sell'.
        ticker (str): The stock ticker.
        quantity (int): The quantity of shares traded.
        price (float): The price at which the trade was made.
    """
    trade = {
        "type": trade_type,
        "ticker": ticker,
        "quantity": quantity,
        "price": price,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Append the trade to the trade history in a thread-safe manner
    with lock:
        trade_history.append(trade)
    logging.info(
        f"Recorded trade: {trade_type} {quantity} shares of {ticker} at ${price}"
    )


# Function to scrape OpenInsider data
def scrape_openinsider(custom_url):
    """
    Scrapes insider trading data from OpenInsider.
    Args:
        custom_url (str): The URL from OpenInsider with filters applied.
    Returns:
        dict: A dictionary where each key is a stock ticker, and the value is a list of insider transaction data.
    """
    logging.info(f"Scraping insider data from {custom_url}")

    try:
        # Make the HTTP request to OpenInsider
        response = requests.get(custom_url)
        response.raise_for_status()  # Raise exception if the request was unsuccessful
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the insider trading table
        table = soup.find("table", {"class": "tinytable"})
        if not table:
            logging.error(
                "Error: Unable to locate the insider trading table on the page."
            )
            return {}

        insider_data = defaultdict(list)
        rows = table.find("tbody").find_all("tr")

        logging.info(f"Found {len(rows)} rows in the table.")

        # Loop through each row in the table
        for row_index, row in enumerate(rows):
            cols = row.find_all("td")

            # Log the raw HTML for the row for further inspection
            logging.debug(f"Row {row_index + 1} HTML: {row}")

            # Log column values for debugging
            logging.debug(
                f"Row {row_index + 1} columns: {[col.text.strip() for col in cols]}"
            )

            # Ensure there are enough columns (skip the first and last 4 columns)
            if len(cols) < 17:
                logging.warning(
                    f"Row {row_index + 1} skipped: Found {len(cols)} columns. Data: {[col.text.strip() for col in cols]}"
                )
                continue

            try:
                # Map the relevant columns (skip the first and last 4 columns)
                insider_data_dict = {
                    "filing_date": cols[1].text.strip(),
                    "trade_date": cols[2].text.strip(),
                    "ticker": cols[3].text.strip(),
                    "company_name": cols[4].text.strip(),
                    "insider_name": cols[5].text.strip(),
                    "title": cols[6].text.strip(),
                    "trade_type": cols[7].text.strip(),
                    "price": cols[8].text.strip(),
                    "qty": cols[9].text.strip(),
                    "owned": cols[10].text.strip(),
                    "own_change": cols[11].text.strip(),
                    "total_value": cols[12].text.strip(),
                }

                # Log parsed data for each row
                logging.debug(
                    f"Parsed data for row {row_index + 1}: {insider_data_dict}"
                )

                # Convert price, quantity, own_change, and total_value to appropriate types
                insider_data_dict["price"] = (
                    float(insider_data_dict["price"].replace("$", "").replace(",", ""))
                    if insider_data_dict["price"]
                    .replace(".", "")
                    .replace(",", "")
                    .isdigit()
                    else None
                )
                insider_data_dict["qty"] = (
                    int(insider_data_dict["qty"].replace(",", "").replace("+", ""))
                    if insider_data_dict["qty"]
                    .replace(",", "")
                    .replace("+", "")
                    .isdigit()
                    else None
                )
                insider_data_dict["own_change"] = (
                    float(
                        insider_data_dict["own_change"]
                        .replace("%", "")
                        .replace("+", "")
                    )
                    if insider_data_dict["own_change"]
                    .replace(".", "")
                    .replace("%", "")
                    .replace("+", "")
                    .isdigit()
                    else None
                )
                insider_data_dict["total_value"] = (
                    float(
                        insider_data_dict["total_value"]
                        .replace("$", "")
                        .replace(",", "")
                    )
                    if insider_data_dict["total_value"]
                    .replace(".", "")
                    .replace(",", "")
                    .isdigit()
                    else None
                )

                # Log converted types
                logging.debug(
                    f"Converted types for row {row_index + 1}: {insider_data_dict}"
                )

                # Ensure the necessary data is available before appending
                if (
                    insider_data_dict["price"] is not None
                    and insider_data_dict["qty"] is not None
                    and insider_data_dict["own_change"] is not None
                    and insider_data_dict["total_value"] is not None
                ):
                    insider_data[insider_data_dict["ticker"]].append(insider_data_dict)
                    logging.info(
                        f"Stock {insider_data_dict['ticker']} added successfully."
                    )
                else:
                    logging.warning(
                        f"Row {row_index + 1} skipped: Found {len(cols)} columns. Data: {[col.text.strip() for col in cols]}"
                    )
                    logging.debug(
                        f"Missing data in row {row_index + 1}: {insider_data_dict}"
                    )

            except (ValueError, IndexError) as e:
                logging.error(f"Error parsing row {row_index + 1}: {e}")
                continue

        logging.info(f"Scraped {len(insider_data)} stocks from insider data")
        return insider_data

    except requests.RequestException as e:
        logging.error(f"Error fetching insider data: {e}")
        return {}


class TradingBot:
    def __init__(self):
        self.api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version="v2")
        self.budget = self.get_budget()
        self.positions = {}  # Track bought stocks
        self.is_running = False  # Flag to control whether the bot is running
        pass

    def get_budget(self):
        """
        Gets the current account cash balance from Alpaca.
        """
        try:
            account = self.api.get_account()
            cash_balance = float(account.cash)
            logging.info(f"Current Alpaca balance: ${cash_balance}")
            return cash_balance
        except Exception as e:
            logging.error(f"Error fetching Alpaca account balance: {e}")
            return 0

    def buy_stock(self, ticker, price, max_position_size=0.2):
        if ticker in self.positions:
            logging.info(f"Already holding position in {ticker}, skipping buy.")
            return

        max_spend = self.budget * max_position_size
        buying_power = max_spend / price
        quantity = int(buying_power)

        logging.info(f"Attempting to buy {quantity} shares of {ticker} at {price}")
        logging.info(f"Budget before trade: ${self.budget}, Max spend: ${max_spend}")

        if quantity > 0:
            try:
                self.api.submit_order(
                    symbol=ticker,
                    qty=quantity,
                    side="buy",
                    type="market",
                    time_in_force="gtc",
                )
                with lock:
                    self.positions[ticker] = {
                        "quantity": quantity,
                        "buy_price": price,
                        "highest_price": price,
                    }
                    self.budget -= quantity * price
                logging.info(f"Bought {quantity} shares of {ticker} at {price}")
                record_trade("buy", ticker, quantity, price)
            except Exception as e:
                logging.error(f"Error buying {ticker}: {e}")

    def sell_stock(self, ticker):
        if ticker in self.positions:
            quantity = self.positions[ticker]["quantity"]
            try:
                self.api.submit_order(
                    symbol=ticker,
                    qty=quantity,
                    side="sell",
                    type="market",
                    time_in_force="gtc",
                )
                logging.info(f"Sold {quantity} shares of {ticker}")
                with lock:
                    self.budget += quantity * self.get_current_price(ticker)
                    record_trade(
                        "sell", ticker, quantity, self.get_current_price(ticker)
                    )
                    del self.positions[ticker]
            except Exception as e:
                logging.error(f"Error selling {ticker}: {e}")

    def monitor_prices(
        self, gain_threshold=GAIN_THRESHOLD, drop_threshold=DROP_THRESHOLD
    ):
        while self.positions and self.is_running:
            logging.info("Starting price monitoring cycle...")
            if self.is_market_open():
                for ticker, info in self.positions.items():
                    current_price = self.get_current_price(ticker)
                    buy_price = info["buy_price"]
                    highest_price = info.get("highest_price", buy_price)

                    gain = (current_price - buy_price) / buy_price * 100

                    if current_price > highest_price:
                        with lock:
                            self.positions[ticker]["highest_price"] = current_price
                        logging.info(
                            f"{ticker} reached a new high price of {current_price}"
                        )

                    if gain >= gain_threshold:
                        logging.info(f"Stock {ticker} reached a {gain_threshold}% gain")
                        drop = (highest_price - current_price) / highest_price * 100
                        if drop >= drop_threshold:
                            logging.info(
                                f"Stock {ticker} dropped by {drop_threshold}% from its peak"
                            )
                            self.sell_stock(ticker)
            else:
                logging.info("Market is closed, skipping price monitoring.")
            time.sleep(60)  # Monitor every 60 seconds

    def get_current_price(self, ticker):
        try:
            bar = self.api.get_bars(ticker, "minute", limit=1).df.iloc[0]
            return bar.c
        except Exception as e:
            logging.error(f"Error fetching current price for {ticker}: {e}")
            return 0

    def filter_significant_transactions(
        self,
        insider_data,
        min_value=MIN_VALUE,
        min_insiders=MIN_INSIDERS,
        min_own_change=5,
    ):

        significant_stocks = []

        for ticker, transactions in insider_data.items():
            total_value = sum(item["total_value"] for item in transactions)
            unique_insiders = len(set(item["insider_name"] for item in transactions))
            avg_own_change = (
                sum(item["own_change"] for item in transactions) / len(transactions)
                if len(transactions) > 0
                else 0
            )

            # Log why certain stocks are not passing filters
            if total_value < min_value:
                logging.info(
                    f"Stock {ticker} excluded for low total value: {total_value}"
                )
                continue
            if unique_insiders < min_insiders:
                logging.info(
                    f"Stock {ticker} excluded for low unique insiders: {unique_insiders}"
                )
                continue
            if avg_own_change < min_own_change:
                logging.info(
                    f"Stock {ticker} excluded for low ownership change: {avg_own_change}"
                )

            if (
                total_value >= min_value
                and unique_insiders >= min_insiders
                and avg_own_change >= min_own_change
            ):
                significant_stocks.append(ticker)
                logging.info(
                    f"Stock {ticker} passed filters: Total value: {total_value}, Unique insiders: {unique_insiders}, Avg ΔOwn: {avg_own_change}%"
                )

        return significant_stocks

    def is_market_open(self):
        try:
            clock = self.api.get_clock()
            logging.info(f"Market is {'open' if clock.is_open else 'closed'}")
            return clock.is_open
        except Exception as e:
            logging.error(f"Error fetching market open status: {e}")
        return False

    def run_trading_cycle(
        self, insider_data, gain_threshold=GAIN_THRESHOLD, drop_threshold=DROP_THRESHOLD
    ):
        self.is_running = True
        while self.is_running:
            significant_stocks = self.filter_significant_transactions(
                insider_data,
                min_value=MIN_VALUE,
                min_insiders=MIN_INSIDERS,
                min_own_change=MIN_OWN_CHANGE,
            )

            # Check if there are no significant stocks
            if not significant_stocks:
                logging.info(
                    "No significant stocks found in this cycle. Skipping trading."
                )
                time.sleep(300)  # Wait for 5 minutes before repeating the cycle
                continue

            for ticker in significant_stocks:
                price = self.get_current_price(ticker)
                if self.budget > 0 and price > 0:
                    self.buy_stock(ticker, price)
                else:
                    logging.info("Insufficient budget or price issue, skipping stock.")
                    break
            self.monitor_prices(
                gain_threshold=gain_threshold, drop_threshold=drop_threshold
            )

            logging.info("Completed a trading cycle, repeating...")
            time.sleep(300)  # Wait for 5 minutes before repeating the cycle

    def stop(self):
        logging.info("Stopping the trading bot...")
        self.is_running = False
