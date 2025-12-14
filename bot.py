"""
AI Trading Bot with Martingale Strategy

A desktop trading application that implements a Martingale-style Dollar Cost Averaging (DCA)
strategy for equity trading. Features integration with Alpaca Markets API for live trading
and OpenAI for intelligent portfolio analysis.

Author: Your Name
Date: December 2025
License: MIT
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
import threading
import os
import alpaca_trade_api as tradeapi
import openai

# Try to import from config.py, fallback to environment variables
try:
    from config import (
        ALPACA_API_KEY,
        ALPACA_SECRET_KEY,
        ALPACA_BASE_URL,
        OPENAI_API_KEY,
        DATA_FILE
    )
except ImportError:
    # Fallback to environment variables
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', '')
    ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets/')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    DATA_FILE = 'equities.json'
    
    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        print("⚠️ WARNING: API keys not found!")
        print("Please create config.py or set environment variables.")

# Initialize Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version="v2")


def fetch_portfolio():
    """
    Fetch current portfolio positions from Alpaca.
    
    Returns:
        list: List of dictionaries containing position data for each holding
    """
    positions = api.list_positions()
    portfolio = []
    for pos in positions:
        portfolio.append({
            'symbol': pos.symbol,
            'qty': pos.qty,
            'entry_price': pos.avg_entry_price,
            'current_price': pos.current_price,
            'unrealized_pl': pos.unrealized_pl,
            'side': 'buy'
        })
    return portfolio


def fetch_open_orders():
    """
    Fetch all open orders from Alpaca.
    
    Returns:
        list: List of dictionaries containing open order details
    """
    orders = api.list_orders(status='open')
    open_orders = []
    for order in orders:
        open_orders.append({
            'symbol': order.symbol,
            'qty': order.qty,
            'limit_price': order.limit_price,
            'side': 'buy'
        })
    return open_orders


def llm_response(message):
    """
    Generate AI-powered portfolio analysis using OpenAI.
    
    Args:
        message (str): User's question or request for portfolio analysis
        
    Returns:
        str: AI-generated response with portfolio insights
    """
    portfolio_data = fetch_portfolio()
    open_orders = fetch_open_orders()
    
    pre_prompt = f"""
    You are an AI portfolio manager responsible for analyzing my portfolio.
    Your tasks are the following:
    1.) Evaluate risk exposures of my current holdings
    2.) Analyze my open limit orders and their potential impact
    3.) Provide insights into portfolio health, diversification, trade adjustments, etc.
    4.) Speculate on the market outlook based on current market conditions
    5.) Identify potential market risks and suggest risk management strategies

    Here is my portfolio: {portfolio_data}

    Here are my open orders: {open_orders}

    Overall, answer the following question with priority having that background: {message}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": pre_prompt}],
            api_key=OPENAI_API_KEY
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"


def fetch_mock_api(symbol):
    """
    Mock API function for testing purposes.
    
    Args:
        symbol (str): Stock ticker symbol
        
    Returns:
        dict: Dictionary with mock price data
    """
    return {"price": 100}


