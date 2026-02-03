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
DATA_PATH = "data/df_clean.csv"

# --- DATA LOADING ---
@st.cache_data
def load_data(path):
    try:
        if not os.path.exists(path):
            st.error(f"File not found at path: {path}")
            return pd.DataFrame()

        df = pd.read_csv(path)
        
        # FIX: Strip whitespace from column names to handle invisible spaces
        df.columns = df.columns.str.strip()
        
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
    
    # Load Data
    with st.spinner('Loading data...'):
        df = load_data(DATA_PATH)

    if df.empty:
        return

    # DEBUG: Un-comment this if you still get errors to see exact column names
    # st.write(df.columns.tolist())

    # Sidebar Filters
    st.sidebar.header("Filter Options")
    
    if 'Timestamp' in df.columns:
        min_date = df['Timestamp'].min().date()
        max_date = df['Timestamp'].max().date()
        
        selected_date = st.sidebar.date_input(
            "Select Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )
        
        mask = (df['Timestamp'].dt.date == selected_date)
        df_filtered = df.loc[mask]
    else:
        df_filtered = df

    if df_filtered.empty:
        st.info("No data available for the selected date.")
        return

    # --- PLOTLY DASHBOARD ---
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(
            "Air Flow % (Blower Damper)", 
            "Tube Scaling Delta (TStack - TSteam)", 
            "Steam Pressure", 
            "Stack O2"
        )
    )

    # 1. Air Flow (Formerly Channel 2)
    damper_col = 'Air flow %'
    if damper_col in df_filtered.columns:
        fig.add_trace(
            go.Scatter(
                x=df_filtered['Timestamp'], 
                y=df_filtered[damper_col], 
                name="Air Flow %",
                line=dict(color='#2563eb', width=2),
                fill='tozeroy',
                fillcolor='rgba(37, 99, 235, 0.1)'
            ),
            row=1, col=1
        )
    else:
        st.warning(f"Column '{damper_col}' not found. Available columns: {df.columns.tolist()}")

    # 2. Tube Scaling
    if 'Scaling_Delta' in df_filtered.columns:
        fig.add_trace(
            go.Scatter(
                x=df_filtered['Timestamp'], 
                y=df_filtered['Scaling_Delta'], 
                name="Scaling Delta (°C)",
                line=dict(color='#dc2626', width=2)
            ),
            row=2, col=1
        )

    # 3. Pressure
    if 'SteamPrMbus' in df_filtered.columns:
        fig.add_trace(
            go.Scatter(
                x=df_filtered['Timestamp'], 
                y=df_filtered['SteamPrMbus'], 
                name="Pressure (Bar)",
                line=dict(color='#059669', width=2)
            ),
            row=3, col=1
        )

    # 4. Stack O2
    if 'StackO2Mbus' in df_filtered.columns:
        fig.add_trace(
            go.Scatter(
                x=df_filtered['Timestamp'], 
                y=df_filtered['StackO2Mbus'], 
                name="Stack O2 %",
                line=dict(color='#7c3aed', width=2)
            ),
            row=4, col=1
        )

    fig.update_layout(
        height=900,
        showlegend=True,
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    fig.update_yaxes(title_text="Air Flow %", row=1, col=1)
    fig.update_yaxes(title_text="Delta °C", row=2, col=1)
    fig.update_yaxes(title_text="Bar", row=3, col=1)
    fig.update_yaxes(title_text="O2 %", row=4, col=1)

    fig.update_xaxes(
        tickformat="%H:%M",
        title_text="Time (HH:MM)",
        row=4, col=1
    )

    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
