import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random

from database import init_db, get_connection
from zynd_agents import (
    WeatherAgent,
    FloodPredictionAgent,
    EmergencyCoordinationAgent,
    CommunityAlertAgent
)
from logic import consensus_reached

# -------------------------------------------------
# Streamlit Page
# -------------------------------------------------
st.set_page_config(
    page_title="Flood Resilience Network – Planet AI",
    layout="wide"
)

# -------------------------------------------------
# Initialize Database
# -------------------------------------------------
init_db()

# -------------------------------------------------
# App Header
# -------------------------------------------------
st.title("🌊 Flood Resilience Network – Planet AI")
st.caption("Decentralized Multi Agent Flood Response System")

# -------------------------------------------------
# Cities Data
# -------------------------------------------------
cities = [
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
    {"name": "Bengaluru", "lat": 12.9716, "lon": 77.5946},
    {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639},
    {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
    {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    {"name": "Pune", "lat": 18.5204, "lon": 73.8567},
    {"name": "Ahmedabad", "lat": 23.0225, "lon": 72.5714},
    {"name": "Jaipur", "lat": 26.9124, "lon": 75.7873},
    {"name": "Lucknow", "lat": 26.8467, "lon": 80.9462},
]

# -------------------------------------------------
# Region / Cities Selection 
# -------------------------------------------------
region_names = [city["name"] for city in cities]
selected_cities = st.multiselect(
    "Select City / Cities",
    region_names,
    default=[region_names[0]]
)

# -------------------------------------------------
# Main Agent Execution
# -------------------------------------------------
if st.button("Run Agent Network"):
    weather_agent = WeatherAgent("Weather Agent", "Weather Intelligence")
    flood_agent = FloodPredictionAgent("Flood Agent", "Risk Prediction")
    emergency_agent = EmergencyCoordinationAgent("Emergency Agent", "Coordination")
    alert_agent = CommunityAlertAgent("Alert Agent", "Community Alerts")

    city_data = {}
    for city_name in selected_cities:
        
        city_weather_msg = {
            "rainfall_mm": random.randint(80, 320),
            "river_level_m": round(random.uniform(2.5, 9.0), 2)
        }
        city_flood_msg = flood_agent.analyze(city_weather_msg)
        city_plan_msg = emergency_agent.plan(city_flood_msg)
        city_alert_msg, city_confidence = alert_agent.broadcast(city_name, city_flood_msg)

        city_data[city_name] = {
            "weather": city_weather_msg,
            "flood": city_flood_msg,
            "plan": city_plan_msg,
            "alert": city_alert_msg,
            "confidence": city_confidence
        }

    # -------------------------------------------------
    # Flood Probability 
    # -------------------------------------------------
    st.subheader("📊 Flood Probability per Selected City")
    bar_df = pd.DataFrame([
        {"City": city, 
         "Probability": city_data[city]["flood"]["probability"], 
         "Severity": city_data[city]["flood"]["severity"]}
        for city in selected_cities
    ])
    fig = px.bar(
        bar_df,
        x="City",
        y="Probability",
        text="Probability",
        color="Severity",
        range_y=[0, 1],
        title="Flood Probability per Selected City"
    )
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # Flood Probability Gauges 
    # -------------------------------------------------
    st.subheader("📈 Flood Risk Gauges")
    for city in selected_cities:
        city_prob = city_data[city]["flood"]["probability"] * 100
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=city_prob,
            title={"text": f"{city} Flood Probability (%)"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 40], "color": "lightgreen"},
                    {"range": [40, 70], "color": "orange"},
                    {"range": [70, 100], "color": "red"}
                ]
            }
        ))
        st.plotly_chart(gauge_fig, use_container_width=True)

    # -------------------------------------------------
    # Overall Gauge 
    # -------------------------------------------------
    st.subheader("🌐 Overall Flood Risk Gauge")
    overall_prob = max([city_data[city]["flood"]["probability"] for city in selected_cities]) * 100
    overall_gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_prob,
        title={"text": "Overall Max Flood Probability (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "darkred"},
            "steps": [
                {"range": [0, 40], "color": "lightgreen"},
                {"range": [40, 70], "color": "orange"},
                {"range": [70, 100], "color": "red"}
            ]
        }
    ))
    st.plotly_chart(overall_gauge_fig, use_container_width=True)

    # -------------------------------------------------
    # Environmental Conditions
    # -------------------------------------------------
    st.subheader("🌧 Environmental Conditions per Selected City")
    for city in selected_cities:
        env_df = pd.DataFrame({
            "Factor": ["Rainfall (mm)", "River Level (m)"],
            "Value": [
                city_data[city]["weather"]["rainfall_mm"],
                city_data[city]["weather"]["river_level_m"]
            ]
        })
        env_fig = px.bar(
            env_df,
            x="Factor",
            y="Value",
            title=f"{city} Environmental Conditions"
        )
        st.plotly_chart(env_fig, use_container_width=True)

    # -------------------------------------------------
    # Emergency Coordination 
    # -------------------------------------------------
    st.subheader("🚨 Emergency Coordination per City")
    for city in selected_cities:
        st.success(f"{city}: {city_data[city]['plan']['action']}")

    # -------------------------------------------------
    # Community Alert
    # -------------------------------------------------
    st.subheader("📢 Community Alerts")
    for city in selected_cities:
        st.markdown(f"**{city}**: {city_data[city]['alert']} (Confidence: {city_data[city]['confidence']})")

    # -------------------------------------------------
    # Agent Trust Table
    # -------------------------------------------------
    st.subheader("🤖 Active Agents & Trust")
    conn = get_connection()
    agents_df = pd.read_sql("SELECT * FROM agents", conn)
    st.dataframe(agents_df, use_container_width=True)

    # -------------------------------------------------
    # Alert Confidence Timeline
    # -------------------------------------------------
    st.subheader("🚨 Alert Confidence Over Time")
    alerts_df = pd.read_sql("SELECT * FROM alerts", conn)
    if not alerts_df.empty:
        alerts_fig = px.line(
            alerts_df,
            x="timestamp",
            y="confidence",
            markers=True,
            title="Community Alert Confidence Timeline"
        )
        st.plotly_chart(alerts_fig, use_container_width=True)

    # -------------------------------------------------
    # Flood Risk Map
    # -------------------------------------------------
    st.subheader("🗺 Flood Risk Map Across Selected Cities")
    map_df = pd.DataFrame([{
        "City": city["name"],
        "Lat": city["lat"],
        "Lon": city["lon"],
        "Probability": city_data[city["name"]]["flood"]["probability"] if city["name"] in selected_cities else 0
    } for city in cities])
    map_fig = px.scatter_mapbox(
        map_df,
        lat="Lat",
        lon="Lon",
        size="Probability",
        size_max=25,
        color="Probability",
        color_continuous_scale="Reds",
        hover_name="City",
        zoom=4,
        mapbox_style="carto-positron",
        title="Flood Risk Across Selected Cities"
    )
    st.plotly_chart(map_fig, use_container_width=True)
