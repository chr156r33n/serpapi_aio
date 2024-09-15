import streamlit as st
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

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

    combined_similarity_data = []
    raw_html_files = []

    for keyword in keyword_list:
        st.write(f"## Results for Keyword: {keyword}")
        all_results = []
        ai_overviews = []
        no_ai_overview_indices = []
        for i in range(num_calls):
            params = {
                "engine": "google",
                "q": keyword,
                "location": location_list[i % len(location_list)],  # Rotate through location values
                "google_domain": google_domain,
                "gl": gl,
                "hl": hl,
                "no_cache": str(no_cache).lower(),
                "api_key": api_key
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()  # Raise an error for bad status codes
                results = response.json()
                all_results.append(results)
                ai_overview = results.get('ai_overview')
                raw_html_file = results.get('search_metadata', {}).get('raw_html_file')
                if raw_html_file:
                    raw_html_files.append({
                        "keyword": keyword,
                        "location": location_list[i % len(location_list)],
                        "raw_html_file": raw_html_file
                    })
                if ai_overview:
                    # Convert ai_overview to string
                    ai_overviews.append(str(ai_overview))
                else:
                    no_ai_overview_indices.append(i + 1)
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")
                break

        if ai_overviews:
            st.write("### Answer Boxes")
            for idx, ai_overview in enumerate(ai_overviews):
                st.write(f"**Answer Box {idx + 1}:** {ai_overview}\n")

            # Compute similarity
            vectorizer = TfidfVectorizer().fit_transform(ai_overviews)
            vectors = vectorizer.toarray()
            cosine_matrix = cosine_similarity(vectors)

            st.write("### Similarity Matrix")
            st.write(cosine_matrix)

            # Combine similarity data
            for row_idx, row in enumerate(cosine_matrix):
                combined_similarity_data.append({
                    "keyword": keyword,
                    "location": location_list[row_idx % len(location_list)],
                    **{f"similarity_{col_idx + 1}": value for col_idx, value in enumerate(row)}
                })
        else:
            st.write("No answer boxes found in the results.")

        if no_ai_overview_indices:
            st.write("### Requests with No Answer Box")
            st.write(f"No answer box found in the following requests: {no_ai_overview_indices}")

    # Export combined similarity matrix
    if combined_similarity_data:
        df_similarity = pd.DataFrame(combined_similarity_data)
        csv_similarity = df_similarity.to_csv(index=False)
        st.download_button(
            label="Download Combined Similarity Matrix as CSV",
            data=csv_similarity,
            file_name='combined_similarity_matrix.csv',
            mime='text/csv',
        )

    # Display and export raw HTML files
    if raw_html_files:
        st.write("### Raw HTML Files")
        for entry in raw_html_files:
            st.write(f"Keyword: {entry['keyword']}, Location: {entry['location']}, [Raw HTML File]({entry['raw_html_file']})")

        df_raw_html = pd.DataFrame(raw_html_files)
        csv_raw_html = df_raw_html.to_csv(index=False)
        st.download_button(
            label="Download Raw HTML Files as CSV",
            data=csv_raw_html,
            file_name='raw_html_files.csv',
            mime='text/csv',
        )
