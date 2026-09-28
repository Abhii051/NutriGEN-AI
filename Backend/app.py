import streamlit as st

st.set_page_config(
    page_title="NUTRIGEN-AI",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 NUTRIGEN-AI")
st.subheader("Personalized Nutrition & Diet Optimization")

st.write(
    "Enter your details below to generate a personalized nutrition plan."
)

st.divider()

st.header("👤 Personal Information")

name = st.text_input("Name")

age = st.number_input(
    "Age",
    min_value=1,
    max_value=120,
    value=20
)

gender = st.selectbox(
    "Gender",
    ["Male", "Female"]
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

st.header("🏃 Activity & Goal")

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

st.header("🥗 Food Preference")

diet = st.selectbox(
    "Diet Preference",
    [
        "Vegetarian",
        "Non-Vegetarian",
        "Vegan"
    ]
)

if st.button("Generate Nutrition Plan"):
    st.success("Your information has been received!")