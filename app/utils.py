import streamlit as st
import pandas as pd
import plotly.express as px
import os

@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"Error: '{os.path.basename(file_path)}' not found. Looked for it at: '{file_path}'. Please ensure it's in the 'data/' directory inside your project root.")
        return None
    try:
        df = pd.read_csv(file_path)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading {os.path.basename(file_path)}: {e}")
        return None

def summarize_data(country_dfs):
    summary_data = []
    for country, df in country_dfs.items():
        if df is not None and not df.empty:
            ghi_avg = df['GHI'].mean() if 'GHI' in df.columns else 0
            dni_avg = df['DNI'].mean() if 'DNI' in df.columns else 0
            dhi_avg = df['DHI'].mean() if 'DHI' in df.columns else 0
            summary_data.append({
                'Country': country.replace('_clean', '').title(),
                'Average GHI (kWh/m²/day)': f"{ghi_avg:.2f}",
                'Average DNI (kWh/m²/day)': f"{dni_avg:.2f}",
                'Average DHI (kWh/m²/day)': f"{dhi_avg:.2f}"
            })
    if not summary_data:
        return None
    return pd.DataFrame(summary_data)

def plot_boxplot_multi_country(df_combined, metric):
    if df_combined is None or df_combined.empty:
        st.warning("No data available to plot boxplot.")
        return None

    fig = px.box(df_combined, x='Country', y=metric,
                 title=f'Comparison of {metric} Across Countries',
                 labels={metric: f'{metric} (kWh/m²/day)'},
                 color='Country'
                 )
    fig.update_layout(xaxis_title="Country", yaxis_title=f"{metric} (kWh/m²/day)")
    return fig

def plot_time_series(df, metric, country_name="Selected Country"):
    if df is None or df.empty or 'Date' not in df.columns or metric not in df.columns:
        st.warning(f"No valid data or 'Date' column found for {country_name} time series.")
        return None
    
    fig = px.line(df, x='Date', y=metric,
                  title=f'{metric} Over Time for {country_name}',
                  labels={'Date': 'Date', metric: f'{metric} (kWh/m²/day)'})
    fig.update_xaxes(rangeslider_visible=True)
    return fig