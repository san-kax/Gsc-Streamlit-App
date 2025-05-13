
# gsc_streamlit_app.py

import streamlit as st
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import datetime
import os
import json

st.set_page_config(page_title="GSC Data Explorer", layout="wide")
st.title("🔍 Google Search Console Data Explorer")

# Function to authenticate user
def authenticate():
    # Build secrets-based client config
    client_secrets = {
        "installed": {
            "client_id": st.secrets["google"]["client_id"],
            "client_secret": st.secrets["google"]["client_secret"],
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }

    with open("client_secrets.json", "w") as f:
        json.dump(client_secrets, f)

    flow = Flow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['https://www.googleapis.com/auth/webmasters.readonly'],
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )
    auth_url, _ = flow.authorization_url(prompt='consent')

    st.write("### Step 1: Authorize the app")
    st.markdown(f"[Click here to authorize]({auth_url})")
    code = st.text_input("Step 2: Paste the authorization code here")

    if code:
        try:
            flow.fetch_token(code=code)
            credentials = flow.credentials
            st.success("✅ Authentication successful")
            return credentials
        except Exception as e:
            st.error(f"❌ Authentication failed: {e}")
    return None

# Function to get list of verified sites
def get_sites(service):
    site_list = service.sites().list().execute()
    return [s['siteUrl'] for s in site_list.get('siteEntry', []) if s['permissionLevel'] == 'siteFullUser']

# Function to query GSC data
def get_gsc_data(service, site_url, start_date, end_date, dimensions, row_limit=25000):
    body = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': dimensions,
        'rowLimit': row_limit
    }
    response = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    return response.get('rows', [])

# Main execution
credentials = authenticate()

if credentials:
    service = build('searchconsole', 'v1', credentials=credentials)

    sites = get_sites(service)
    site = st.selectbox("Select a site", sites)

    default_start = datetime.date.today() - datetime.timedelta(days=30)
    default_end = datetime.date.today()
    
    start_date = st.date_input("Start date", default_start)
    end_date = st.date_input("End date", default_end)

    dimensions = st.multiselect("Choose dimensions", ['query', 'page', 'country', 'device', 'date'], default=['query'])

    if st.button("Fetch GSC Data"):
        rows = get_gsc_data(service, site, str(start_date), str(end_date), dimensions)

        if not rows:
            st.warning("No data found for the selected parameters.")
        else:
            df = pd.DataFrame(rows)
            if 'keys' in df.columns:
                df[dimensions] = pd.DataFrame(df['keys'].tolist(), index=df.index)
                df.drop(columns=['keys'], inplace=True)
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name="gsc_data.csv", mime="text/csv")
