import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz
import plotly.express as px

st.set_page_config(page_title="Property Investment Dashboard", layout="wide")

# ----------------------------
# Load Data
# ----------------------------
@st.cache_data
def load_data():
    demo = pd.read_csv("data/demographics.csv")
    listings = pd.read_csv("data/listings.csv")

    # Convert zip columns to string
    demo["zip_code"] = demo["zip_code"].astype(str)
    listings["postal_code"] = listings["postal_code"].astype(str)

    return demo, listings


# ----------------------------
# Clean Postal Code
# ----------------------------
def clean_zip(zip_code):
    return str(zip_code).replace("XX", "").strip()


# ----------------------------
# Fuzzy Matching Join
# ----------------------------
def fuzzy_join(listings, demo):

    demo_zips = demo["zip_code"].tolist()

    # Clean postal code
    listings["postal_code_clean"] = listings["postal_code"].apply(clean_zip)

    def match_zip(zip_code):
        match = process.extractOne(
            zip_code,
            demo_zips,
            scorer=fuzz.ratio
        )
        if match and match[1] > 70:
            return match[0]
        return None

    listings["matched_zip"] = listings["postal_code_clean"].apply(match_zip)

    merged = listings.merge(
        demo,
        left_on="matched_zip",
        right_on="zip_code",
        how="left"
    )

    return merged


# ----------------------------
# Load and Merge Data
# ----------------------------
demo_df, listings_df = load_data()
merged_df = fuzzy_join(listings_df, demo_df)

# Remove unmatched rows
merged_df = merged_df.dropna(subset=["median_income"])


# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")

zip_filter = st.sidebar.multiselect(
    "ZIP Code",
    sorted(merged_df["matched_zip"].unique())
)

price_range = st.sidebar.slider(
    "Listing Price",
    int(merged_df["listing_price"].min()),
    int(merged_df["listing_price"].max()),
    (
        int(merged_df["listing_price"].min()),
        int(merged_df["listing_price"].max())
    )
)

filtered_df = merged_df.copy()

if zip_filter:
    filtered_df = filtered_df[
        filtered_df["matched_zip"].isin(zip_filter)
    ]

filtered_df = filtered_df[
    (filtered_df["listing_price"] >= price_range[0]) &
    (filtered_df["listing_price"] <= price_range[1])
]


# ----------------------------
# Dashboard Title
# ----------------------------
st.title("🏠 Property Investment Insights Dashboard")


# ----------------------------
# KPI Section
# ----------------------------
col1, col2, col3 = st.columns(3)

avg_price = filtered_df["listing_price"].mean()

avg_price_sqft = (
    filtered_df["listing_price"] / filtered_df["sq_ft"]
).mean()

avg_school_rating = filtered_df["school_rating"].mean()

col1.metric("Average Listing Price", f"${avg_price:,.0f}")
col2.metric("Average Price per SqFt", f"${avg_price_sqft:,.2f}")
col3.metric("Average School Rating", f"{avg_school_rating:.1f}")


# ----------------------------
# Scatter Plot
# ----------------------------
st.subheader("Listing Price vs Median Income")

scatter_fig = px.scatter(
    filtered_df,
    x="median_income",
    y="listing_price",
    size="sq_ft",
    hover_data=["raw_address"]
)

st.plotly_chart(scatter_fig, use_container_width=True)


# ----------------------------
# Histogram
# ----------------------------
st.subheader("Listing Price Distribution")

hist_fig = px.histogram(
    filtered_df,
    x="listing_price",
    nbins=30
)

st.plotly_chart(hist_fig, use_container_width=True)


# ----------------------------
# Crime vs Price
# ----------------------------
st.subheader("Crime Index vs Listing Price")

crime_fig = px.box(
    filtered_df,
    x="crime_index",
    y="listing_price"
)

st.plotly_chart(crime_fig, use_container_width=True)


# ----------------------------
# Data Table
# ----------------------------
st.subheader("Filtered Property Listings")

st.dataframe(
    filtered_df[
        [
            "raw_address",
            "matched_zip",
            "sq_ft",
            "bedrooms",
            "listing_price",
            "median_income",
            "school_rating",
            "crime_index"
        ]
    ]
)
