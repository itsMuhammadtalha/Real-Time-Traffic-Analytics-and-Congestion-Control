import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st
from sqlalchemy import create_engine, text
import random

# Database connection
@st.cache_resource
def get_db_connection():
    try:
        engine = create_engine('postgresql://traffic_user:password@localhost:5432/traffic_data')
        return engine
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# Load data from PostgreSQL
@st.cache_data(ttl=600)
def load_data(query, params=None):
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()  # Return empty DataFrame if connection fails
    with conn.connect() as con:
        result = con.execute(text(query), params or {})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

# Streamlit App Layout
st.title("Real-Time Traffic Analytics Dashboard")

# Sidebar Filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Select Date Range", 
                                   [datetime.now().date() - timedelta(days=7), datetime.now().date()])
station_ids = load_data("SELECT DISTINCT station_id FROM TrafficData ORDER BY station_id")['station_id']
station_id = st.sidebar.selectbox("Select Station ID", options=station_ids)

# Real-time Data Display
# Real-time Data Display
st.header("Real-time Traffic Data")
real_time_data = load_data("""
    SELECT * FROM TrafficData 
    WHERE station_id = :station_id
    ORDER BY day_of_data DESC, day_of_week DESC 
    LIMIT 1
""", params={"station_id": station_id})

if not real_time_data.empty:
    st.subheader("Real-Time Traffic Overview")

    fig = px.bar(
        real_time_data.melt(id_vars=['station_id'], 
                            value_vars=['traffic_1_to_4', 'traffic_5_to_8', 'traffic_9_to_12', 
                                        'traffic_13_to_16', 'traffic_17_to_20', 'traffic_21_to_24']),
        x='variable', y='value', color='variable',
        labels={'variable': 'Time Interval', 'value': 'Traffic Volume'},
        title="Real-Time Traffic Volume"
    )
    st.plotly_chart(fig, use_container_width=True)



# Historical Data Analysis
st.header("Historical Traffic Analysis")
historical_data = load_data("""
    SELECT * FROM TrafficData 
    WHERE day_of_data BETWEEN :start_date AND :end_date
    ORDER BY day_of_data, day_of_week, station_id
""", params={
    "start_date": int(date_range[0].strftime('%Y%m%d')), 
    "end_date": int(date_range[1].strftime('%Y%m%d'))
})

# Check if data is available
if historical_data.empty:
    st.warning("No historical data available for the selected date range.")
else:
    # Display the data
    st.write(f"Showing data for all stations from {date_range[0]} to {date_range[1]}")
    st.dataframe(historical_data)

    # You can add more visualizations or analysis here
    # For example:
    st.subheader("Traffic by Station")
    station_traffic = historical_data.groupby('station_id')['traffic_1_to_4'].mean().sort_values(ascending=False)
    st.bar_chart(station_traffic)


    
# Prediction Accuracy Monitoring
st.header("Prediction Accuracy")
if not historical_data.empty:
    accuracy_data = historical_data.copy()
    for interval in ['1_to_4', '5_to_8', '9_to_12', '13_to_16', '17_to_20', '21_to_24']:
        accuracy_data[f'error_{interval}'] = accuracy_data[f'traffic_{interval}'] - accuracy_data[f'predicted_{interval}']

    mae = accuracy_data[[f'error_{interval}' for interval in ['1_to_4', '5_to_8', '9_to_12', '13_to_16', '17_to_20', '21_to_24']]].abs().mean()
    st.write("Mean Absolute Error for each time interval:")
    st.write(mae)

# Interactive Predictions
st.header("Interactive Traffic Prediction")
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
    predictions = {f'predicted_{interval}': random.randint(0, 100) 
                   for interval in ['1_to_4', '5_to_8', '9_to_12', '13_to_16', '17_to_20', '21_to_24']}
    st.write("Predicted Traffic:")
    st.write(predictions)




# Verify historical data fetch
st.write("Date Range Selected:", date_range)


st.subheader("Historical Data Preview")
st.write(historical_data.head())  # Display first few rows

if historical_data.empty:
    st.warning("No historical data found for the selected range and station.")
    st.stop()
