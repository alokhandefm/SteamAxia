import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="Steam Axia Monitor",
    page_icon="🔥",
    layout="wide"
)

# --- CONSTANTS ---
# Use the relative path. This works if 'data' folder is in the same directory as this script.
DATA_PATH = "data/df_clean.csv"

# --- DATA LOADING ---
@st.cache_data
def load_data(path):
    try:
        # Check if file exists locally (good for debugging)
        if not os.path.exists(path):
            st.error(f"File not found at path: {path}")
            st.info("Please ensure 'df_clean.csv' is inside the 'data' folder in your GitHub repository.")
            return pd.DataFrame()

        df = pd.read_csv(path)
        
        # Convert Timestamp to datetime
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Calculate Scaling Delta if columns exist
        if 'StackTempMbus' in df.columns and 'SteamTempMbus' in df.columns:
            df['Scaling_Delta'] = df['StackTempMbus'] - df['SteamTempMbus']
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# --- MAIN APP ---
def main():
    st.title("🔥 Steam Axia Operational Dashboard")
    st.markdown("Real-time monitoring of Blower Damper, Tube Scaling, Pressure, and O2.")

    # Load Data
    with st.spinner('Loading data...'):
        df = load_data(DATA_PATH)

    if df.empty:
        return

    # Sidebar Filters
    st.sidebar.header("Filter Options")
    
    # Date Range Filter
    if 'Timestamp' in df.columns:
        min_date = df['Timestamp'].min().date()
        max_date = df['Timestamp'].max().date()
        
        selected_date = st.sidebar.date_input(
            "Select Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )
        
        # Filter DataFrame
        mask = (df['Timestamp'].dt.date == selected_date)
        df_filtered = df.loc[mask]
    else:
        df_filtered = df

    if df_filtered.empty:
        st.info("No data available for the selected date.")
        return

    # --- PLOTLY DASHBOARD ---
    # Create 4 stacked subplots with shared X-axis
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(
            "Blower Damper (Channel 2)", 
            "Tube Scaling Delta (TStack - TSteam)", 
            "Steam Pressure", 
            "Stack O2"
        )
    )

    # 1. Blower Damper (Blue)
    fig.add_trace(
        go.Scatter(
            x=df_filtered['Timestamp'], 
            y=df_filtered['Channel2 Position'], 
            name="Blower Damper %",
            line=dict(color='#2563eb', width=2),
            fill='tozeroy',
            fillcolor='rgba(37, 99, 235, 0.1)'
        ),
        row=1, col=1
    )

    # 2. Tube Scaling (Red)
    fig.add_trace(
        go.Scatter(
            x=df_filtered['Timestamp'], 
            y=df_filtered['Scaling_Delta'], 
            name="Scaling Delta (°C)",
            line=dict(color='#dc2626', width=2)
        ),
        row=2, col=1
    )

    # 3. Pressure (Green)
    fig.add_trace(
        go.Scatter(
            x=df_filtered['Timestamp'], 
            y=df_filtered['SteamPrMbus'], 
            name="Pressure (Bar)",
            line=dict(color='#059669', width=2)
        ),
        row=3, col=1
    )

    # 4. Stack O2 (Purple)
    fig.add_trace(
        go.Scatter(
            x=df_filtered['Timestamp'], 
            y=df_filtered['StackO2Mbus'], 
            name="Stack O2 %",
            line=dict(color='#7c3aed', width=2)
        ),
        row=4, col=1
    )

    # --- LAYOUT STYLING ---
    fig.update_layout(
        height=900,  # Tall chart
        showlegend=True,
        hovermode="x unified", # Tooltip shows all 4 values at once
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    # Y-Axis Labels
    fig.update_yaxes(title_text="Damper %", row=1, col=1)
    fig.update_yaxes(title_text="Delta °C", row=2, col=1)
    fig.update_yaxes(title_text="Bar", row=3, col=1)
    fig.update_yaxes(title_text="O2 %", row=4, col=1)

    # X-Axis Formatting
    fig.update_xaxes(
        tickformat="%H:%M",
        title_text="Time (HH:MM)",
        row=4, col=1
    )

    # Display Plot
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
