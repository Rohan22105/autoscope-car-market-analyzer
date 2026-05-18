import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# AutoScope - Used Car Market Intelligence Dashboard
# ---------------------------------------------------------

st.set_page_config(
    page_title="AutoScope",
    page_icon="🚗",
    layout="wide"
)

st.title(" AutoScope - Used Car Market Intelligence Dashboard")

st.write(
    """
    AutoScope analyzes real used-car market data to identify pricing trends,
    depreciation patterns, and potentially underpriced listings based on
    mileage, age, and estimated market value.
    """
)

# ---------------------------------------------------------
# LOAD REAL DATASET
# ---------------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("vehicles.csv", low_memory=False)

    # Select useful columns
    df = df[
        [
            "manufacturer",
            "model",
            "year",
            "price",
            "odometer",
            "fuel",
            "transmission",
            "type",
            "state"
        ]
    ]

    # Rename columns
    df.columns = [
        "Brand",
        "Model",
        "Year",
        "Price",
        "Mileage",
        "Fuel Type",
        "Transmission",
        "Body Type",
        "State"
    ]

    # Remove missing values
    df = df.dropna()

    # Clean unrealistic values
    df = df[
        (df["Price"] > 1000)
        & (df["Price"] < 150000)
        & (df["Mileage"] > 0)
        & (df["Mileage"] < 300000)
        & (df["Year"] >= 2000)
    ]
    df = df.sample(3000, random_state=42)

    return df


df = load_data()

# ---------------------------------------------------------
# CREATE ANALYTICS COLUMNS
# ---------------------------------------------------------

current_year = 2026

df["Vehicle Age"] = current_year - df["Year"]

# Estimated market value formula
df["Estimated Market Value"] = (
    df["Price"]
    + (df["Vehicle Age"] * 1200)
    + (df["Mileage"] * 0.03)
)

# Compare listed price against estimated market value
df["Value Difference"] = (
    df["Estimated Market Value"] - df["Price"]
)

# Depreciation estimate
df["Depreciation %"] = (
    (df["Vehicle Age"] * 6)
    + (df["Mileage"] / 15000)
)

# Price per mile metric
df["Price per Mile"] = (
    df["Price"] / df["Mileage"]
)

# Deal score calculation
df["Deal Score"] = (
    (df["Value Difference"] / 1000)
    + ((300000 - df["Mileage"]) / 50000)
    + ((50000 - df["Price"]) / 10000)
)

df["Deal Score"] = df["Deal Score"].round(2)

# Market labeling
def market_label(row):
    if row["Value Difference"] > 4000:
        return "Underpriced"
    elif row["Value Difference"] < -4000:
        return "Overpriced"
    else:
        return "Fair Price"

df["Market Status"] = df.apply(market_label, axis=1)

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------

st.sidebar.header("Filter Listings")

selected_brands = st.sidebar.multiselect(
    "Brand",
    options=sorted(df["Brand"].unique()),
    default=sorted(df["Brand"].unique())[:10]
)

selected_body_types = st.sidebar.multiselect(
    "Body Type",
    options=sorted(df["Body Type"].unique()),
    default=sorted(df["Body Type"].unique())
)

price_range = st.sidebar.slider(
    "Price Range",
    int(df["Price"].min()),
    int(df["Price"].max()),
    (
        int(df["Price"].min()),
        int(df["Price"].max())
    )
)

year_range = st.sidebar.slider(
    "Year Range",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (
        int(df["Year"].min()),
        int(df["Year"].max())
    )
)

mileage_range = st.sidebar.slider(
    "Mileage Range",
    int(df["Mileage"].min()),
    int(df["Mileage"].max()),
    (
        int(df["Mileage"].min()),
        int(df["Mileage"].max())
    )
)

filtered_df = df[
    (df["Brand"].isin(selected_brands))
    & (df["Body Type"].isin(selected_body_types))
    & (df["Price"].between(price_range[0], price_range[1]))
    & (df["Year"].between(year_range[0], year_range[1]))
    & (df["Mileage"].between(mileage_range[0], mileage_range[1]))
]

# ---------------------------------------------------------
# DASHBOARD METRICS
# ---------------------------------------------------------

st.subheader(" Market Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Listings", len(filtered_df))

col2.metric(
    "Average Price",
    f"${filtered_df['Price'].mean():,.0f}"
)

col3.metric(
    "Average Mileage",
    f"{filtered_df['Mileage'].mean():,.0f}"
)

