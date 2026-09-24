import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000"

st.set_page_config(
    page_title="NUTRIGEN-AI",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 NUTRIGEN-AI")
st.subheader("Personalized Nutrition & Diet Optimization")

st.write(
    "Enter your information below to generate a personalized nutrition plan."
)

st.divider()

st.header("Personal Information")

name = st.text_input("Name")

age = st.number_input(
    "Age",
    min_value=1,
    max_value=120,
    value=20
)

height = st.number_input(
    "Height (cm)",
    min_value=50.0,
    max_value=250.0,
    value=170.0
)

weight = st.number_input(
    "Weight (kg)",
    min_value=10.0,
    max_value=300.0,
    value=60.0
)

activity = st.selectbox(
    "Activity Level",
    [
        "Sedentary",
        "Lightly Active",
        "Moderately Active",
        "Very Active"
    ]
)

goal = st.selectbox(
    "Goal",
    [
        "Maintain Weight",
        "Weight Loss",
        "Weight Gain"
    ]
)

diet = st.selectbox(
    "Diet Preference",
    [
        "Vegetarian",
        "Non-Vegetarian",
        "Vegan"
    ]
)

st.divider()

if st.button("Generate Nutrition Plan"):

    try:
        response = requests.get(
            f"{API_URL}/api/health"
        )

        if response.status_code == 200:

            st.success("REST API connected successfully!")

            st.write("### Your Information")

            st.write(f"Name: {name}")
            st.write(f"Age: {age}")
            st.write(f"Height: {height} cm")
            st.write(f"Weight: {weight} kg")
            st.write(f"Activity Level: {activity}")
            st.write(f"Goal: {goal}")
            st.write(f"Diet Preference: {diet}")

        else:

            st.error("REST API returned an unexpected response.")

    except requests.exceptions.ConnectionError:

        st.error(
            "Could not connect to the REST API. "
            "Make sure Flask is running."
        )