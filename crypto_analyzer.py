import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from datetime import datetime, timedelta

class CryptoAnalyzer:
    def __init__(self, symbol, start_date=None, end_date=None):
        self.symbol = symbol
        self.start_date = start_date or (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        self.data = None
        self.load_data()

    def load_data(self):
        """Load historical data from Yahoo Finance"""
        ticker = yf.Ticker(f"{self.symbol}-USD")
        self.data = ticker.history(start=self.start_date, end=self.end_date)
        if self.data.empty:
            raise ValueError(f"No data found for {self.symbol}")

    def add_indicators(self):
        """Calculate technical indicators"""
        # SMA
        sma_20 = SMAIndicator(close=self.data['Close'], window=20)
        self.data['SMA20'] = sma_20.sma_indicator()
        
        sma_50 = SMAIndicator(close=self.data['Close'], window=50)
        self.data['SMA50'] = sma_50.sma_indicator()

        # EMA
        ema_20 = EMAIndicator(close=self.data['Close'], window=20)
        self.data['EMA20'] = ema_20.ema_indicator()

        # RSI
        rsi = RSIIndicator(close=self.data['Close'])
        self.data['RSI'] = rsi.rsi()

        # Bollinger Bands
        bb = BollingerBands(close=self.data['Close'])
        self.data['BB_upper'] = bb.bollinger_hband()
        self.data['BB_lower'] = bb.bollinger_lband()
        self.data['BB_middle'] = bb.bollinger_mavg()

    def identify_patterns(self):
        """Identify basic trading patterns"""
        # Golden Cross (SMA20 crosses above SMA50)
        self.data['Golden_Cross'] = (self.data['SMA20'] > self.data['SMA50']) & (self.data['SMA20'].shift(1) <= self.data['SMA50'].shift(1))
        
        # Death Cross (SMA20 crosses below SMA50)
        self.data['Death_Cross'] = (self.data['SMA20'] < self.data['SMA50']) & (self.data['SMA20'].shift(1) >= self.data['SMA50'].shift(1))
        
        # Oversold (RSI < 30)
        self.data['Oversold'] = self.data['RSI'] < 30
        
        # Overbought (RSI > 70)
        self.data['Overbought'] = self.data['RSI'] > 70

    def plot_analysis(self):
        """Create an interactive plot with all indicators"""
        fig = go.Figure()

        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=self.data.index,
            open=self.data['Open'],
            high=self.data['High'],
            low=self.data['Low'],
            close=self.data['Close'],
            name='Price'
        ))

        # Add moving averages
        fig.add_trace(go.Scatter(x=self.data.index, y=self.data['SMA20'], name='SMA20', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=self.data.index, y=self.data['SMA50'], name='SMA50', line=dict(color='blue')))
        
        # Add Bollinger Bands
        fig.add_trace(go.Scatter(x=self.data.index, y=self.data['BB_upper'], name='BB Upper', line=dict(color='gray', dash='dash')))
        fig.add_trace(go.Scatter(x=self.data.index, y=self.data['BB_lower'], name='BB Lower', line=dict(color='gray', dash='dash')))

        # Mark patterns
        golden_cross_points = self.data[self.data['Golden_Cross']].index
        death_cross_points = self.data[self.data['Death_Cross']].index

        for point in golden_cross_points:
            fig.add_annotation(
                x=point,
                y=self.data.loc[point, 'Low'],
                text="Golden Cross",
                showarrow=True,
                arrowhead=1,
                arrowcolor="green"
            )

        for point in death_cross_points:
            fig.add_annotation(
                x=point,
                y=self.data.loc[point, 'High'],
                text="Death Cross",
                showarrow=True,
                arrowhead=1,
                arrowcolor="red"
            )

        fig.update_layout(
            title=f'{self.symbol} Technical Analysis',
            yaxis_title='Price',
            xaxis_title='Date',
            template='plotly_dark'
        )

        fig.show()

    def generate_report(self):
        """Generate a summary report of the analysis"""
        report = {
            'Symbol': self.symbol,
            'Period': f"{self.start_date} to {self.end_date}",
            'Current Price': self.data['Close'][-1],
            'Price Change (%)': ((self.data['Close'][-1] - self.data['Close'][0]) / self.data['Close'][0]) * 100,
            'RSI': self.data['RSI'][-1],
            'Golden Crosses': len(self.data[self.data['Golden_Cross']]),
            'Death Crosses': len(self.data[self.data['Death_Cross']]),
            'Times Oversold': len(self.data[self.data['Oversold']]),
            'Times Overbought': len(self.data[self.data['Overbought']])
        }
        return report

def main():
    # Example usage
    analyzer = CryptoAnalyzer('BTC')  # Bitcoin analysis for the past year
    analyzer.add_indicators()
    analyzer.identify_patterns()
    
    # Generate and print report
    report = analyzer.generate_report()
    print("\nAnalysis Report:")
    for key, value in report.items():
        print(f"{key}: {value}")
    
    # Plot the analysis
    analyzer.plot_analysis()

if __name__ == "__main__":
    main()
