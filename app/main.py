import streamlit as st
import pandas as pd
import os
from utils import load_data, summarize_data, plot_boxplot_multi_country, plot_time_series # THIS LINE IS CHANGED!

st.set_page_config(
    page_title="MoonLight Energy Solutions Dashboard (WIP)",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_DIR = "data"
BENIN_DATA_PATH = os.path.join(DATA_DIR, "benin_clean.csv")
SIERRALEONE_DATA_PATH = os.path.join(DATA_DIR, "sierraleone_clean.csv")
TOGO_DATA_PATH = os.path.join(DATA_DIR, "togo_clean.csv")

st.header("Loading Solar Potential Data...")
benin_df = load_data(BENIN_DATA_PATH)
sierraleone_df = load_data(SIERRALEONE_DATA_PATH)
togo_df = load_data(TOGO_DATA_PATH)

country_dfs = {
    "Benin": benin_df,
    "SierraLeone": sierraleone_df,
    "Togo": togo_df
}

loaded_country_dfs = {k: v for k, v in country_dfs.items() if v is not None}

if not loaded_country_dfs:
    st.error("Could not load any country data. Some visualizations may not be available.")
    st.stop()

st.title("☀️ MoonLight Energy Solutions Dashboard (WIP)")
st.write("Welcome to the interactive solar potential dashboard, visualizing solar potential across countries.")

tab1, tab2 = st.tabs(["📊 Cross-Country Analysis", "📈 Single Country Time Series"])

with tab1:
    st.header("Global Solar Potential Overview")

    summary_df = summarize_data(loaded_country_dfs)
    if summary_df is not None:
        st.subheader("Country Solar Potential Summaries")
        st.dataframe(summary_df.set_index('Country'), use_container_width=True)
    else:
        st.warning("No data to display in summary table.")

    combined_df_list = []
    for country_name, df in loaded_country_dfs.items():
        if df is not None and not df.empty:
            df['Country'] = country_name
            combined_df_list.append(df[['Country', 'GHI', 'DNI', 'DHI']].copy())

    if combined_df_list:
        combined_df = pd.concat(combined_df_list, ignore_index=True)
        metrics = ['GHI', 'DNI', 'DHI']
        selected_metric_boxplot = st.selectbox("Select Metric for Cross-Country Boxplot", metrics, key='boxplot_metric')

        if selected_metric_boxplot:
            st.subheader(f"{selected_metric_boxplot} Distribution Across Countries")
            boxplot_fig = plot_boxplot_multi_country(combined_df, selected_metric_boxplot)
            if boxplot_fig:
                st.plotly_chart(boxplot_fig, use_container_width=True)
    else:
        st.warning("Not enough data loaded to perform cross-country comparisons.")

with tab2:
    st.header("Detailed Single Country Analysis")

    country_options = list(loaded_country_dfs.keys())
    selected_country_ts = st.selectbox("Select a Country for Time Series Analysis", country_options, key='ts_country')

    if selected_country_ts and selected_country_ts in loaded_country_dfs:
        df_selected_country = loaded_country_dfs[selected_country_ts]
        if df_selected_country is not None and not df_selected_country.empty:
            metrics_ts = ['GHI', 'DNI', 'DHI']
            selected_metric_ts = st.selectbox(f"Select Metric for {selected_country_ts}", metrics_ts, key='ts_metric')

            if selected_metric_ts:
                st.subheader(f"{selected_metric_ts} Time Series for {selected_country_ts}")
                ts_fig = plot_time_series(df_selected_country, selected_metric_ts, selected_country_ts)
                if ts_fig:
                    st.plotly_chart(ts_fig, use_container_width=True)
                else:
                    st.warning("Time series plot could not be generated for selected options.")
        else:
            st.warning(f"No data available for {selected_country_ts}.")
    else:
        st.info("Please select a country to view its time series data.")

st.markdown("---")
st.markdown("Developed for MoonLight Energy Solutions (WIP)")