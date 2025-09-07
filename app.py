import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
import time

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="India AQI Dashboard", layout="wide")

# -----------------------------
# Load and Geocode Data
# -----------------------------
@st.cache_data
def load_and_geocode():
    df = pd.read_csv("notebooks/AQI_Clean_Data.csv")  # raw AQI dataset

    states = df['State'].unique()
    geolocator = Nominatim(user_agent="my_app")

    lat_lng_data = []
    for state in states:
        try:
            location = geolocator.geocode(state + ", India")  # ensure India context
            if location:
                lat_lng_data.append((state, location.latitude, location.longitude))
            else:
                lat_lng_data.append((state, None, None))
        except:
            lat_lng_data.append((state, None, None))
        time.sleep(1)  # avoid hitting geopy too fast

    df_lat_lng = pd.DataFrame(lat_lng_data, columns=["State", "Latitude", "Longitude"])
    merged_df = df.merge(df_lat_lng, on="State", how="left")
    return merged_df

df = load_and_geocode()

# -----------------------------
# UI - Title
# -----------------------------
st.title("🌏 India Air Quality Index (AQI) Dashboard")

# -----------------------------
# Overall AQI Map
# -----------------------------
st.subheader("Overall AQI across India (Live Geocoded)")

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
# State Search
# -----------------------------
st.sidebar.header("🔍 Search Location")
search_state = st.sidebar.selectbox("Select a State:", sorted(df["State"].unique()))

st.subheader(f"📍 AQI details for {search_state}")
state_data = df[df["State"] == search_state]

if not state_data.empty:
    st.dataframe(state_data)
else:
    st.warning("⚠️ Data not available for this state.")
