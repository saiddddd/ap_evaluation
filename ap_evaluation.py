import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

st.sidebar.header("Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = df[['date', 'level', 'location', 'yearweek', 'raw_value', 'initial_projection', 'latest_projection']]
    st.sidebar.success("File uploaded successfully!")

    st.sidebar.header("Select Filters")

    level = st.sidebar.selectbox("Select Level", df['level'].dropna().unique())
    available_locations = df[df['level'] == level]['location'].dropna().unique()
    location = st.sidebar.selectbox("Select Location", available_locations)

    df_filtered = df[
        (df['level'] == level) &
        (df['location'] == location)
    ].copy()

    if 'yearweek' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['yearweek'].notna()]
        df_filtered['yearweek'] = df_filtered['yearweek'].astype(str).str.zfill(6)
        df_filtered['year'] = df_filtered['yearweek'].str[:4].astype(int)
        df_filtered['week'] = df_filtered['yearweek'].str[4:].astype(int)
        df_filtered = df_filtered[(df_filtered['week'] > 0) & (df_filtered['week'] <= 53)]
        df_filtered['time'] = pd.to_datetime(df_filtered['year'].astype(str) + '-W' + df_filtered['week'].astype(str) + '-1', format='%Y-W%W-%w', errors='coerce')
        df_filtered = df_filtered[df_filtered['time'].notna() & (df_filtered['time'].dt.year >= 2000)]

    st.header(f"Adaptive Projection for {location}")

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.lineplot(data=df_filtered, x='time', y='raw_value', label='Raw Value', color='blue', ax=ax)
    sns.lineplot(data=df_filtered, x='time', y='initial_projection', label='Initial Projection', color='orange', ax=ax)
    sns.lineplot(data=df_filtered, x='time', y='latest_projection', label='Latest Projection', color='green', ax=ax)

    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    ax.set_xlabel("Time")
    ax.set_ylabel("Payload (TByte)")
    ax.set_title(f"Payload Adaptive Projection for {location}")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    st.subheader("Descriptive Statistics")
    st.write(df_filtered[['raw_value', 'initial_projection', 'latest_projection']].describe())
