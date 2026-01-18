import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

# -----------------------------
# Load logo FIRST
logo = Image.open("CCH logo.png")

# -----------------------------
# Page configuration (MUST be first Streamlit command)
st.set_page_config(
    page_title="CCH Data Visualization",
    page_icon=logo,
    layout="wide",
)

# -----------------------------
# Page navigation state
if "page" not in st.session_state:
    st.session_state.page = "Home"

# -----------------------------
# Sidebar navigation (available on all pages)
st.sidebar.markdown("### Navigation")
if st.sidebar.button("Home", key="home_btn"):
    st.session_state.page = "Home"
    st.rerun()
if st.sidebar.button("About Us", key="about_btn"):
    st.session_state.page = "About"
    st.rerun()

st.sidebar.markdown("---")

# =============================
# HOME PAGE
# =============================
if st.session_state.page == "Home":

    # Sidebar logo
    st.sidebar.image(logo, width=150)
    st.sidebar.markdown("##")

    # Load data
    df = pd.read_excel(
        "CCH1.0.xlsx",
        engine="openpyxl",
        sheet_name="Raw data",
        usecols="A:j",
        nrows=100,
    )

    # Sidebar filters
    st.sidebar.header("Filter Here:")
    Organisation_Name = st.sidebar.multiselect(
        "Select Organisation Name:",
        options=df["Organisation_Name"].unique(),
        default=df["Organisation_Name"].unique()
    )

    Time_of_day = st.sidebar.multiselect(
        "Select Time of day:",
        options=df["Time_of_day"].unique(),
        default=df["Time_of_day"].unique()
    )

    Location = st.sidebar.multiselect(
        "Select Location:",
        options=df["Location"].unique(),
        default=df["Location"].unique()
    )

    Capacity_tier = st.sidebar.multiselect(
        "Select Capacity Tier:",
        options=df["Capacity_tier"].unique(),
        default=df["Capacity_tier"].unique()
    )

    # Apply filters
    df_selection = df[
        (df["Organisation_Name"].isin(Organisation_Name)) &
        (df["Time_of_day"].isin(Time_of_day)) &
        (df["Location"].isin(Location)) &
        (df["Capacity_tier"].isin(Capacity_tier))
    ]

    # Title
    st.title("CCH Data Visualization Dashboard")
    st.markdown("##")

    # Metrics
    avg_price_by_tier = df_selection.groupby("Capacity_tier")["Price_per_hour"].mean().reset_index()
    avg_price_per_hour = df_selection["Price_per_hour"].mean()
    avg_price_per_person = (df_selection["Price_per_hour"] / df_selection["Capacity"]).mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Average Price per Room by Tier", "")
    col2.metric("Average Price per Person", f"£{avg_price_per_person:.2f}")
    col3.metric("Average Price per Hour", f"£{avg_price_per_hour:.2f}")

    st.dataframe(avg_price_by_tier.rename(columns={"Price_per_hour": "Average Price (£)"}))
    st.markdown("---")

    # Chart 1
    avg_price_by_time = df_selection.groupby("Time_of_day")["Price_per_hour"].mean().reset_index()
    fig1 = px.bar(avg_price_by_time, x="Time_of_day", y="Price_per_hour",
                  text=avg_price_by_time["Price_per_hour"].round(2),
                  title="Average Price per Hour by Time of Day")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("""
    **Findings:**
    - Evening prices are higher than daytime.
    - Day bookings offer better value.
    """)

    # Chart 2
    fig2 = px.bar(avg_price_by_tier, x="Capacity_tier", y="Price_per_hour",
                  text=avg_price_by_tier["Price_per_hour"].round(2),
                  title="Average Price per Room by Capacity Tier")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    **Findings:**
    - Larger rooms cost more per hour.
    - Smaller rooms suit low-budget events.
    """)

    # Heatmap
    heatmap_data = df_selection.pivot_table(
        index="Capacity_tier", columns="Time_of_day",
        values="Cost_per_person", aggfunc="mean"
    )

    fig5 = px.imshow(heatmap_data, text_auto=True,
                     title="Price per Person by Capacity Tier & Time")
    st.plotly_chart(fig5, use_container_width=True)

    # Scatter
    fig3 = px.scatter(df_selection, x="Capacity", y="Price_per_hour",
                      color="Capacity_tier",
                      title="Price per Hour vs Capacity")
    st.plotly_chart(fig3, use_container_width=True)

    # Top 5 rooms
    top_rooms = df_selection.sort_values(by="Price_per_hour", ascending=False).head(5)
    fig6 = px.bar(top_rooms, x="Names_of_Room", y="Price_per_hour",
                  color="Capacity_tier",
                  title="Top 5 Most Expensive Rooms")
    st.plotly_chart(fig6, use_container_width=True)

    # Duration chart
    avg_price_by_duration = df_selection.groupby("Minimum_Duration_per_hour")["Price_per_hour"].mean().reset_index()
    fig7 = px.line(avg_price_by_duration, x="Minimum_Duration_per_hour", y="Price_per_hour",
                   title="Price per Hour by Minimum Booking Duration")
    st.plotly_chart(fig7, use_container_width=True)

# =============================
# ABOUT PAGE
# =============================
elif st.session_state.page == "About":
    st.title("About This Dataset")

    st.markdown("""
    ### Coventry Central Hall Room Hire Dataset

    This dashboard analyses room hire data from Coventry venue halls.

    **Dataset fields include:**
    - Location  
    - Organisation Name  
    - Room Names  
    - Capacity  
    - Time of Day  
    - Minimum Booking Duration  
    - Price per Hour  
    - Cost per Person  
    - Capacity Tier  

    ### Purpose
    - Compare room prices  
    - Identify value-for-money options  
    - Support event planning  
    - Analyse pricing trends  

    ### Official Website  for hall hire
    https://coventrycentralhall.co.uk/

   """)

# Footer
footer = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color:#0c0230 ;
    text-align: center;
    padding: 10px;
    font-size: 14px;
}
</style>

<div class="footer">
Developed by Daniel Kioko                                                     © 2026 CCH Data Visualization | Built with Streamlit
</div>
"""

st.markdown(footer, unsafe_allow_html=True)
