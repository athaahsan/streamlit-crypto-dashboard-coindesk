# Crypto Dashboard

This project is a cryptocurrency dashboard that visualizes real-time market data, technical indicators, and sentiment analysis using public APIs.  
It combines market visualization with an AI-powered technical insight system to provide structured analysis based on quantitative signals.

---

## Features

### 📊 Live Price Data
Displays cryptocurrency prices using the [Binance Public API](https://binance-docs.github.io/apidocs/spot/en/).

### 📈 Chart Visualization
- Candlestick, Line, and OHLC chart types
- Toggleable indicators available in the interface:
  - Volume (VOL)
  - Moving Average (MA)
  - Exponential Moving Average (EMA)
- Configurable chart range and interval selection

### 😱 Market Sentiment
Integrates the [Fear and Greed Index API](https://api.alternative.me/fng) to provide an overview of current crypto market sentiment.

### ✨ AI Insights (Daily Interval Only)
An AI-powered technical analysis module generates structured trading bias based on internally engineered indicators.

These indicators are **not displayed on the chart**, but are calculated in the background as part of the AI payload:

- RSI(14) momentum signals
- MACD(12-26-9) histogram trend
- ADX(14) trend strength
- Directional Index (+DI / −DI) dominance
- EMA alignment and price distance
- Fear & Greed sentiment data

The AI produces probabilistic signals:
- `buy_confidence`
- `hold_confidence`
- `sell_confidence`

Analysis is strictly based on provided technical data without external market assumptions.

---

## APIs Used

- **Binance Public API**  
  Real-time ticker and historical pricing data.

- **Alternative.me Fear & Greed Index API**  
  Market sentiment index derived from multiple sources.

- **OpenRouter AI API**  
  Structured LLM analysis for technical insight generation.

---

## Live Demo

This project is hosted using Streamlit and can be accessed here:  
👉 **https://atha-crypto-dashboard.streamlit.app/**

---

## Notes

- The AI analysis does **not** provide financial advice.
- All decisions are generated purely from provided technical indicators.
- Designed for educational, analytical, and experimental purposes.
