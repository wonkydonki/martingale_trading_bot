# AI Trading Bot with Martingale Strategy

An intelligent trading bot built with Python and Tkinter that implements a Martingale-style Dollar Cost Averaging (DCA) strategy for equity trading through the Alpaca API. Features an integrated AI assistant powered by OpenAI for portfolio analysis and insights.

## Features

- **GUI-Based Trading Interface**: User-friendly desktop application built with Tkinter
- **Martingale DCA Strategy**: Automated buying at predetermined drawdown levels
- **Real-Time Portfolio Tracking**: Monitor positions, entry prices, and order status
- **AI Portfolio Assistant**: Chat with an AI assistant for portfolio analysis and market insights
- **Alpaca Integration**: Live paper trading through Alpaca Markets API
- **Auto-Refresh System**: Background thread continuously monitors and executes trades
- **Persistent Data Storage**: Save and load equity configurations via JSON

## Prerequisites

- Python 3.7 or higher
- Alpaca Paper Trading Account ([Sign up here](https://alpaca.markets/))
- OpenAI API Key ([Get one here](https://platform.openai.com/))

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/martingale_trading_bot.git
   cd martingale_trading_bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API credentials**
   
   Copy the example config file:
   ```bash
   cp config.example.py config.py
   ```
   
   Edit `config.py` and add your API keys:
   ```python
   # Alpaca API
   ALPACA_API_KEY = "your_alpaca_key_here"
   ALPACA_SECRET_KEY = "your_alpaca_secret_here"
   ALPACA_BASE_URL = "https://paper-api.alpaca.markets/"
   
   # OpenAI API
   OPENAI_API_KEY = "your_openai_key_here"
   ```

## Usage

1. **Run the application**
   ```bash
   python bot.py
   ```

2. **Add an equity to track**
   - Enter the stock symbol (e.g., AAPL)
   - Set the number of levels (how many buy orders to place)
   - Set the drawdown percentage (price drop between levels)
   - Click "Add Equity"

3. **Activate trading**
   - Select an equity from the table
   - Click "Toggle Selected System" to turn trading ON
   - The bot will automatically place and manage orders

4. **Chat with AI assistant**
   - Type questions about your portfolio in the chat box
   - Get insights on risk exposure, diversification, and market outlook

## How the Martingale Strategy Works

1. **Initial Entry**: Bot places a market order when you activate an equity
2. **Level Calculation**: Calculates buy prices at specified drawdown intervals
3. **Limit Orders**: Places limit orders at each calculated level
4. **Auto-Execution**: When price drops to a level, order executes automatically
5. **Position Tracking**: Updates your position and recalculates levels

**Example**: 
- Stock: AAPL at $100
- Levels: 5
- Drawdown: 5%
- Orders placed at: $95, $90, $85, $80, $75

## Project Structure

```
martingale_trading_bot/
├── bot.py                  # Main application file
├── config.py               # API configuration (create from example)
├── equities.json           # Persistent storage for tracked equities
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── alpaca.ipynb           # Jupyter notebook for Alpaca API testing
└── openai.ipynb           # Jupyter notebook for OpenAI integration testing
```

## Configuration Options

### Equity Parameters
- **Symbol**: Stock ticker (e.g., TSLA, MSFT, AAPL)
- **Levels**: Number of buy orders (1-10 recommended)
- **Drawdown%**: Percentage drop between levels (1-20% typical)

### System Behavior
- **Auto-Update Interval**: 5 seconds (configurable in code)
- **Order Type**: Limit orders for DCA levels
- **Time in Force**: GTC (Good Till Canceled)

## Security Warnings

**NEVER commit your `config.py` file with real API keys to GitHub!**

- API keys are in `.gitignore` by default
- Use environment variables for production
- Rotate keys if accidentally exposed

## Testing with Notebooks

Two Jupyter notebooks are included for testing, but not visible as per .gitignore:

- **alpaca.ipynb**: Test Alpaca API connections and order placement
- **openai.ipynb**: Test OpenAI integration and prompt engineering

