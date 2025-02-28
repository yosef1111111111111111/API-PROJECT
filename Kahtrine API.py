import requests
import datetime
import time
import numpy as np
import pandas as pd

# Mapping fra aktiesymboler til firmanavne
COMPANY_NAMES = {
    "AAPL": "Apple Inc.",
    "TSLA": "Tesla Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com Inc.",
    "NFLX": "Netflix Inc.",
    "NVDA": "NVIDIA Corporation",
    "META": "Meta Platforms Inc."
}

class StockTracker:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.last_request_time = 0
        self.cached_data = {}  # Gem tidligere hentede aktiedata

    def get_stock_data(self, symbol):
        current_time = time.time()
        if symbol in self.cached_data:
            print(f"Bruger gemt data for {symbol} ({COMPANY_NAMES.get(symbol, symbol)}) for at spare API-kald.")
            return self.cached_data[symbol]
        
        if current_time - self.last_request_time < 60:
            wait_time = 60 - (current_time - self.last_request_time)
            print(f"Vent venligst {int(wait_time)} sekunder, da API-nøglen er gratis og har begrænsninger.")
            time.sleep(wait_time)  # Vent til vi kan lave et nyt kald

        url = f"{self.base_url}?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={self.api_key}&outputsize=compact"
        response = requests.get(url)
        data = response.json()
        self.last_request_time = time.time()
        self.cached_data[symbol] = data.get("Time Series (Daily)", {})  # Gem data lokalt
        return self.cached_data[symbol]

    def calculate_rsi(self, prices, window=14):
        """Beregn Relative Strength Index (RSI)"""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.convolve(gains, np.ones(window)/window, mode='valid')
        avg_loss = np.convolve(losses, np.ones(window)/window, mode='valid')
        rs = avg_gain / (avg_loss + 1e-10)  # Undgå division med nul
        rsi = 100 - (100 / (1 + rs))

        return rsi[-1]  # Returnér seneste RSI-værdi

    def analyze_stock(self, symbol):
        stock_data = self.get_stock_data(symbol)
        if not stock_data:
            print("Ingen data fundet. Tjek symbolet og prøv igen.")
            return

        dates = []
        prices = []

        for date, info in sorted(stock_data.items()):
            dates.append(datetime.datetime.strptime(date, "%Y-%m-%d"))
            prices.append(float(info["4. close"]))

        latest_price = prices[-1]
        rsi = self.calculate_rsi(prices)

        recommendation = "KØB" if rsi < 30 else "SÆLG" if rsi > 70 else "HOLD"
        advice = ""

        if recommendation == "KØB":
            advice = "Aktien ser undervurderet ud baseret på RSI. Overvej at købe, men tjek også fundamentale data som indtjening og markedstrends."
        elif recommendation == "SÆLG":
            advice = "RSI viser, at aktien er overkøbt. Det kan være et godt tidspunkt at tage profit, men undersøg også andre faktorer som kommende nyheder."
        else:
            advice = "Aktien er i en neutral zone. Overvej at vente på et bedre købspunkt eller sælge, hvis fundamentale faktorer peger på en nedgang."

        company_name = COMPANY_NAMES.get(symbol, symbol)
        result = {
            "Firmanavn": company_name,
            "Aktiesymbol": symbol,
            "Seneste lukkekurs": f"${latest_price:.2f}",
            "RSI": f"{rsi:.2f}",
            "Anbefaling": recommendation,
            "Rådgivning": advice
        }
        
        print("\nAktieanalyse Resultat:")
        for key, value in result.items():
            print(f"{key}: {value}")
        
        return result

if __name__ == "__main__":
    api_key = "BOH8R4USABEVNX5B"  # Udskift med din egen API-nøgle
    tracker = StockTracker(api_key)
    while True:
        symbol = input("Indtast aktiesymbol (f.eks. AAPL, TSLA) eller 'exit' for at stoppe: ")
        if symbol.lower() == 'exit':
            break
        tracker.analyze_stock(symbol)