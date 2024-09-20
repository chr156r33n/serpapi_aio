import streamlit as st
import requests
import time  # Import time for adding delays
import random  # Import random for shuffling
import pandas as pd  # Ensure pandas is imported
import json  # Import json for saving JSON files
from datetime import datetime  # Import datetime for timestamping

st.title("Google Search API with SerpAPI")

keywords = st.text_area("Keywords (semicolon-separated)", "bora bora; skin flooding trend; longevity research")
locations = st.text_area("Locations (semicolon-separated)", "Austin, Texas, United States; New York, New York, United States; San Francisco, California, United States")
google_domain = st.text_input("Google Domain", "google.com")
gl = st.text_input("GL", "us")
hl = st.text_input("HL", "en")
no_cache = st.checkbox("No Cache", True)
api_key = st.text_input("API Key", "secret_api_key", type="password")
num_calls = st.number_input("Number of API Calls per Keyword", min_value=1, max_value=10, value=1)

if st.button("Search"):
    url = "https://serpapi.com/search"
    keyword_list = [keyword.strip() for keyword in keywords.split(";")]
    location_list = [location.strip() for location in locations.split(";")]

    raw_json_files = []  # List to hold raw JSON responses

    for keyword in keyword_list:
        st.write(f"## Results for Keyword: {keyword}")

        # Shuffle the locations for this keyword
        shuffled_locations = location_list.copy()  # Create a copy to shuffle
        random.shuffle(shuffled_locations)

        for i in range(num_calls):
            params = {
                "engine": "google",
                "q": keyword,
                "location": shuffled_locations[i % len(shuffled_locations)],
                "google_domain": google_domain,
                "gl": gl,
                "hl": hl,
                "no_cache": str(no_cache).lower(),
                "api_key": api_key
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()  # Raise an error for bad status codes
                
                # Save the raw JSON response
                json_response = response.json()
                raw_json_files.append(json_response)

                # Save the JSON response to a file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{keyword.replace(' ', '_')}_iteration_{i+1}_{timestamp}.json"
                with open(filename, 'w') as json_file:
                    json.dump(json_response, json_file, indent=4)

                # Optional: Add a delay to avoid hitting rate limits
                time.sleep(1)  # Adjust the delay as needed

            except Exception as e:
                st.error(f"Error for keyword: {keyword}, location: {shuffled_locations[i % len(shuffled_locations)]}, iteration: {i + 1}. {str(e)}")
                continue  # Continue to the next API call

    # Check if raw_json_files is not empty before creating DataFrame
    if raw_json_files:
        df_raw_json = pd.DataFrame(raw_json_files)
        csv_raw_json = df_raw_json.to_csv(index=False)
        
        # Only show the download button once after all API calls
        st.download_button(
            label="Download Raw JSON Responses as CSV",
            data=csv_raw_json,
            file_name='raw_json_responses.csv',
            mime='text/csv',
        )
    else:
        st.warning("No JSON responses were collected.")
