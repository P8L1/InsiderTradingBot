import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import logging


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
            logging.error("Error: Unable to locate the insider trading table on the page.")
            return {}

        insider_data = defaultdict(list)
        rows = table.find("tbody").find_all("tr")

        logging.info(f"Found {len(rows)} rows in the table.")

        # Loop through each row in the table
        for row_index, row in enumerate(rows):
            cols = row.find_all("td")

            # Ensure there are enough columns
            if len(cols) < 17:
                logging.warning(f"Row {row_index + 1} skipped: Found {len(cols)} columns. Data: {[col.text.strip() for col in cols]}")
                continue

            # Process only the first 13 columns (index 0 to 12)
            try:
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
                logging.debug(f"Parsed data for row {row_index + 1}: {insider_data_dict}")

                price_cleaned = insider_data_dict["price"].replace("$", "").replace(",", "").strip()
                insider_data_dict["price"] = float(price_cleaned) if price_cleaned.replace(".", "").isdigit() else None

                # Clean and convert 'qty' (quantity)
                qty_cleaned = insider_data_dict["qty"].replace(",", "").replace("+", "").strip()
                insider_data_dict["qty"] = int(qty_cleaned) if qty_cleaned.isdigit() else None

                # Clean and convert 'own_change' (ownership change percentage)
                own_change_cleaned = insider_data_dict["own_change"].replace("%", "").replace("+", "").strip()
                insider_data_dict["own_change"] = float(own_change_cleaned) if own_change_cleaned.replace(".", "").isdigit() else None

                # Clean and convert 'total_value'
                total_value_cleaned = insider_data_dict["total_value"].replace("$", "").replace(",", "").strip()
                insider_data_dict["total_value"] = float(total_value_cleaned) if total_value_cleaned.replace(".", "").isdigit() else None

                # Ensure the necessary data is available before appending
                if (
                    insider_data_dict["price"] is not None
                    and insider_data_dict["qty"] is not None
                    and insider_data_dict["own_change"] is not None
                    and insider_data_dict["total_value"] is not None
                ):
                    insider_data[insider_data_dict["ticker"]].append(insider_data_dict)
                    logging.info(f"Stock {insider_data_dict['ticker']} added successfully.")
                else:
                    logging.warning(f"Row {row_index + 1} skipped: Missing critical data.")

            except (ValueError, TypeError) as e:
                logging.error(f"Error converting data for {insider_data_dict['ticker']}: {e}")
            continue

        logging.info(f"Scraped {len(insider_data)} stocks from insider data")
        return insider_data

    except requests.RequestException as e:
        logging.error(f"Error fetching insider data: {e}")
        return {}