class TradingBotGUI:
    """
    Main GUI class for the AI Trading Bot.
    
    Implements a Martingale-style DCA strategy with automated order placement,
    portfolio tracking, and AI-powered chat assistant.
    """
    
    def __init__(self, root):
        """
        Initialize the trading bot GUI.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("AI Trading Bot")
        self.equities = self.load_equities()
        self.system_running = False

        # Input form frame
        self.form_frame = tk.Frame(root)
        self.form_frame.pack(pady=10)

        # Symbol input
        tk.Label(self.form_frame, text='Symbol:').grid(row=0, column=0)
        self.symbol_entry = tk.Entry(self.form_frame)
        self.symbol_entry.grid(row=0, column=1)
        
        # Levels input
        tk.Label(self.form_frame, text='Levels:').grid(row=0, column=2)
        self.levels_entry = tk.Entry(self.form_frame)
        self.levels_entry.grid(row=0, column=3)
        
        # Drawdown input
        tk.Label(self.form_frame, text='Drawdown%:').grid(row=0, column=4)
        self.drawdown_entry = tk.Entry(self.form_frame)
        self.drawdown_entry.grid(row=0, column=5)

        self.add_button = tk.Button(
            self.form_frame, 
            text='Add Equity', 
            command=self.add_equity
        )
        self.add_button.grid(row=0, column=6)

        # Treeview table for displaying equities
        self.tree = ttk.Treeview(
            root, 
            columns=('Symbol', 'Position', 'Entry Price', 'Levels', 'Status'), 
            show='headings'
        )
        for col in ['Symbol', 'Position', 'Entry Price', 'Levels', 'Status']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(pady=10)

        # Control buttons
        self.toggle_system_button = tk.Button(
            root, 
            text='Toggle Selected System', 
            command=self.toggle_selected_system
        )
        self.toggle_system_button.pack(pady=5)
        
        self.remove_button = tk.Button(
            root, 
            text='Remove Selected Equity', 
            command=self.remove_selected_equity
        )
        self.remove_button.pack(pady=5)

        # AI chat component
        self.chat_frame = tk.Frame(root)
        self.chat_frame.pack(pady=10)

        self.chat_input = tk.Entry(self.chat_frame, width=50)
        self.chat_input.grid(row=0, column=0, padx=5)

        self.send_button = tk.Button(
            self.chat_frame, 
            text='Send', 
            command=self.send_message
        )
        self.send_button.grid(row=0, column=1)

        self.chat_output = tk.Text(root, height=5, width=60, state=tk.DISABLED)
        self.chat_output.pack()

        # Load saved data and start auto-update thread
        self.refresh_table()

        self.running = True
        self.auto_update_thread = threading.Thread(target=self.auto_update, daemon=True)
        self.auto_update_thread.start()

    def add_equity(self):
        """
        Add a new equity to track with specified levels and drawdown percentage.
        Calculates Martingale-style DCA price levels automatically.
        """
        symbol = self.symbol_entry.get().upper()
        levels = self.levels_entry.get()
        drawdown = self.drawdown_entry.get()

        # Validate inputs
        if not symbol or not levels.isdigit() or not drawdown.replace('.', '', 1).isdigit():
            messagebox.showerror("Error", "Invalid input.")
            return
        
        levels = int(levels)
        drawdown = float(drawdown) / 100
        entry_price = fetch_mock_api(symbol)['price']

        # Calculate Martingale-style DCA levels
        level_prices = {
            i+1: round(entry_price * (1 - drawdown * (i+1)), 2) 
            for i in range(levels)
        }

        self.equities[symbol] = {
            "position": 0,
            "entry_price": entry_price,
            "levels": level_prices,
            "drawdown": drawdown,
            "status": "Off"
        }
        
        self.save_equities()
        self.refresh_table()
        
        # Clear input fields
        self.symbol_entry.delete(0, tk.END)
        self.levels_entry.delete(0, tk.END)
        self.drawdown_entry.delete(0, tk.END)
    
    def toggle_selected_system(self):
        """
        Toggle trading system ON/OFF for selected equity in the table.
        When ON, the bot will actively monitor and place orders.
        """
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No equity selected.")
            return
        
        for item in selected_items:
            symbol = self.tree.item(item)['values'][0]
            current_status = self.equities[symbol]['status']
            self.equities[symbol]['status'] = 'On' if current_status == 'Off' else 'Off'

        self.save_equities()
        self.refresh_table()

    def remove_selected_equity(self):
        """
        Remove selected equity from tracking.
        """
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No equity selected.")
            return
        
        for item in selected_items:
            symbol = self.tree.item(item)['values'][0]
            del self.equities[symbol]

        self.save_equities()
        self.refresh_table()

    def send_message(self):
        """
        Send message to AI assistant and display response in chat window.
        """
        message = self.chat_input.get()
        if not message:
            return
        
        try:
            response = llm_response(message)
            self.chat_output.config(state=tk.NORMAL)
            self.chat_output.insert(tk.END, f"You: {message}\\n{response}\\n\\n")
            self.chat_output.config(state=tk.DISABLED)
            self.chat_input.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("AI Error", f"Error communicating with AI: {e}")
    
    def fetch_alpaca_data(self, symbol):
        """
        Fetch real-time price data from Alpaca API.
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: Dictionary with current price, or -1 if error
        """
        try:
            barset = api.get_latest_trade(symbol)
            return {"price": barset.price}
        except Exception as e:
            return {"price": -1}

    def check_existing_orders(self, symbol, price):
        """
        Check if an order already exists at a specific price for a symbol.
        
        Args:
            symbol (str): Stock ticker symbol
            price (float): Limit price to check
            
        Returns:
            bool: True if order exists, False otherwise
        """
        try:
            orders = api.list_orders(status='open', symbols=symbol)
            for order in orders:
                if float(order.limit_price) == price:
                    return True
        except Exception as e:
            messagebox.showerror("API Error", f"Error checking orders: {e}")
        return False

    def get_max_entry_price(self, symbol):
        """
        Get the highest filled order price for a symbol (most recent entry).
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            float: Maximum filled price, or -1 if no filled orders found
        """
        try:
            orders = api.list_orders(status="filled", limit=50)
            prices = [
                float(order.filled_avg_price) 
                for order in orders 
                if order.filled_avg_price and order.symbol == symbol
            ]
            return max(prices) if prices else -1
        except Exception as e:
            messagebox.showerror("API Error", f"Error fetching orders: {e}")
            return 0

    def trade_systems(self):
        """
        Main trading logic loop. Monitors active systems and places orders
        according to Martingale DCA strategy.
        """
        for symbol, data in self.equities.items():
            if data['status'] == 'On':
                position_exists = False
                
                try:
                    # Check if position exists
                    position = api.get_position(symbol)
                    entry_price = self.get_max_entry_price(symbol)
                    position_exists = True
                except Exception as e:
                    # No position exists, place initial market order
                    api.submit_order(
                        symbol=symbol,
                        qty=1,
                        side='buy',
                        type='market',
                        time_in_force='gtc'
                    )
                    messagebox.showinfo("Order placed", f"Initial order placed for {symbol}")
                    time.sleep(2)
                    entry_price = self.get_max_entry_price(symbol)
                
                print(entry_price)
                
                # Recalculate level prices based on actual entry
                level_prices = {
                    i+1: round(entry_price * (1 - data['drawdown'] * (i+1)), 2) 
                    for i in range(len(data['levels']))
                }
                
                # Update levels
                existing_levels = self.equities.get(symbol, {}).get('levels', {})
                for level, price in level_prices.items():
                    if level not in existing_levels and -level not in existing_levels:
                        existing_levels[level] = price
                
                # Update equity data
                self.equities[symbol]['entry_price'] = entry_price
                self.equities[symbol]['levels'] = existing_levels
                self.equities[symbol]['position'] = 1

                # Place limit orders for each level
                for level, price in level_prices.items():
                    if level in self.equities[symbol]['levels']:
                        self.place_order(symbol, price, level)
                
                self.save_equities()
                self.refresh_table()
            else:
                return
    
    def place_order(self, symbol, price, level):
        """
        Place a limit order for a specific level.
        
        Args:
            symbol (str): Stock ticker symbol
            price (float): Limit price for the order
            level (int): DCA level number
        """
        # Check if order already placed for this level
        if -level in self.equities[symbol]['levels'] or '-1' in self.equities[symbol]['levels'].keys():
            return
        
        try:
            api.submit_order(
                symbol=symbol,
                qty=1,
                side='buy',
                type='limit',
                time_in_force='gtc',
                limit_price=price
            )
            # Mark level as order placed (negative indicates placed)
            self.equities[symbol]['levels'][-level] = price
            del self.equities[symbol]['levels'][level]
            print(f"Placed Order for {symbol}@{price}")
        except Exception as e:
            messagebox.showerror("Order Error", f"Error placing order: {e}")

    def refresh_table(self):
        """
        Refresh the treeview table with current equity data.
        """
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert updated data
        for symbol, data in self.equities.items():
            self.tree.insert('', 'end', values=(
                symbol,
                data['position'],
                data['entry_price'],
                str(data['levels']),
                data['status']
            ))

    def auto_update(self):
        """
        Background thread that continuously monitors and executes trades.
        Runs every 5 seconds while the application is running.
        """
        while self.running:
            time.sleep(5)
            self.trade_systems()
    
    def save_equities(self):
        """
        Save equity data to JSON file for persistence.
        """
        with open(DATA_FILE, 'w') as f:
            json.dump(self.equities, f, indent=2)
    
    def load_equities(self):
        """
        Load equity data from JSON file.
        
        Returns:
            dict: Dictionary of equity data, or empty dict if file doesn't exist
        """
        try:    
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def on_close(self):
        """
        Handle application closure. Stops background threads and saves data.
        """
        self.running = False
        self.save_equities()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
