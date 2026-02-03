import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="Steam Axia Monitor",
    page_icon="🔥",
    layout="wide"
)

# --- CONSTANTS ---
# REPLACE THIS URL WITH YOUR ACTUAL RAW GITHUB URL
GITHUB_DATA_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main/data/df_clean.csv"

# --- DATA LOADING ---
@st.cache_data
def load_data(url):
    try:
        df = pd.read_csv(url)
        
        # Convert Timestamp to datetime
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Calculate Scaling Delta if columns exist
        if 'StackTempMbus' in df.columns and 'SteamTempMbus' in df.columns:
            df['Scaling_Delta'] = df['StackTempMbus'] - df['SteamTempMbus']
            
        return df
    except Exception as e:
        st.error(f"Error loading data from GitHub: {e}")
        return pd.DataFrame()

# --- MAIN APP ---
def main():
    st.title("🔥 Steam Axia Operational Dashboard")
    st.markdown("Real-time monitoring of Blower Damper, Tube Scaling, Pressure, and O2.")

    # Load Data
    with st.spinner('Fetching data from GitHub...'):
        df = load_data(GITHUB_DATA_URL)

    if df.empty:
        st.warning("No data loaded. Please check the GitHub URL in the code.")
        return

    # Sidebar Filters (Optional but useful)
    st.sidebar.header("Filter Options")
    
    # Date Range Filter logic (if data spans multiple days)
    min_date = df['Timestamp'].min().date()
    max_date = df['Timestamp'].max().date()
    
    selected_date = st.sidebar.date_input(
        "Select Date",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter DataFrame based on selection
    mask = (df['Timestamp'].dt.date == selected_date)
    df_filtered = df.loc[mask]

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

    # X-Axis Formatting (HH:MM)
    fig.update_xaxes(
        tickformat="%H:%M",
        title_text="Time (HH:MM)",
        row=4, col=1
    )

    # Display Plot
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
