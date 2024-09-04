import streamlit as st
import requests

st.title("Google Search API with SerpAPI")

query = st.text_input("Search Query", "bora bora")
location = st.text_input("Location", "United States")
google_domain = st.text_input("Google Domain", "google.com")
gl = st.text_input("GL", "us")
hl = st.text_input("HL", "en")
no_cache = st.checkbox("No Cache", True)
api_key = st.text_input("API Key", "secret_api_key", type="password")
num_calls = st.number_input("Number of API Calls", min_value=1, max_value=10, value=1)

if st.button("Search"):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "location": location,
        "google_domain": google_domain,
        "gl": gl,
        "hl": hl,
        "no_cache": str(no_cache).lower(),
        "api_key": api_key
    }

    all_results = []
    for _ in range(num_calls):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an error for bad status codes
            results = response.json()
            all_results.append(results)
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
            break

    for idx, results in enumerate(all_results):
        st.write(f"### Results from API Call {idx + 1}")
        answer_box = results.get('answer_box')
        if answer_box:
            st.write(f"**Answer Box:** {answer_box}\n")
        else:
            st.write("No answer box found in this result.")
