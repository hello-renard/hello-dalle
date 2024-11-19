import streamlit as st
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO
import os
import json

DB_FILE = 'db.json'

def main():
    client = OpenAI(api_key=st.session_state.openai_api_key)
    st.title('DALL-E 3 Text-to-Image Generator')
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
          size="512x512",
          quality="hd",
          style="natural",
          n=4,
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
                st.image(message["content"], use_column_width=True)


if __name__ == '__main__':

    if 'openai_api_key' in st.session_state and st.session_state.openai_api_key:
        main()
    
    else:

        # if the DB_FILE not exists, create it
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, 'w') as file:
                db = {
                    'openai_api_keys': [],
                }
                json.dump(db, file)
        # load the database
        else:
            with open(DB_FILE, 'r') as file:
                db = json.load(file)

        # display the selectbox from db['openai_api_keys']
        selected_key = st.selectbox(
            label = "Existing OpenAI API Keys", 
            options = db['openai_api_keys']
        )

        # a text input box for entering a new key
        new_key = st.text_input(
            label="New OpenAI API Key", 
            type="password"
        )

        login = st.button("Login")

        # if new_key is given, add it to db['openai_api_keys']
        # if new_key is not given, use the selected_key
        if login:
            if new_key:
                db['openai_api_keys'].append(new_key)
                with open(DB_FILE, 'w') as file:
                    json.dump(db, file)
                st.success("Key saved successfully.")
                st.session_state['openai_api_key'] = new_key
                st.rerun()
            else:
                if selected_key:
                    st.success(f"Logged in with key '{selected_key}'")
                    st.session_state['openai_api_key'] = selected_key
                    st.rerun()
                else:
                    st.error("API Key is required to login")

                    
