import streamlit as st
import requests
import time  # Import time for adding delays
import random  # Import random for shuffling
import json  # Import json for saving JSON files
from datetime import datetime  # Import datetime for timestamping
import os  # Import os for file operations
import zipfile  # Import zipfile for creating zip files

st.title("Google Search API with SerpAPI")

# Option to enter keywords or upload a file
keywords_input = st.text_area("Keywords (semicolon-separated)", "bora bora; skin flooding trend; longevity research")
uploaded_file = st.file_uploader("Or upload a text file with one keyword per line", type=["txt"])

# Process uploaded file if it exists
if uploaded_file is not None:
    keywords_input = uploaded_file.read().decode("utf-8").strip()  # Read and decode the file content

# Split keywords from the input
keyword_list = [keyword.strip() for keyword in keywords_input.split(";") if keyword.strip()]

locations = st.text_area("Locations (semicolon-separated)", "Austin, Texas, United States; New York, New York, United States; San Francisco, California, United States")
google_domain = st.text_input("Google Domain", "google.com")
gl = st.text_input("GL", "us")
hl = st.text_input("HL", "en")
no_cache = st.checkbox("No Cache", True)
api_key = st.text_input("API Key", "secret_api_key", type="password")
num_calls = st.number_input("Number of API Calls per Keyword", min_value=1, max_value=10, value=1)

if st.button("Search"):
    url = "https://serpapi.com/search"
    location_list = [location.strip() for location in locations.split(";")]

    json_files = []  # List to hold filenames of saved JSON files

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
                
                # Save the raw JSON response to a file
                json_response = response.json()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{keyword.replace(' ', '_')}_iteration_{i+1}_{timestamp}.json"
                with open(filename, 'w') as json_file:
                    json.dump(json_response, json_file, indent=4)
                
                json_files.append(filename)  # Add filename to the list

                # Optional: Add a delay to avoid hitting rate limits
                time.sleep(1)  # Adjust the delay as needed

            except Exception as e:
                st.error(f"Error for keyword: {keyword}, location: {shuffled_locations[i % len(shuffled_locations)]}, iteration: {i + 1}. {str(e)}")
                continue  # Continue to the next API call

    # Create a zip file containing all JSON files
    zip_filename = "json_responses.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for json_file in json_files:
            zipf.write(json_file)
            os.remove(json_file)  # Optionally remove the JSON file after zipping

    # Provide a download link for the zip file
    with open(zip_filename, 'rb') as f:
        st.download_button(
            label="Download JSON Files as Zip",
            data=f,
            file_name=zip_filename,
            mime='application/zip',
        )

    st.success("All API calls completed and JSON files saved.")
