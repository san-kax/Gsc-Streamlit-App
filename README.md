# 📊 Google Search Console Streamlit App

A Streamlit web app to explore and export your Google Search Console (GSC) data beyond the 1,000-row export limit of the GSC UI.

## 🚀 Features

- OAuth 2.0 authentication with Google
- Select from your verified GSC properties
- Choose dimensions like `query`, `page`, `country`, `device`, `date`
- Specify a custom date range
- Fetch and display up to 25,000 rows of data
- Download the results as CSV

## 📦 Requirements

- Python 3.7+
- Google Cloud project with OAuth credentials
- `client_secrets.json` or use Streamlit secrets

## 🛠 Setup

1. Clone this repo and install dependencies:

```bash
pip install -r requirements.txt
