import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
from datetime import datetime, timedelta

# --------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Indian Cities Air Quality Dashboard",
    page_icon="🌏",
    layout="wide"
)

# --------- API & STYLE ----------
API_KEY = '14e4f43b89530801a91760fda72315ae'  
sns.set_theme(style="whitegrid", context="talk")

AQI_CATEGORIES = {
    1: ("Good", "#009966"),
    2: ("Fair", "#FFDE33"),
    3: ("Moderate", "#FF9933"),
    4: ("Poor", "#CC0033"),
    5: ("Very Poor", "#660099"),
}

# --------- LOAD CITY DATA ----------
@st.cache_data
def load_city_data():
    return pd.read_csv("cities.csv")  # CSV with columns: city, lat, lon

city_df = load_city_data()

# --------- HEADER ----------
st.markdown("<h1 style='text-align:center; color:#2E86C1;'>🌏 Indian Cities Air Quality Dashboard</h1>", unsafe_allow_html=True)
st.write("Get **real-time air quality data** and **past 7 days AQI trends** for major Indian cities.")

# --------- SIDEBAR ----------
st.sidebar.header("📍 Select a City")
city_name = st.sidebar.selectbox("Choose city", city_df['city'].sort_values().unique())
selected_city = city_df[city_df['city'] == city_name].iloc[0]
lat, lon = selected_city['lat'], selected_city['lon']

# --------- REAL-TIME DATA ----------
url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
response = requests.get(url)
data = response.json()

if 'list' not in data or len(data['list']) == 0:
    st.error("⚠️ No air pollution data found for this city.")
else:
    info = data['list'][0]
    aqi = info['main']['aqi']
    components = info['components']
    category, color = AQI_CATEGORIES.get(aqi, ("Unknown", "#000000"))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"<h2 style='color:{color};'>{category}</h2>", unsafe_allow_html=True)
        st.metric(label="AQI Value", value=aqi)

    with col2:
        df = pd.DataFrame(list(components.items()), columns=['Pollutant', 'Concentration'])
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x='Pollutant', y='Concentration', data=df, palette="coolwarm", ax=ax)
        ax.set_title(f'Pollutant Concentrations in {city_name}')
        ax.set_ylabel('µg/m³')
        ax.set_xlabel('')
        st.pyplot(fig)

# --------- PAST 7 DAYS HISTORY ----------
end_time = int(time.time())  
start_time = int((datetime.now() - timedelta(days=7)).timestamp())  

history_url = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start_time}&end={end_time}&appid={API_KEY}"
history_response = requests.get(history_url)
history_data = history_response.json()

if 'list' in history_data and len(history_data['list']) > 0:
    history_list = history_data['list']
    dates = [datetime.fromtimestamp(item['dt']) for item in history_list]
    aqi_values = [item['main']['aqi'] for item in history_list]
    categories = [AQI_CATEGORIES.get(a, ("Unknown", "#000000"))[0] for a in aqi_values]
    colors = [AQI_CATEGORIES.get(a, ("Unknown", "#000000"))[1] for a in aqi_values]

    hist_df = pd.DataFrame({'Date': dates, 'AQI': aqi_values, 'Category': categories, 'Color': colors})

    fig2, ax2 = plt.subplots(figsize=(12, 6))
    for i in range(len(hist_df)):
        ax2.plot(hist_df['Date'][i], hist_df['AQI'][i], 'o', color=hist_df['Color'][i], markersize=10)
    ax2.plot(hist_df['Date'], hist_df['AQI'], color="gray", alpha=0.5)
    ax2.set_title(f"AQI Trend (Past 7 Days) - {city_name}")
    ax2.set_ylabel('AQI Level')
    ax2.set_xlabel('Date')
    st.pyplot(fig2)

else:
    st.warning("⚠️ No historical AQI data available for this city.")

# --------- FOOTER ----------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>© 2025 Air Quality Dashboard | Powered by OpenWeather API</p>", unsafe_allow_html=True)
