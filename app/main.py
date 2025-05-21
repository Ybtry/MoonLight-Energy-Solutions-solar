import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import plotly.express as px

st.set_page_config(layout="wide")
st.title("MoonLight Energy Solutions Dashboard (WIP)")
st.write("Welcome to the interactive solar potential dashboard, visualizing solar potential across countries.")

@st.cache_data
def load_data(country_name):
    try:
        script_dir = os.path.dirname(__file__)

        if country_name == 'benin':
            file_name = 'benin_clean.csv'
        elif country_name == 'sierraleone':
            file_name = 'sierraleone_clean.csv'
        elif country_name == 'togo':
            file_name = 'togo_clean.csv'
        else:
            st.error(f"Invalid country name: {country_name}")
            return pd.DataFrame()

        file_path = os.path.abspath(os.path.join(script_dir, '..', 'data', file_name))

        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"Error: '{file_name}' not found. Looked for it at: '{file_path}'. Please ensure it's in the 'data/' directory inside your project root.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred while loading {country_name} data: {e}")
        return pd.DataFrame()

df_benin = load_data('benin')
df_sierraleone = load_data('sierraleone')
df_togo = load_data('togo')

df_all_countries = pd.DataFrame()
metrics = ['GHI', 'DNI', 'DHI']

if not df_benin.empty and not df_sierraleone.empty and not df_togo.empty:
    df_benin['Country'] = 'Benin'
    df_sierraleone['Country'] = 'Sierra Leone'
    df_togo['Country'] = 'Togo'
    df_all_countries = pd.concat([df_benin, df_sierraleone, df_togo], ignore_index=True)
else:
    st.warning("Could not load all country data for comparison. Some visualizations may not be available.")

st.header("1. Cross-Country Solar Potential Comparison")

if not df_all_countries.empty:
    selected_metric_boxplot = st.selectbox("Select a solar metric for cross-country boxplot comparison:", metrics)

    if selected_metric_boxplot:
        st.write(f"### Distribution of {selected_metric_boxplot} across Countries")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(x='Country', y=selected_metric_boxplot, data=df_all_countries, palette='viridis', ax=ax)
        ax.set_xlabel("Country")
        ax.set_ylabel(f"{selected_metric_boxplot} (W/m²)")
        ax.set_title(f'Distribution of {selected_metric_boxplot} by Country')
        st.pyplot(fig)
else:
    st.info("No combined data available for cross-country boxplots. Please check data loading.")


st.header("2. Time Series Analysis of Solar Metrics")

if not df_all_countries.empty:
    countries = df_all_countries['Country'].unique().tolist()
    selected_country_ts = st.selectbox("Select a Country for Time Series Analysis:", countries)

    df_selected_country_ts = df_all_countries[df_all_countries['Country'] == selected_country_ts].copy()

    selected_timeseries_metric = st.selectbox(f"Select a metric for {selected_country_ts} time series:", metrics)

    if selected_timeseries_metric:
        st.write(f"### {selected_timeseries_metric} Time Series for {selected_country_ts}")

        if 'Timestamp' in df_selected_country_ts.columns:
            if not pd.api.types.is_datetime64_any_dtype(df_selected_country_ts['Timestamp']):
                df_selected_country_ts['Timestamp'] = pd.to_datetime(df_selected_country_ts['Timestamp'])
        else:
            st.warning(f"Timestamp column not found in data for {selected_country_ts}. Time series plot not available.")
            df_selected_country_ts = pd.DataFrame()

        if not df_selected_country_ts.empty:
            fig_ts = px.line(df_selected_country_ts,
                             x='Timestamp',
                             y=selected_timeseries_metric,
                             title=f'{selected_timeseries_metric} Over Time in {selected_country_ts}',
                             labels={'Timestamp': 'Date', selected_timeseries_metric: f'{selected_timeseries_metric} (W/m²)'})

            fig_ts.update_layout(hovermode="x unified")
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No data available to generate time series plot for the selected country/metric.")
else:
    st.info("No combined data available for time series analysis.")


st.header("3. Country Solar Potential Summaries")

if not df_all_countries.empty:
    st.write("### Average Solar Metrics by Country")

    summary_df = df_all_countries.groupby('Country')[metrics].mean().reset_index()

    summary_df = summary_df.sort_values(by='GHI', ascending=False)

    for col in metrics:
        if col in summary_df.columns:
            summary_df[col] = summary_df[col].round(2)

    st.dataframe(summary_df, use_container_width=True)

    st.write("""
        <small>
        *GHI: Global Horizontal Irradiance (average W/m²)<br>
        *DNI: Direct Normal Irradiance (average W/m²)<br>
        *DHI: Diffuse Horizontal Irradiance (average W/m²)
        </small>
    """, unsafe_allow_html=True)

else:
    st.info("No combined data available for country summaries. Please check data loading.")