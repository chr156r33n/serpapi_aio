import streamlit as st
import GoogleSearch

# Streamlit UI for input parameters
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
        search = GoogleSearch(params)
        results = search.get_dict()
        all_results.append(results)

    for idx, results in enumerate(all_results):
        st.write(f"### Results from API Call {idx + 1}")
        for result in results.get('organic_results', []):
            st.write(f"**Title:** {result.get('title')}")
            st.write(f"**Link:** {result.get('link')}")
            st.write(f"**Snippet:** {result.get('snippet')}\n")
            answer_box = result.get('answer_box')
            if answer_box:
                st.write(f"**Answer Box:** {answer_box}\n")