col4.metric(
    "Average Deal Score",
    f"{filtered_df['Deal Score'].mean():.2f}"
)

# ---------------------------------------------------------
# BEST DEAL SECTION
# ---------------------------------------------------------

st.subheader(" Best Deal Recommendation")

if not filtered_df.empty:

    best_car = filtered_df.sort_values(
        "Deal Score",
        ascending=False
    ).iloc[0]

    st.success(
        f"""
        Best Deal Found:
        {best_car['Year']} {best_car['Brand']} {best_car['Model']}

        Price: ${best_car['Price']:,}
        Mileage: {best_car['Mileage']:,} miles
        Deal Score: {best_car['Deal Score']}
        Market Status: {best_car['Market Status']}
        """
    )

# ---------------------------------------------------------
# DISPLAY TABLE
# ---------------------------------------------------------

st.subheader(" Filtered Car Listings")

display_columns = [
    "Brand",
    "Model",
    "Year",
    "Body Type",
    "Mileage",
    "Price",
    "Estimated Market Value",
    "Value Difference",
    "Deal Score",
    "Market Status",
    "State"
]

st.dataframe(
    filtered_df[display_columns]
    .sort_values("Deal Score", ascending=False),
    use_container_width=True
)

# ---------------------------------------------------------
# VISUALIZATIONS
# ---------------------------------------------------------

st.subheader(" Market Visualizations")

chart_col1, chart_col2 = st.columns(2)

# Mileage vs Price
with chart_col1:

    st.write("### Mileage vs Price")

    fig1, ax1 = plt.subplots()

    ax1.scatter(
        filtered_df["Mileage"],
        filtered_df["Price"]
    )

    ax1.set_xlabel("Mileage")
    ax1.set_ylabel("Price")
    ax1.set_title("Mileage vs Price")

    st.pyplot(fig1)

# Average Price by Brand
with chart_col2:

    st.write("### Average Price by Brand")

    avg_price_brand = (
        filtered_df
        .groupby("Brand")["Price"]
        .mean()
        .sort_values()
    )

    fig2, ax2 = plt.subplots()

    ax2.bar(
        avg_price_brand.index,
        avg_price_brand.values
    )

    ax2.set_xlabel("Brand")
    ax2.set_ylabel("Average Price")
    ax2.set_title("Average Price by Brand")

    plt.xticks(rotation=45)

    st.pyplot(fig2)

# ---------------------------------------------------------
# SECOND ROW OF CHARTS
# ---------------------------------------------------------

chart_col3, chart_col4 = st.columns(2)

# Deal Score Distribution
with chart_col3:

    st.write("### Deal Score Distribution")

    fig3, ax3 = plt.subplots()

    ax3.hist(
        filtered_df["Deal Score"],
        bins=20
    )

    ax3.set_xlabel("Deal Score")
    ax3.set_ylabel("Frequency")

    st.pyplot(fig3)

# Market Status Pie Chart
with chart_col4:

    st.write("### Market Status Breakdown")

    status_counts = (
        filtered_df["Market Status"]
        .value_counts()
    )

    fig4, ax4 = plt.subplots()

    ax4.pie(
        status_counts.values,
        labels=status_counts.index,
        autopct="%1.1f%%"
    )

    st.pyplot(fig4)

# ---------------------------------------------------------
# INSIGHTS SECTION
# ---------------------------------------------------------

st.subheader(" AutoScope Insights")

if not filtered_df.empty:

    underpriced_count = len(
        filtered_df[
            filtered_df["Market Status"] == "Underpriced"
        ]
    )

    overpriced_count = len(
        filtered_df[
            filtered_df["Market Status"] == "Overpriced"
        ]
    )

    best_brand = (
        filtered_df
        .groupby("Brand")["Deal Score"]
        .mean()
        .idxmax()
    )

    st.write(
        f"""
        AutoScope identified **{underpriced_count} underpriced listings**
        and **{overpriced_count} overpriced listings** within the current
        filtered market.

        The brand with the highest average deal score is
        **{best_brand}**.

        This dashboard demonstrates how pricing, mileage,
        depreciation, and estimated market value can be used
        to evaluate vehicle listings more intelligently than
        simply comparing sticker prices alone.
        """
    )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown("---")

st.caption(
    "AutoScope | Built with Python, Pandas, Streamlit, and Matplotlib"
)