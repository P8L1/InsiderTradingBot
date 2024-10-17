
import requests
from bs4 import BeautifulSoup

class DataOrganiser:
    def __init__(self):
        # Custom URL with your specific filters (latest insider trades within 3 days)
        self.custom_url = "http://openinsider.com/screener?s=&o=&pl=1&ph=&ll=&lh=&fd=1&fdr=&td=7&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&isofficer=1&iscob=1&isceo=1&ispres=1&iscoo=1&iscfo=1&isgc=1&isvp=1&isdirector=1&istenpercent=1&isother=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=1&cnt=100&page=1"

    def fetch_insider_trading_data(self):
        """
        Fetch insider trading data using the custom URL.
        """
        return self._fetch_data_from_url(self.custom_url)

    def _fetch_data_from_url(self, url):
        """
        Fetch data from the given URL.
        """
        data = set()
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch data: {e}")
            return data

        soup = BeautifulSoup(response.text, 'html.parser')
        tinytable = soup.find('table', {'class': 'tinytable'})

        if tinytable is None:
            print("No data found.")
            return data

        rows = tinytable.find('tbody').findAll('tr', recursive=False)
        for row in rows:
            cells = row.findAll('td', recursive=False)
            if not cells:
                continue
            data.add(tuple(cell.text.strip() for cell in cells))
        return data
