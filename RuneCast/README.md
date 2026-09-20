# RuneCast

**Deep Learning for Complex RuneScape Item Price Prediction**

---

## Overview

RuneCast is an advanced machine learning project that predicts the prices of complex, craftable items in the RuneScape Grand Exchange. Unlike straightforward price trackers, RuneCast models the layered dependencies between crafted goods and their precursor materials using multivariate time series forecasting.

By combining real-time web scraping, deep neural networks (LSTM), and automated hyperparameter optimization, RuneCast provides accurate and interpretable forecasts to help players, traders, and developers better understand and anticipate in-game market trends.

---

## Motivation

The RuneScape economy is intricate and volatile. Many valuable items require multiple precursor components, each with their own price fluctuations influenced by player demand, supply chain changes, and game updates. Traditional forecasting approaches treating each item independently often fail to capture these dependencies.

RuneCast tackles this challenge by:

- Modeling precursor relationships explicitly through a configurable "depth" system  
- Leveraging sequential models that handle multivariate input time series  
- Integrating automated data collection with model training and evaluation  

The result is a robust forecasting pipeline capable of providing insights on composite item prices that reflect their underlying market dynamics.

---

## Features

- **Multivariate LSTM Model:** Predict prices using multiple precursor item price histories simultaneously  
- **Dynamic Precursor Depth:** Configure how many tiers of precursor items are included in the model input  
- **Automated Data Collection:** Scrape and cache historical price data from RuneScape APIs and third-party sources  
- **Hyperparameter Optimization:** Use Optuna to tune model architecture and training parameters for best performance  
- **Modular Design:** Clean, extensible codebase for data processing, modeling, prediction, and optimization  
- **Command-Line Interface:** Easy-to-use scripts for training, predicting, and optimizing without complex setup  

---

## Tech Stack

| Component        | Technology         |
|------------------|--------------------|
| Programming      | Python 3.10+       |
| ML Framework     | PyTorch            |
| Data Handling    | Pandas, NumPy      |
| Hyperparameter Tuning | Optuna         |
| Web Scraping     | Requests, BeautifulSoup |
| Visualization    | Matplotlib, Seaborn|

---

## Project Structure

runecast/
│
├── data/ # Raw and processed price data CSVs
├── models/ # Trained model weights and scalers
│
├── train.py # Training pipeline script
├── predict.py # Model loading and inference script
├── optimise.py # Hyperparameter tuning pipeline
├── price_scraper.py # Price history fetching and caching
├── data_utils.py # Data loading and preprocessing utilities
├── requirements.txt # Python dependencies
└── README.md # Project documentation


---

## Getting Started

### Prerequisites

- Python 3.10 or higher  
- PyTorch  
- Required Python packages (see `requirements.txt`)

### Installation

Clone the repository:

```bash
git clone https://github.com/raefr-io/runecast.git
cd runecast
pip install -r requirements.txt
```
#### Usage: 

Download price history for items at desired precursor depth:
```
python price_scraper.py
```

Train a price prediction model:
```
python train.py
```
Run price prediction using a saved model:
```
python predict.py
```
Tune hyperparameters using Optuna:
```
python optimize.py
```

## How It Works

### Data Collection:
Historical price data is scraped and cached from RuneScape Grand Exchange APIs or third-party sources.

### Preprocessing:
Data is cleaned and formatted into multivariate time series based on configured precursor depth.

### Model Training:
A configurable LSTM model is trained on sequences of precursor prices to predict target item prices.

### Prediction:
The trained model is loaded to generate short-term price forecasts based on live scraped data.

### Optimisation:
Optuna automates tuning of model hyperparameters to improve forecasting accuracy.


## Results & Evaluation

Models are evaluated against a univariate baseline (LSTM trained on target item price only) using RMSE and MAE on a held-out 20% test set. Results below are for the Glorious bar target item across precursor depth configurations.

| Model | Depth | Input Features | RMSE | MAE | vs. Baseline |
|---|---|---|---|---|---|
| Univariate baseline | 1 | 1 | — | — | — |
| Multivariate LSTM | 2 | 4 | — | — | — |
| Multivariate LSTM | 3 | 14 | — | — | — |
| Multivariate LSTM | 4 | 27 | — | — | — |
| Multivariate LSTM | 5 | 40 | — | — | — |

> **Note:** Evaluation figures to be populated after full training run. The depth system hypothesis is that deeper precursor inclusion improves accuracy for items with tightly coupled supply chains, with diminishing returns beyond depth 3 as lower-tier ore prices are more weakly correlated with finished bar prices.

## Future Improvements

    Implement Transformer-based models for enhanced temporal context

    Automate live prediction dashboards with real-time data ingestion

    Extend support for additional item categories and dynamic precursor sets

    Build a web API for community access and integration with RuneScape tools

    Explore arbitrage and flipping opportunity detection models



Inspired by real-world commodity price modeling and my MSc dissertation work revisited with modern deep learning techniques.




