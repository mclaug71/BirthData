# app.py

import streamlit as st
import pandas as pd
import plotly.express as px

# STEP 2 — Page Config
st.set_page_config(layout="wide")
st.title("Provisional Natality Data Dashboard")
st.subheader("Birth Analysis by State and Gender")

# STEP 3 — Load Data
try:
    df = pd.read_csv("Provisional_Natality_2025_CDC.csv")
except FileNotFoundError:
    st.error("Dataset file not found in repository.")
    st.stop()

# Normalize column names
df.columns = (
    df.columns.str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Required logical fields
required_fields = [
    "state_of_residence",
    "month",
    "month_code",
    "year_code",
    "sex_of_infant",
    "births",
]

missing_fields = [field for field in required_fields if field not in df.columns]

if missing_fields:
    st.error(f"Missing required logical fields: {missing_fields}")
    st.write("Available columns in dataset:")
    st.write(df.columns)
    st.stop()

# Convert births to numeric and drop nulls
df["births"] = pd.to_numeric(df["births"], errors="coerce")
df = df.dropna(subset=["births"])

# Preserve original dataframe
filtered_df = df.copy()

# STEP 4 — Sidebar Filters
st.sidebar.header("Filters")

# Month filter
month_options = sorted(filtered_df["month"].dropna().unique())
month_selection = st.sidebar.multiselect(
    "Select Month",
    options=["All"] + list(month_options),
    default=["All"],
)

# Gender filter
gender_options = sorted(filtered_df["sex_of_infant"].dropna().unique())
gender_selection = st.sidebar.multiselect(
    "Select Gender",
    options=["All"] + list(gender_options),
    default=["All"],
)

# State filter
state_options = sorted(filtered_df["state_of_residence"].dropna().unique())
state_selection = st.sidebar.multiselect(
    "Select State",
    options=["All"] + list(state_options),
    default=["All"],
)

# STEP 5 — Filtering Logic
if "All" not in month_selection:
    filtered_df = filtered_df[filtered_df["month"].isin(month_selection)]

if "All" not in gender_selection:
    filtered_df = filtered_df[filtered_df["sex_of_infant"].isin(gender_selection)]

if "All" not in state_selection:
    filtered_df = filtered_df[filtered_df["state_of_residence"].isin(state_selection)]

# STEP 9 — Edge Case Handling for Empty Filter
if filtered_df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# STEP 6 — Aggregation
aggregated_df = (
    filtered_df.groupby(
        ["state_of_residence", "sex_of_infant"], as_index=False
    )["births"]
    .sum()
    .sort_values("state_of_residence")
)

# STEP 7 — Plot
fig = px.bar(
    aggregated_df,
    x="state_of_residence",
    y="births",
    color="sex_of_infant",
    title="Total Births by State and Gender",
    labels={
        "state_of_residence": "State of Residence",
        "births": "Total Births",
        "sex_of_infant": "Gender",
    },
)

fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    legend_title_text="Gender",
    xaxis_title="State of Residence",
    yaxis_title="Total Births",
)

st.plotly_chart(fig, use_container_width=True)

# STEP 8 — Show Filtered Table
st.dataframe(
    filtered_df.reset_index(drop=True),
    use_container_width=True,
)
