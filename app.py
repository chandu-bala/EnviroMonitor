import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
from geopy.geocoders import Nominatim
import time

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="India AQI Dashboard", layout="wide")

# -----------------------------
# Load Dataset with Lat/Lon
# -----------------------------
@st.cache_data
def load_data_with_coords():
    try:
        # If preprocessed dataset exists, load it
        df = pd.read_csv("AQI_Clean_Data_with_coords.csv")
    except FileNotFoundError:
        # Fallback: add coordinates on the fly
        df = pd.read_csv("notebooks/AQI_Clean_Data.csv")
        geolocator = Nominatim(user_agent="aqi_app")

        latitudes, longitudes = [], []
        for state in df["State"]:
            try:
                location = geolocator.geocode(state + ", India")
                if location:
                    latitudes.append(location.latitude)
                    longitudes.append(location.longitude)
                else:
                    latitudes.append(None)
                    longitudes.append(None)
            except:
                latitudes.append(None)
                longitudes.append(None)
            time.sleep(1)  # avoid hitting API rate limits

        df["Latitude"] = latitudes
        df["Longitude"] = longitudes
        df.to_csv("AQI_Clean_Data_with_coords.csv", index=False)  # save for future

    return df

df = load_data_with_coords()

# -----------------------------
# Load ML Model
# -----------------------------
model = joblib.load("aqi_model.pkl")  # ensure model file is in the same directory

# -----------------------------
# UI - Title
# -----------------------------
st.title("🌏 India Air Quality Index (AQI) Dashboard")

# -----------------------------
# Sidebar Search
# -----------------------------
st.sidebar.header("🔍 Search Location")
search_state = st.sidebar.selectbox("Select a State:", sorted(df["State"].unique()))

# -----------------------------
# Overall AQI Map
# -----------------------------
st.subheader("Overall AQI across India")
fig = px.scatter_mapbox(
    df,
    lat="Latitude",
    lon="Longitude",
    size="AQI",  # replace with your AQI column
    color="AQI",
    hover_name="State",
    color_continuous_scale=px.colors.cyclical.IceFire,
    zoom=3,
    height=600
)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Details for Selected State
# -----------------------------
st.subheader(f"📍 AQI details for {search_state}")
state_data = df[df["State"] == search_state]

if not state_data.empty:
    st.dataframe(state_data)
else:
    st.warning("⚠️ Data not available for this state.")

# -----------------------------
# Model Prediction
# -----------------------------
st.subheader("🔮 Predict AQI from Inputs")

col1, col2, col3 = st.columns(3)
pm25 = col1.number_input("PM2.5", min_value=0.0, value=50.0)
pm10 = col2.number_input("PM10", min_value=0.0, value=80.0)
co = col3.number_input("CO", min_value=0.0, value=0.5)

if st.button("Predict AQI"):
    features = [[pm25, pm10, co]]
    prediction = model.predict(features)[0]
    st.success(f"Predicted AQI: {prediction:.2f}")
