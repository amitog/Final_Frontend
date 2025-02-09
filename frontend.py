import logging
import streamlit as st
import requests
import time

# Suppress Streamlit duplicate key errors
logging.getLogger("streamlit").setLevel(logging.CRITICAL)

# Hide Streamlit error messages
st.markdown(
    """
    <style>
    .stException { display: none; }
    </style>
    """,
    unsafe_allow_html=True
)

# API URL - Change if Flask is running on a different machine
BASE_URL = "https://final-backend-35fg.onrender.com"

# Title
st.title("🌱 Fertilizer & Irrigation Monitoring System")

# Sidebar for live sensor data
st.sidebar.header("📡 Live Sensor Data")

# Function to fetch sensor data
def get_sensor_data():
    try:
        response = requests.get(f"{BASE_URL}/get_sensor_data", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

# Function to fetch irrigation state
def get_irrigation_state():
    try:
        response = requests.get(f"{BASE_URL}/get_irrigation_state", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

# Function to toggle irrigation state
def toggle_irrigation(state):
    try:
        response = requests.post(f"{BASE_URL}/set_irrigation_state", json={"state": state}, timeout=5)
        return response.status_code == 200
    except:
        return False

# Display live sensor data and irrigation state
sensor_placeholder = st.sidebar.empty()
irrigation_placeholder = st.sidebar.empty()
button_placeholder = st.sidebar.empty()

# Sidebar function to update UI
def update_sidebar():
    sensor_data = get_sensor_data()
    irrigation_data = get_irrigation_state()

    # Display sensor data (Default text if API fails)
    sensor_text = (
        f"**🌡 Temperature:** {sensor_data['temperature']} °C  \n"
        f"**💧 Humidity:** {sensor_data['humidity']} %  \n"
        f"**🌿 Soil Moisture:** {sensor_data['soil_moisture']} %"
        if sensor_data else "📊 Sensor Data Unavailable"
    )
    sensor_placeholder.write(sensor_text)

    # Display irrigation status (Default text if API fails)
    if irrigation_data:
        irrigation_state = irrigation_data.get("irrigation_state", False)
        status = "💦 ON ✅" if irrigation_state else "❌ OFF"
        irrigation_placeholder.write(f"**🚰 Irrigation System:** {status}")

        # Toggle button with a unique key
        toggle_state = "OFF" if irrigation_state else "ON"
        if st.sidebar.button(f"Turn Irrigation {toggle_state}", key=f"toggle_{toggle_state}"):
            new_state = not irrigation_state  # Toggle the state
            if toggle_irrigation(new_state):
                st.sidebar.success(f"🚰 Irrigation system turned {toggle_state}")
                update_sidebar()  # Refresh sidebar after toggle
    else:
        irrigation_placeholder.write("🚰 Irrigation Status Unavailable")


# Initially update the sidebar
update_sidebar()

# Soil & Crop Information Form
st.header("🌾 Soil & Crop Information")
with st.form("soil_crop_form"):
    nitrogen = st.number_input("🧪 Nitrogen Level", min_value=0, max_value=100, value=10)
    potassium = st.number_input("🧪 Potassium Level", min_value=0, max_value=100, value=10)
    phosphorous = st.number_input("🧪 Phosphorous Level", min_value=0, max_value=100, value=10)
    
    soil_type = st.selectbox("🌱 Soil Type", ["Sandy", "Loamy", "Clayey", "Peaty", "Saline", "Chalky", "Silty"])
    crop_type = st.selectbox("🌾 Crop Type", ["Wheat", "Rice", "Maize", "Barley", "Sugarcane", "Cotton", "Vegetables"])
    
    submitted = st.form_submit_button("🚀 Predict Fertilizer")

if submitted:
    payload = {
        "nitrogen": nitrogen,
        "potassium": potassium,
        "phosphorous": phosphorous,
        "soilType": soil_type,
        "cropType": crop_type
    }

    try:
        response = requests.post(f"{BASE_URL}/process_data", json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            predicted_fertilizer = result.get("Predicted Fertilizer", "No fertilizer prediction available")
            
            # Use if-else to display fertilizer details based on the predicted fertilizer
            if predicted_fertilizer == "10-26-26":
                fertilizer_details = "10% Nitrogen (N), 26% Phosphorus (P), 26% Potassium (K) - Ideal for crops needing strong root growth and overall health."
            elif predicted_fertilizer == "14-35-14":
                fertilizer_details = "14% Nitrogen (N), 35% Phosphorus (P), 14% Potassium (K) - Best for early plant growth, root development, and flower formation."
            elif predicted_fertilizer == "17-17-17":
                fertilizer_details = "17% Nitrogen (N), 17% Phosphorus (P), 17% Potassium (K) - A balanced fertilizer suitable for a wide range of crops."
            elif predicted_fertilizer == "20-20":
                fertilizer_details = "20% Nitrogen (N), 20% Potassium (K) - Designed for plants needing nitrogen and potassium but little phosphorus."
            elif predicted_fertilizer == "28-28":
                fertilizer_details = "28% Nitrogen (N), 28% Potassium (K) - High in nitrogen and potassium for rapid growth and stress tolerance."
            elif predicted_fertilizer == "DAP":
                fertilizer_details = "18% Nitrogen (N), 46% Phosphorus (P) - Ideal for root development and flowering."
            elif predicted_fertilizer == "Urea":
                fertilizer_details = "46% Nitrogen (N) - Promotes leaf and vegetative growth."
            else:
                fertilizer_details = "No details available for the predicted fertilizer."

            st.success(f"Predicted Fertilizer: {predicted_fertilizer}")
            st.info(f"Fertilizer Details: {fertilizer_details}")
        else:
            st.error("Error from backend")
    except Exception as e:
        st.error(f"Request failed: {e}")

# Real-time updates: Refresh every 3 seconds
while True:
    update_sidebar()
    time.sleep(3)
