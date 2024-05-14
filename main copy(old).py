# path/filename: main.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
plt.style.use('ggplot')

def get_coin_price(coin_symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin_symbol}USDT"
    response = requests.get(url)
    if response.status_code == 200:
        price_data = response.json()
        if 'price' in price_data:
            return float(price_data['price'])
        else:
            print(f"No price key in response for {coin_symbol}: {price_data}")
            return None
    else:
        print(f"Error fetching price for {coin_symbol}: {response.text}")
        return None


def fetch_historical_prices(symbol, interval='1d'):
    endpoint = f'https://api.binance.com/api/v3/klines'
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=365)  # Fetch data for the last year

    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': int(start_time.timestamp() * 1000),
        'endTime': int(end_time.timestamp() * 1000),
        'limit': 1000
    }
    
    response = requests.get(endpoint, params=params)
    data = response.json()
    prices = [float(item[4]) for item in data]  # Closing prices
    dates = [datetime.fromtimestamp(item[0] / 1000).replace(tzinfo=timezone.utc) for item in data]

    return dates, prices


class BudgetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Churnut - Cryptocurrency Budgeting Service')
        self.geometry('800x600')
        self.portfolio = {}
        self.portfolio2 = {}
        self.current_frame = None
        

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)  # Central row where the frame will be, less flexible
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=2)  # Central column, less flexible
        self.grid_columnconfigure(2, weight=1)

        self.frames = {}
        pages = (BudgetInputPage,CryptoSelectionPage,PortfolioOverviewPage)
        
    
        for F in pages:
                page_name = F.__name__
                frame = F(parent=self, controller=self)
                self.frames[page_name] = frame
                frame.grid(row=1, column=1, sticky="nsew")

     

      
           

        self.show_frame("BudgetInputPage")

    def show_frame(self, page_name):
            frame = self.frames[page_name]
            frame.tkraise()
            self.current_frame = page_name
            print(f"Current frame set to {page_name}")
            print(f"Current frame set to {page_name}, retrieving data...")
            if page_name == "PortfolioOverviewPage":
             frame.display_coins()
     

    def set_portfolio(self,symbol,value):
        self.portfolio[symbol] = value
        print(f"Portfolio set - {symbol}: {value}")
        print(self.portfolio)
    def get_portfolio(self,symbol):
        value = self.portfolio.get(symbol)
        print(f"Portfolio get - {symbol}: {value}")
        return self.portfolio.get(symbol)
    
    def set_portfolio2(self,symbol,value):
        self.portfolio2[symbol] = value

    def get_portfolio2(self,symbol):
        return self.portfolio2.get(symbol)

    def update_graph(self, selected_cryptos, objet):
        objet.fig.clear()
        plot = objet.fig.add_subplot(1, 1, 1)

        for crypto in selected_cryptos:
            symbol = crypto['symbol']
            name = crypto['name']
            dates, prices = fetch_historical_prices(symbol + 'USDT')
            if prices:
                plot.plot(dates, prices, label=name)
            else:
                print(f"Could not retrieve price for {symbol}")

        plot.set_title("Cryptocurrency Prices Over Time")
        plot.set_xlabel("Date")
        plot.set_ylabel("Price in USD")
        plot.legend()
        plot.xaxis_date()  # Ensure x-axis is treated as dates
        plot.figure.autofmt_xdate()  # Auto-format dates

        objet.canvas.draw()

class BudgetInputPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="Enter your budget for cryptocurrency investment:")
        label.pack(pady=(20,10),expand=True)
        

        self.budget_entry = tk.Entry(self)
        self.budget_entry.pack(pady=(0,20),expand=True)
        

        submit_button = tk.Button(self, text="Submit", command=lambda: [self.on_submit(),self.controller.show_frame("CryptoSelectionPage")])
        submit_button.pack(pady=(0,10),expand=True)
    

        

    def on_submit(self):
        budget = self.budget_entry.get()
        print(f"Budget entered: {budget}")
        # Placeholder for future functionality

class CryptoSelectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selections = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Minimal weight for title
        self.grid_rowconfigure(1, weight=0)  # Minimal weight for cryptocurrency labels and entries
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=1)  # Higher weight for graph row, so it takes up most of the space
        self.grid_rowconfigure(5, weight=0)


        label = tk.Label(self, text="Select Cryptocurrencies and Show Their Real-time Prices")
        label.grid(row=0, column=0, sticky="ew")
        self.fig = Figure(figsize=(5, 2), dpi=100)  # Adjust figure size as needed
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=4, column=0, sticky="nsew")
        
        

        self.crypto_details = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'ADA': 'Cardano',
        }


        self.entries = {}
        self.deuxepage()
        self.show_graph()

    def crypto_infos(self):
        return list(self.crypto_details.keys())
        
    def deuxepage(self):
        for i, (symbol, name) in enumerate(self.crypto_details.items()):
                price = get_coin_price(symbol)
                prompt = tk.Entry(self)
                prompt.grid(row=i+1, column=0, sticky="e")
                self.entries[symbol] = prompt
                prompt.bind('<KeyRelease>', lambda e,s=symbol: self.update_price(s))
                chk = tk.Label(self, text=f"{name} ({symbol}): {price} USDT")
                chk.grid(row=i+1, column=0, sticky="w")
                self.entries[symbol].label = chk
                

            

        submit_button = tk.Button(self, text="Submit", command=lambda: [self.controller.frames["PortfolioOverviewPage"].update_coins(),self.controller.show_frame("PortfolioOverviewPage")])
        submit_button.grid(row=5, column=0, sticky="ew")
    
    def update_price(self,symbol):
        entry = self.entries[symbol]
        
        try:
                    your_price_usd = float(entry.get())             # Get the current value from the widget that received the key release
                    raw_total_price_usd = get_coin_price(symbol)
                    value = (your_price_usd/raw_total_price_usd) * 1
                    entry.label.config(text=f"{self.crypto_details[symbol]} ({symbol}): {value} {raw_total_price_usd} USDT")
                    self.controller.set_portfolio(symbol,your_price_usd)
                    self.controller.set_portfolio2(symbol,value)
                    
        except ValueError:
                    raw_total_price_usd = get_coin_price(symbol)
                    entry.label.config(text=f"{self.crypto_details[symbol]} ({symbol}): {0} USDT")
                    self.controller.set_portfolio(symbol,0)
                    self.controller.set_portfolio2(symbol,0)

               
        
        

    def show_graph(self):
        selected_cryptos = [{'symbol': symbol, 'name': name} for symbol, name in self.crypto_details.items()]
        if selected_cryptos:
            self.show_graph_for_cryptos(selected_cryptos)
        else:
            messagebox.showinfo("Selection Needed", "Please select at least one cryptocurrency.")

    def show_graph_for_cryptos(self, selected_cryptos):
        self.controller.update_graph(selected_cryptos, self)

    


        


class PortfolioOverviewPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="Portfolio Overview")
        label.pack(pady=10)
        print("Initializing PortfolioOverviewPage")
        print(f"el patron esta {self.controller.current_frame}")
        self.text_list = {}
        

    

    def display_coins(self):
            print(f"el patron esta {self.controller.current_frame}")
            print("Displaying coins...")
            symbols = self.controller.frames["CryptoSelectionPage"].crypto_infos()
            for symbol in symbols:
                print(self.text_list)
                text,text2 = self.text_list[symbol]
                print(f"Displaying - {symbol}: {text}, {text2}")
                string_label = f"{symbol} : {text} {text2}"
                label = tk.Label(self,text=string_label)
                label.pack()
    
    def update_coins(self):
        symbols = self.controller.frames["CryptoSelectionPage"].crypto_infos()
        for symbol in symbols:
            text = self.controller.get_portfolio(symbol)
            text2 = self.controller.get_portfolio2(symbol)
            self.text_list[symbol] = text,text2


    


if __name__ == "__main__":
    app = BudgetApp()
    app.mainloop()
    






