import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import random

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Traffic Analytics Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- STYLING ----
st.markdown("""
    <style>
        .css-18e3th9 { padding-top: 0rem; }  /* Remove extra padding from top */
        .css-1d391kg { padding: 1rem 2rem; }  /* Add padding for charts */
        .css-10trblm { font-size: 18px; }     /* Control sidebar text size */
    </style>
""", unsafe_allow_html=True)

# ---- DATABASE CONNECTION ----
@st.cache_resource
def get_db_connection():
    try:
        engine = create_engine('postgresql://traffic_user:password@localhost:5432/traffic_data')
        return engine
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

@st.cache_data(ttl=600)
def load_data(query, params=None):
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()  # Return empty DataFrame if connection fails
    with conn.connect() as con:
        result = con.execute(text(query), params or {})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

@st.cache_data(ttl=600)
def get_latest_data():
    conn = psycopg2.connect(
        host="localhost",
        database="traffic_data",
        user="traffic_user",
        password="password"
    )
    query = "SELECT * FROM TrafficData ORDER BY created_at DESC LIMIT 1000"
    return pd.read_sql(query, conn)

# ---- SIDEBAR FILTERS ----
st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Select Date Range", 
    [datetime.now().date() - timedelta(days=7), datetime.now().date()]
)

station_ids = load_data("SELECT DISTINCT station_id FROM TrafficData ORDER BY station_id")['station_id']
station_id = st.sidebar.selectbox("Select Station ID", options=station_ids)

# ---- MAIN LAYOUT ----
st.title("🚦 Real-Time Traffic Analytics Dashboard")

# ---- LATEST DATA SECTION ----
data = get_latest_data()
st.subheader("Latest Traffic Data")
st.dataframe(data.head(10), use_container_width=True)

# ---- REAL-TIME DATA VISUALIZATION ----
st.header("📊 Station-wise Traffic Analytics")

real_time_data = load_data("""
    SELECT * FROM TrafficData 
    WHERE station_id = :station_id
    ORDER BY day_of_data DESC, day_of_week DESC 
    LIMIT 1
""", params={"station_id": station_id})

if not real_time_data.empty:
    fig = px.bar(
        real_time_data.melt(id_vars=['station_id'], 
                            value_vars=['traffic_1_to_4', 'traffic_5_to_8', 
                                        'traffic_9_to_12', 'traffic_13_to_16', 
                                        'traffic_17_to_20', 'traffic_21_to_24']),
        x='variable', y='value', color='variable',
        labels={'variable': 'Time Interval', 'value': 'Traffic Volume'},
        title="Real-Time Traffic Volume",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- INTERACTIVE TRAFFIC PREDICTION ----
st.header("🔮 Interactive Traffic Prediction")
col1, col2, col3 = st.columns(3)

with col1:
    pred_day = st.number_input("Day of Month", min_value=1, max_value=31, value=1)
    pred_month = st.number_input("Month", min_value=1, max_value=12, value=1)
with col2:
    pred_day_of_week = st.number_input("Day of Week (1-7)", min_value=1, max_value=7, value=1)
    pred_lane = st.number_input("Lane of Travel", min_value=1, max_value=9, value=1)
with col3:
    pred_direction = st.number_input("Direction of Travel", min_value=1, max_value=9, value=1)
    pred_station = st.number_input("Station ID", min_value=1, value=station_id)

if st.button("Predict Traffic"):
    predictions = {
        f'predicted_{interval}': random.randint(0, 100) 
        for interval in ['1_to_4', '5_to_8', '9_to_12', '13_to_16', '17_to_20', '21_to_24']
    }
    st.success("Predicted Traffic:")
    st.json(predictions)

# ---- SEASONAL TRAFFIC TRENDS ----
st.header("📈 Seasonal Traffic Trends")
fig2 = px.box(
    data, x='month_of_data', y='predicted_total_traffic', 
    title='Seasonal Traffic Trends', template="plotly_dark"
)
st.plotly_chart(fig2, use_container_width=True)
