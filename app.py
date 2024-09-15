import streamlit as st
import requests
from collections import Counter
import time  # Import time for adding delays
import random  # Import random for shuffling
import pandas as pd  # Ensure pandas is imported

st.title("Google Search API with SerpAPI")

keywords = st.text_area("Keywords (semicolon-separated)", "bora bora; skin flooding trend; longevity research")
locations = st.text_area("Locations (semicolon-separated)", "Austin, Texas, United States; New York, New York, United States; San Francisco, California, United States")
google_domain = st.text_input("Google Domain", "google.com")
gl = st.text_input("GL", "us")
hl = st.text_input("HL", "en")
no_cache = st.checkbox("No Cache", True)
api_key = st.text_input("API Key", "secret_api_key", type="password")
num_calls = st.number_input("Number of API Calls per Keyword", min_value=1, max_value=10, value=1)

def extract_ai_overview_text_and_links(ai_overview):
    """Extracts text snippets and references from the ai_overview JSON structure."""
    snippets = []
    references = []
    
    for block in ai_overview.get('text_blocks', []):
        if 'type' in block:
            if block['type'] == 'paragraph' and 'snippet' in block:
                snippets.append(block['snippet'])
            elif block['type'] == 'list' and 'list' in block:
                for item in block['list']:
                    if 'snippet' in item:
                        snippets.append(item['snippet'])
    
    for reference in ai_overview.get('references', []):
        references.append({
            "title": reference.get('title', 'No title available'),
            "link": reference.get('link', '#')
        })
    
    return ' '.join(snippets), references

def extract_organic_results(organic_results):
    """Extracts titles and snippets from organic results."""
    results = []
    for result in organic_results:
        results.append({
            "title": result['title'],
            "snippet": result['snippet'],
            "link": result['link']
        })
    return results

if st.button("Search"):
    url = "https://serpapi.com/search"
    keyword_list = [keyword.strip() for keyword in keywords.split(";")]
    location_list = [location.strip() for location in locations.split(";")]

    combined_similarity_data = []
    raw_html_files = []

    for keyword in keyword_list:
        st.write(f"## Results for Keyword: {keyword}")
        all_results = []
        ai_overviews = []
        organic_results_per_call = []  # List to hold organic results for each API call
        references_per_call = []  # List to hold references for each API call
        no_ai_overview_indices = []

        # Shuffle the locations for this keyword
        shuffled_locations = location_list.copy()  # Create a copy to shuffle
        random.shuffle(shuffled_locations)

        for i in range(num_calls):
            # Use the shuffled location for each API call
            params = {
                "engine": "google",
                "q": keyword,
                "location": shuffled_locations[i % len(shuffled_locations)],  # Use the current location in order
                "google_domain": google_domain,
                "gl": gl,
                "hl": hl,
                "no_cache": str(no_cache).lower(),
                "api_key": api_key
            }

            # Debugging: Print the parameters being sent
            st.write(f"Making API call with parameters: {params}")

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()  # Raise an error for bad status codes
                
                # Log the full response content for debugging
                st.write(f"Response Status Code: {response.status_code}")
                st.write(f"Response Content: {response.text}")

                # Check if the response content is empty
                if not response.content:
                    st.error("Error: Received an empty response from the API.")
                    continue
                
                results = response.json()  # Attempt to parse the JSON response
                all_results.append(results)
                ai_overview = results.get('ai_overview')
                organic_results = results.get('organic_results', [])
                raw_html_file = results.get('search_metadata', {}).get('raw_html_file')
                
                if raw_html_file:
                    raw_html_files.append({
                        "keyword": keyword,
                        "location": shuffled_locations[i % len(shuffled_locations)],
                        "raw_html_file": raw_html_file
                    })
                
                if ai_overview:
                    ai_overviews.append(ai_overview)
                    # Extract references and store them for this call
                    _, references = extract_ai_overview_text_and_links(ai_overview)
                    references_per_call.append(references)
                else:
                    no_ai_overview_indices.append(i + 1)

                # Extract organic results and store them for this call
                organic_results_per_call.append(extract_organic_results(organic_results))
                
                # Optional: Add a delay to avoid hitting rate limits
                time.sleep(1)  # Adjust the delay as needed

            except requests.exceptions.RequestException as e:
                st.error(f"Request Error: {e} for keyword: {keyword}, location: {shuffled_locations[i % len(shuffled_locations)]}, iteration: {i + 1}")
                continue  # Continue to the next API call
            except ValueError as e:
                st.error(f"JSON Parsing Error: {e} for keyword: {keyword}, location: {shuffled_locations[i % len(shuffled_locations)]}, iteration: {i + 1}")
                continue  # Continue to the next API call
            except Exception as e:
                st.error(f"Unexpected Error: {e} for keyword: {keyword}, location: {shuffled_locations[i % len(shuffled_locations)]}, iteration: {i + 1}")
                continue  # Continue to the next API call

    # Check if raw_html_files is not empty before creating DataFrame
    if raw_html_files:
        df_raw_html = pd.DataFrame(raw_html_files)
        csv_raw_html = df_raw_html.to_csv(index=False)
        st.download_button(
            label="Download Raw HTML Files as CSV",
            data=csv_raw_html,
            file_name='raw_html_files.csv',
            mime='text/csv',
        )
    else:
        st.warning("No raw HTML files were collected.")

    # Process organic results and references as needed
    # ... rest of the code for processing organic results and references ...
