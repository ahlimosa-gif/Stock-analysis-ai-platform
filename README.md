# Stock Analysis AI Platform

Stock Analysis AI Platform is a multipage Streamlit app for technical stock charting, next-day forecast experiments, and historical backtest validation. Streamlit supports multipage apps through a main script plus a `pages/` directory, and Community Cloud deployment expects a valid main file path together with organized dependencies.[cite:102][cite:269][cite:275]

## Features

- Interactive stock overview with line or candlestick chart.
- Moving averages, RSI, support/resistance, and breakout markers.
- Volume-confirmed first-breakout logic.
- Next-day forecast page with bullish / neutral / bearish probabilities.
- Backtest page with directional accuracy, range-hit rate, confusion matrix, and per-class precision / recall / F1.
- Baseline comparisons such as majority class, always bullish, and neutral benchmark.

## Project structure

```text
stock-analysis-ai-platform/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── pages/
│   ├── 1_Overview.py
│   ├── 3_Next_Day_Forecast.py
│   └── 4_Backtest_Accuracy.py
└── src/
    ├── backtest.py
    ├── charts.py
    ├── forecast.py
    ├── indicators.py
    ├── signals.py
    └── data_loader.py
```

A good README should explain what the project does, how to install it, how to run it, and how the repository is organized so that someone new can get started quickly.[cite:273][cite:276][cite:280]

## Requirements

- Python 3.10+
- Git
- Internet connection for package installation and market data download

For Python projects, it is standard to install in an isolated virtual environment and keep temporary or machine-specific files out of version control with `.gitignore`.[cite:271][cite:277]

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPO_URL>
cd stock-analysis-ai-platform
```

### 2. Create a virtual environment

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

A Python `.gitignore` typically excludes virtual environments, `__pycache__`, and compiled files because these are local artifacts rather than source code.[cite:271][cite:274]

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

Streamlit apps are launched with `streamlit run <main-file>`, and for multipage apps the main file sits alongside the `pages/` directory.[cite:102][cite:269]

### 5. Open the local URL

After startup, Streamlit will show a local address in your terminal, usually:

```text
http://localhost:8501
```

## Fallback install

If you need a direct install without `requirements.txt`, install the core packages manually:

```bash
pip install streamlit yfinance pandas plotly numpy
```

## Usage

### Overview page

Use this page to inspect recent price action, moving averages, RSI, support/resistance, and breakout signals.

### Next-Day Forecast page

Use this page to view the model's next-session directional bias, projected close, and scenario range.

### Backtest / Accuracy page

Use this page to validate forecast behavior on historical data with rolling one-step-ahead evaluation, benchmark baselines, confusion matrix, and class-level metrics.

## GitHub push steps

After confirming the app runs locally, create a repository on GitHub and push the code:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

GitHub's repository quickstart and repository-creation guides describe this general flow for creating a repository and pushing the first commit.[cite:268][cite:270]

## Streamlit deployment

To deploy on Streamlit Community Cloud:

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Select your repository and branch.
4. Set the main file path to `app.py`.
5. Deploy.

Community Cloud deployment depends on correct file organization, dependency declaration, and a valid main file path.[cite:257][cite:269][cite:275]

## Troubleshooting

- If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

- If `python3` is unavailable, try `python`.
- If deployment cannot find the app, verify that `app.py` is in the repository root and `pages/` is beside it, not nested incorrectly.[cite:272][cite:282]

## Disclaimer

This project is for educational and research purposes only. It does not provide financial advice, trading advice, or guaranteed predictions.
