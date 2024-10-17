class DataAnalyzer:
    def __init__(self):
        # Define a weighting system for insider roles
        self.role_weights = {
            'CEO': 3,
            'CFO': 2,
            'Director': 1.5,
            'Other': 1  # Default weight
        }

    def sort_and_filter_insider_trades(self, insider_trades):
        """
        Enhanced filtering of insider trades based on insider role, transaction volume, and other criteria.
        """
        filtered_trades = []

        for trade in insider_trades:
            role = trade[5]  # Assuming insider role is at index 5
            transaction_volume = self._extract_transaction_volume(trade)
            company_market_cap = self._get_company_market_cap(trade[2])  # Assuming ticker symbol at index 2

            if self._is_significant_trade(trade, transaction_volume, company_market_cap):
                # Apply weighting based on role
                weight = self._get_role_weight(role)
                trade.append(weight)  # Append weight for ranking
                filtered_trades.append(trade)

        # Sort by trade weight (descending) and trade date (most recent first)
        return sorted(filtered_trades, key=lambda x: (x[-1], x[1]), reverse=True)

    def _get_role_weight(self, role):
        """
        Assign a weight based on the insider's role.
        """
        for key in self.role_weights:
            if key.lower() in role.lower():
                return self.role_weights[key]
        return self.role_weights['Other']

    def _extract_transaction_volume(self, trade):
        """
        Extract transaction volume from the trade. Assuming trade volume is at index 7.
        """
        return int(trade[7].replace(',', ''))

    def _get_company_market_cap(self, ticker_symbol):
        """
        Fetch the company's market cap (can use an API like yfinance).
        Placeholder for actual implementation.
        """
        # This function would use an API like yfinance to get market cap
        return 1000000000  # Example: 1 billion market cap

    def _is_significant_trade(self, trade, transaction_volume, market_cap):
        """
        Determine if a trade is significant based on the volume-to-market cap ratio.
        """
        threshold_ratio = 0.01  # Example: transaction must be at least 1% of market cap
        return (transaction_volume / market_cap) > threshold_ratio

    def analyze_investment_opportunities(self, filtered_trades):
        """
        Analyze filtered trades to identify the best opportunities.
        """
        # Example analysis: Return top 5 trades based on the ranking
        return filtered_trades[:5]
