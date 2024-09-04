import streamlit as st
import requests

st.title("Google Search API with SerpAPI")

query = st.text_input("Search Query", "bora bora")
api_key = st.text_input("API Key", "secret_api_key", type="password")

if st.button("Search"):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key
    }

    try:
        response = requests.get(url, params=params)
        results = response.json()
        st.write(results)
    except Exception as e:
        st.write(f"Error: {e}")
