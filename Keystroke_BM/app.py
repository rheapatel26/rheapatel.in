import time
import numpy as np
import streamlit as st
from pymongo import MongoClient
from pynput import keyboard

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["keystrokeRrofil23RRRhearofi"]
collection = db["user_profiles"]

# Global variables for keystroke collection
keystroke_data = []
current_input = []
press_times = {}

# Configurations
st.set_page_config(page_title="Keystroke Authentication", layout="centered")
st.title("🔑 Keystroke Dynamics Authentication with MongoDB")

# User Input
username = st.sidebar.text_input("Enter Username:")
mode = st.sidebar.radio("Choose Mode:", ["Register (Train Model)", "Authenticate"])
password_input = st.sidebar.text_input("Enter Password (for registration only)", type="password")

NUM_TRAINING_SAMPLES = 5

# Keystroke Event Handlers
def on_press(key):
    """ Record key press time """
    try:
        if hasattr(key, 'char') and key.char:
            press_times[key.char] = time.time()
    except AttributeError:
        pass

def on_release(key):
    """ Record key release time & compute hold/interkey time """
    try:
        if hasattr(key, 'char') and key.char:
            release_time = time.time()
            hold_time = release_time - press_times[key.char]

            if current_input:
                interkey_time = press_times[key.char] - current_input[-1][1]
            else:
                interkey_time = 0

            current_input.append((key.char, release_time, hold_time, interkey_time))

            # Check if full password is typed
            if "".join([char[0] for char in current_input]) == password_input:
                keystroke_data.append(current_input.copy())
                current_input.clear()

                if len(keystroke_data) >= NUM_TRAINING_SAMPLES:
                    return False  # Stop listener
    except AttributeError:
        pass

def collect_training_data():
    """ Collect real-time keystroke data for registration """
    st.write(f"Type '{password_input}' {NUM_TRAINING_SAMPLES} times for registration.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def calculate_master_vector():
    """ Compute master vector & standard deviation vector dynamically """
    all_features = []
    for sample in keystroke_data:
        features = [data[2:] for data in sample]  # Extract hold time & interkey time
        all_features.append(np.array(features).flatten())

    master_vector = np.mean(all_features, axis=0).tolist()
    std_vector = np.std(all_features, axis=0).tolist()

    return master_vector, std_vector

def save_to_mongodb(username, master_vector, std_vector, password):
    """ Save dynamically collected user profile to MongoDB """
    user_data = {
        "username": username,
        "password": password,  # Store hashed password in real-world apps
        "master_vector": master_vector,
        "std_vector": std_vector
    }
    collection.update_one({"username": username}, {"$set": user_data}, upsert=True)

def get_user_profile(username):
    """ Retrieve user profile from MongoDB """
    user_profile = collection.find_one({"username": username})
    if user_profile:
        return user_profile["password"], np.array(user_profile["master_vector"]), np.array(user_profile["std_vector"])
    return None, None, None

def authenticate_user(master_vector, std_vector, expected_password):
    """ Authenticate user based on typing pattern """
    global current_input
    current_input.clear()
    
    st.write("🔹 Type your password for authentication:")

    def auth_on_release(key):
        global current_input
        try:
            if hasattr(key, 'char') and key.char:
                release_time = time.time()
                hold_time = release_time - press_times[key.char]

                if current_input:
                    interkey_time = press_times[key.char] - current_input[-1][1]
                else:
                    interkey_time = 0

                current_input.append((key.char, release_time, hold_time, interkey_time))

                # Check if full password is typed
                if "".join([char[0] for char in current_input]) == expected_password:
                    features = np.array([data[2:] for data in current_input]).flatten()
                    current_input.clear()

                    # Compute Euclidean distance with standard deviation weighting
                    weighted_diff = (features - master_vector) / std_vector
                    distance = np.linalg.norm(weighted_diff)

                    threshold = 2.5  # Adjust threshold for strictness

                    if distance < threshold:
                        st.success("✅ Authentication Successful!")
                    else:
                        st.error("❌ Authentication Failed! Typing pattern does not match.")
                    
                    return False  # Stop listener
        except AttributeError:
            pass

    with keyboard.Listener(on_press=on_press, on_release=auth_on_release) as listener:
        listener.join()

# Streamlit UI Logic
if mode == "Register (Train Model)":
    if st.button("Start Training"):
        if username and password_input:
            keystroke_data.clear()
            collect_training_data()
            master_vector, std_vector = calculate_master_vector()
            save_to_mongodb(username, master_vector, std_vector, password_input)
            st.success(f"🎉 Training Complete! Profile saved for {username}.")
        else:
            st.warning("⚠️ Please enter a username and password.")

elif mode == "Authenticate":
    if username:
        stored_password, master_vector, std_vector = get_user_profile(username)
        if master_vector is not None:
            auth_password = st.text_input("Enter your password to authenticate:", type="password")
            if st.button("Start Authentication"):
                if auth_password == stored_password:
                    authenticate_user(master_vector, std_vector, stored_password)
                else:
                    st.error("❌ Incorrect password.")
        else:
            st.warning("⚠️ No profile found! Please register first.")
    else:
        st.warning("⚠️ Please enter a username.")
