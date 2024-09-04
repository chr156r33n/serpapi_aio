import streamlit as st
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.title("AIO Content Similarity Checker")

query = st.text_input("Search Query", "bora bora")
locations = st.text_area("Locations (semicolon-separated)", "Austin, Texas, United States; New York, New York, United States; San Francisco, California, United States")
google_domain = st.text_input("Google Domain", "google.com")
gl = st.text_input("GL", "us")
hl = st.text_input("HL", "en")
no_cache = st.checkbox("No Cache", True)
api_key = st.text_input("API Key", "secret_api_key", type="password")
num_calls = st.number_input("Number of API Calls", min_value=1, max_value=10, value=1)

if st.button("Search"):
    url = "https://serpapi.com/search"
    location_list = [location.strip() for location in locations.split(";")]

    all_results = []
    answer_boxes = []
    no_answer_box_indices = []
    for i in range(num_calls):
        params = {
            "engine": "google",
            "q": query,
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
            answer_box = results.get('answer_box')
            if answer_box:
                # Convert answer_box to string
                answer_boxes.append(str(answer_box))
            else:
                no_answer_box_indices.append(i + 1)
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
            break

    if answer_boxes:
        st.write("### Answer Boxes")
        for idx, answer_box in enumerate(answer_boxes):
            st.write(f"**Answer Box {idx + 1}:** {answer_box}\n")

        # Compute similarity
        vectorizer = TfidfVectorizer().fit_transform(answer_boxes)
        vectors = vectorizer.toarray()
        cosine_matrix = cosine_similarity(vectors)

        st.write("### Similarity Matrix")
        st.write(cosine_matrix)
    else:
        st.write("No answer boxes found in the results.")

    if no_answer_box_indices:
        st.write("### Requests with No Answer Box")
        st.write(f"No answer box found in the following requests: {no_answer_box_indices}")
