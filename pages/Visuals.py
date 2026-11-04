
# Visualizations page
import pandas as pd
import pydeck as pdk
import streamlit as st
import json
import plotly.express as px

# Page setup
st.set_page_config(
    page_title="Visuals",
    page_icon="📈",
)

# Page title
st.title("National Parks Explorer")
st.write("Explore visitation at America's national parks.")
tab1, tab2 = st.tabs(["🏞️ National Parks", "📊 Survey Results"])
with tab1:
    # PART 1: GRAPHS FROM data.json

    # Reading JSON file
    infile = open("data.json", "r")
    parks_data = json.load(infile)
    infile.close()


    # Static chart: 2025 park visitation

    # Getting records from 2025
    parks_2025 = []

    for park in parks_data["data"]:
        if park["year"] == 2025:
            parks_2025.append(park)

    # Sorting parks by visitor count
    parks_2025.sort(key=lambda park: park["visitors"],reverse=True)

    # Dictionary of park names and visitor counts
    chart_data = {}

    for park in parks_2025:
        chart_data[park["park"]] = park["visitors"]

    # Bar chart
    st.subheader("2025 National Park Visitation")
    st.bar_chart(chart_data, x_label="National Park", y_label="Number of Visitors", sort = False)


    # Dynamic chart: visitation by year

    # Park coordinates (latitude, longitude)
    park_locations = {
        "Great Smoky Mountains": (35.61, -83.53),
        "Zion": (37.30, -113.03),
        "Yellowstone": (44.60, -110.50),
        "Grand Canyon": (36.06, -112.14),
        "Yosemite": (37.85, -119.54),
        "Rocky Mountain": (40.34, -105.68),
        "Acadia": (44.35, -68.21),
        "Grand Teton": (43.79, -110.68),
        "Olympic": (47.80, -123.60),
        "Glacier": (48.70, -113.80)
    }

    # Session State: selected year
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = 2025

    # Year slider
    selected_year = st.slider(
        "Select a year -> (Selected year will reflect park visitation on map by size of bubble.)",
        min_value=2016,
        max_value=2025,
        key="selected_year"
    )

    # Records for selected year
    parks_selected = []

    for park in parks_data["data"]:
        if park["year"] == selected_year:
            parks_selected.append(park)

    # Adding coordinates to park records
    map_parks = []

    for park in parks_selected:
        location = park_locations[park["park"]]

        map_parks.append({
            "park": park["park"],
            "visitors": park["visitors"],
            "latitude": location[0],
            "longitude": location[1]
        })

    # Organizing data for Plotly
    map_data = {
        "park": [],
        "visitors": [],
        "latitude": [],
        "longitude": []
    }

    for park in map_parks:
        map_data["park"].append(park["park"])
        map_data["visitors"].append(park["visitors"])
        map_data["latitude"].append(park["latitude"])
        map_data["longitude"].append(park["longitude"])

    # Plotly bubble map
    st.subheader("Explore National Park Visitation")

    fig = px.scatter_geo(
        map_data,
        lat="latitude",
        lon="longitude",
        size="visitors",
        hover_name="park",
        hover_data=["visitors"],
        scope="usa",
        title=f"National Park Visitors in {selected_year}"
    )

    # Map background and state borders - (Did lots of extra research, wanted background to match theme a bit better)
    fig.update_geos(
        scope="usa",
        fitbounds="locations",
        showland=True,
        landcolor="#172923",
        showocean=True,
        oceancolor="#101915",
        showlakes=True,
        lakecolor="#101915",
        showcountries=True,
        countrycolor="#34483F",
        showsubunits=True,
        subunitcolor="#52665A",
        bgcolor="#0E1117"
    )

    # Bubble colors and outlines
    fig.update_traces(
        marker=dict(
            color="#6FAF9B",
            opacity=0.85,
            line=dict(color="#C0DDD0",width=1),
            sizemin=7
        )
    )

    # Chart title and overall appearance
    fig.update_layout(
        title=dict(
            font=dict(
                color="#E5EFE8",
                size=20
            ),
            x=0.02
        ),
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(
            color="#E5EFE8"
        ),
        height=600,
        margin=dict(
            l=10,
            r=10,
            t=65,
            b=10
        )
    )


    st.plotly_chart(fig)

with tab2:
    # PART 2: GRAPHS FROM data.csv

    # Reading CSV file
    survey_data = pd.read_csv("data.csv")

    # Reading parks JSON file
    infile = open("parks.json", "r")
    parks = json.load(infile)
    infile.close()

    # Static chart: total reported visits by park

    # Adding together visits for each park
    park_totals = survey_data.groupby("Category", as_index=False)["Value"].sum()

    # Adding coordinates to park records
    map_parks = []

    for park in park_totals.to_dict("records"):
        location = parks[park["Category"]]

        map_parks.append({
            "park": park["Category"],
            "visitors": park["Value"],
            "latitude": location["latitude"],
            "longitude": location["longitude"]
        })

    # 3D map
    st.subheader("Reported Visits by National Park")

    map_layer = pdk.Layer(
        "ColumnLayer",
        data=map_parks,
        get_position="[longitude, latitude]",
        get_elevation="visitors",
        elevation_scale=80000,
        radius=60000,
        get_fill_color=[219, 0, 18],
        pickable=True,
        auto_highlight=True
    )

    map_view = pdk.ViewState(
        latitude=39.5,
        longitude=-98.35,
        zoom=3,
        pitch=45
    )

    park_map = pdk.Deck(
        layers=[map_layer],
        initial_view_state=map_view,
        tooltip={"text": "{park}\nReported visits: {visitors}"}
    )

    st.pydeck_chart(park_map)


    # Dynamic chart: total reported visits by park

    # Session State: minimum number of visits
    if "min_visits" not in st.session_state:
        st.session_state.min_visits = 0

    # Visits slider
    min_visits = st.slider(
        "Select the minimum number of reported visits:",
        min_value=0,
        max_value=int(survey_data["Value"].max()),
        key="min_visits"
    )

    # Adding together visits for each park
    park_totals = survey_data.groupby("Category", as_index=False)["Value"].sum()

    # Sorting parks by total visits
    park_totals = park_totals.sort_values("Value", ascending=False)

    # Filtering parks
    filtered_data = park_totals[park_totals["Value"] >= min_visits]

    # Calculating summary statistics
    mean_visits = filtered_data["Value"].mean()
    median_visits = filtered_data["Value"].median()

    # Displaying summary statistics
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Mean Visits", round(mean_visits, 2))

    with col2:
        st.metric("Median Visits", round(median_visits, 2))

    # Horizontal bar chart
    st.subheader("Compare Reported Visits by National Park")

    fig = px.bar(
        filtered_data,
        x="Value",
        y="Category",
        orientation="h",
        title="Total Reported Visits by Park",
        labels={
            "Value": "Number of Visits",
            "Category": "National Park"
        }
    )

    # Chart appearance
    fig.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#E5EFE8"),
        height=500,
        yaxis=dict(autorange="reversed",)
    )

    st.plotly_chart(fig)