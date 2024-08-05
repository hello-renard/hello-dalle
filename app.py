import streamlit as st
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO
import os
import json

API_KEYS_FILE = 'api_keys.json'

def save_api_key(key_name, key_value):
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE, 'r') as file:
            keys = json.load(file)
    else:
        keys = {}
    keys[key_name] = key_value
    with open(API_KEYS_FILE, 'w') as file:
        json.dump(keys, file)

def load_api_keys():
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE, 'r') as file:
            keys = json.load(file)
        return keys
    return {}

st.sidebar.header('Your OpenAI API Key:')
keys = load_api_keys()
api_key_name = st.sidebar.selectbox("Existing API Key", list(keys.keys()))
new_key_name = st.sidebar.text_input("New Key Name")
new_key_value = st.sidebar.text_input("New Key Value", type="password")
if st.sidebar.button("Save New Key"):
    if new_key_name and new_key_value:
        save_api_key(new_key_name, new_key_value)
        st.sidebar.success(f"Key '{new_key_name}' saved successfully.")
        st.rerun()
    else:
        st.sidebar.error("Both Key Name and Value are required")

if api_key_name:
    client = OpenAI(api_key=keys[api_key_name])

    st.title('DALL-E 3 Image Generator')
    prompt = st.chat_input('Enter your prompt')

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if prompt:
        # Append user's prompt to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Concatenate all previous prompts
        all_prompts = " ".join([message["content"] for message in st.session_state.chat_history if message["role"] == "user"])

        response = client.images.generate(
          model="dall-e-3",
          prompt=all_prompts,
          size="1024x1024",
          quality="standard",
          n=1,
        )

        image_url = response.data[0].url
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))

        # Append generated image to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": img})

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if isinstance(message["content"], str):
                st.markdown(message["content"])
            else:  # message is an image
                st.image(message["content"], caption='Generated Image', use_column_width=True)
else:
    st.error('Please provide an OpenAI API Key')