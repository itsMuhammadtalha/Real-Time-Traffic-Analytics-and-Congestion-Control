import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set page config
st.set_page_config(page_title="Traffic Network Simulation", layout="wide")

# Define the junction coordinates
JUNCTION_COORDINATES = {
    1: (50, 50),
    2: (300, 50),
    3: (550, 50),
    4: (50, 250),
    5: (300, 250),
    6: (550, 250),
    7: (800, 250),
    8: (50, 450),
    9: (300, 450),
    10: (550, 450)
}

# Define the connections between junctions
CONNECTIONS = [
    (1, 2), (2, 3), (3, 7),
    (1, 4), (2, 5), (3, 6),
    (4, 5), (5, 6), (6, 7),
    (4, 8), (5, 9), (6, 10),
    (8, 9), (9, 10)
]

# Function to generate random congestion levels
def generate_congestion():
    return {j: np.random.random() for j in JUNCTION_COORDINATES}

# Function to update signal timings based on congestion
def update_signal_timings(congestion):
    return {j: 60 if c > 0.7 else 45 if c > 0.4 else 30 for j, c in congestion.items()}

# Function to generate car positions
def generate_cars(num_cars=20):
    cars = []
    for _ in range(num_cars):
        start, end = np.random.choice(list(JUNCTION_COORDINATES.keys()), 2, replace=False)
        progress = np.random.random()
        start_pos = np.array(JUNCTION_COORDINATES[start])
        end_pos = np.array(JUNCTION_COORDINATES[end])
        pos = start_pos + progress * (end_pos - start_pos)
        cars.append((*pos, start, end))
    return cars

# Function to create the network plot
def create_network_plot(congestion, signal_timings, cars):
    fig = go.Figure()

    # Add connections
    for start, end in CONNECTIONS:
        x0, y0 = JUNCTION_COORDINATES[start]
        x1, y1 = JUNCTION_COORDINATES[end]
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(color='gray', width=2)))

    # Add junctions
    junction_x, junction_y = zip(*JUNCTION_COORDINATES.values())
    junction_colors = ['green' if c < 0.4 else 'yellow' if c < 0.7 else 'red' for c in congestion.values()]
    junction_sizes = [30 + timing/2 for timing in signal_timings.values()]  # Size represents signal timing
    fig.add_trace(go.Scatter(
        x=junction_x, y=junction_y, mode='markers',
        marker=dict(size=junction_sizes, color=junction_colors, line=dict(width=2, color='white')),
        text=[f"Junction {j}<br>Congestion: {c:.2f}<br>Signal Timing: {t}s" for j, (c, t) in enumerate(zip(congestion.values(), signal_timings.values()), 1)],
        hoverinfo='text'
    ))

    # Add cars
    if cars:
        car_x, car_y, _, _ = zip(*cars)
        fig.add_trace(go.Scatter(
            x=car_x, y=car_y, mode='markers',
            marker=dict(symbol='car', size=10, color='blue'),
            hoverinfo='none'
        ))

    # Set layout
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='rgba(0,255,0,0.1)',  # Light green background
        width=1000,
        height=600,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    return fig

# Streamlit app
st.title("Dynamic Traffic Network Simulation")

# Initialize session state
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
    st.session_state.congestion = generate_congestion()
    st.session_state.signal_timings = update_signal_timings(st.session_state.congestion)
    st.session_state.cars = generate_cars()

# Update simulation every 3 seconds
if datetime.now() - st.session_state.last_update > timedelta(seconds=3):
    st.session_state.last_update = datetime.now()
    st.session_state.congestion = generate_congestion()
    st.session_state.signal_timings = update_signal_timings(st.session_state.congestion)
    st.session_state.cars = generate_cars()

# Create and display the network plot
fig = create_network_plot(st.session_state.congestion, st.session_state.signal_timings, st.session_state.cars)
st.plotly_chart(fig, use_container_width=True)

# Display legend
st.sidebar.title("Legend")
st.sidebar.markdown("**Congestion Levels:**")
st.sidebar.markdown("🟢 Low (<40%)")
st.sidebar.markdown("🟡 Medium (40-70%)")
st.sidebar.markdown("🔴 High (>70%)")
st.sidebar.markdown("**Junction Size:** Larger size indicates longer signal duration")
st.sidebar.markdown("🚗 Blue markers represent cars")

# Display statistics
st.sidebar.title("Statistics")
avg_congestion = np.mean(list(st.session_state.congestion.values()))
max_congestion = max(st.session_state.congestion.values())
adjusted_signals = sum(1 for t in st.session_state.signal_timings.values() if t > 30)

st.sidebar.metric("Average Congestion", f"{avg_congestion:.2%}")
st.sidebar.metric("Highest Congestion", f"{max_congestion:.2%}")
st.sidebar.metric("Adjusted Signals", adjusted_signals)

# Auto-refresh the app
st.empty()
st.experimental_rerun()