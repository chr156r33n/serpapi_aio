import streamlit as st
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from collections import Counter

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
    
    # Return default message if no snippets are found
    if not snippets:
        snippets.append("No content available.")
    
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
                organic_results = results.get('organic_results', [])
                raw_html_file = results.get('search_metadata', {}).get('raw_html_file')
                
                if raw_html_file:
                    raw_html_files.append({
                        "keyword": keyword,
                        "location": location_list[i % len(location_list)],
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
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")
                break

        if ai_overviews:
            st.write("### AIO Boxes")
            ai_overview_texts = []
            for idx, ai_overview in enumerate(ai_overviews):
                # Use the new function to extract text and links
                overview_text, references = extract_ai_overview_text_and_links(ai_overview)
                ai_overview_texts.append(overview_text)
                st.write(f"**AIO Box {idx + 1}:** {overview_text}\n")
                
                # Display references
                if references:
                    st.write("**References:**")
                    for ref in references:
                        st.write(f"- [{ref['title']}]({ref['link']})")

            # Compute similarity for AI Overviews
            vectorizer_ai = TfidfVectorizer().fit_transform(ai_overview_texts)
            vectors_ai = vectorizer_ai.toarray()
            cosine_matrix_ai = cosine_similarity(vectors_ai)

            st.write("### AI Overview Similarity Matrix")
            st.write(cosine_matrix_ai)

        else:
            st.write("No AIO boxes found in the results.")

        if organic_results_per_call:
            st.write("### Organic Results")
            all_links = []  # To hold all links for comparison
            for call_results in organic_results_per_call:
                for result in call_results:
                    st.write(f"- **[{result['title']}]({result['link']})**: {result['snippet']}")
                    all_links.append(result['link'])

            # Count occurrences of each URL
            link_counts = Counter(all_links)

            # Create a matrix to show shared vs distinct URLs
            total_calls = len(organic_results_per_call)
            shared_urls = {url: count for url, count in link_counts.items() if count > 1}
            distinct_urls = {url: count for url, count in link_counts.items() if count == 1}

            # Calculate percentages
            shared_count = len(shared_urls)
            distinct_count = len(distinct_urls)
            total_count = shared_count + distinct_count

            if total_count > 0:
                shared_percentage = (shared_count / total_count) * 100
                distinct_percentage = (distinct_count / total_count) * 100
            else:
                shared_percentage = 0
                distinct_percentage = 0

            # Display the results
            st.write("### URL Occurrences in Organic Results")
            st.write(f"- Total URLs: {total_count}")
            st.write(f"- Shared URLs: {shared_count} ({shared_percentage:.2f}%)")
            st.write(f"- Distinct URLs: {distinct_count} ({distinct_percentage:.2f}%)")

            # Display the shared URLs
            if shared_urls:
                st.write("### Shared URLs:")
                for url in shared_urls:
                    st.write(f"- {url}: {link_counts[url]} times")

            # Display the distinct URLs
            if distinct_urls:
                st.write("### Distinct URLs:")
                for url in distinct_urls:
                    st.write(f"- {url}: {link_counts[url]} time")

        # Reference comparison
        if references_per_call:
            st.write("### AI Overview References")
            all_references = []  # To hold all references for comparison
            for call_references in references_per_call:
                for ref in call_references:
                    all_references.append(ref['link'])  # Collecting links from references

            # Count occurrences of each reference link
            reference_counts = Counter(all_references)

            # Create a matrix to show shared vs distinct references
            total_references = len(reference_counts)
            shared_references = {ref: count for ref, count in reference_counts.items() if count > 1}
            distinct_references = {ref: count for ref, count in reference_counts.items() if count == 1}

            # Calculate percentages
            shared_ref_count = len(shared_references)
            distinct_ref_count = len(distinct_references)

            if total_references > 0:
                shared_ref_percentage = (shared_ref_count / total_references) * 100
                distinct_ref_percentage = (distinct_ref_count / total_references) * 100
            else:
                shared_ref_percentage = 0
                distinct_ref_percentage = 0

            # Display the results for references
            st.write("### Reference Occurrences in AI Overviews")
            st.write(f"- Total References: {total_references}")
            st.write(f"- Shared References: {shared_ref_count} ({shared_ref_percentage:.2f}%)")
            st.write(f"- Distinct References: {distinct_ref_count} ({distinct_ref_percentage:.2f}%)")

            # Display the shared references
            if shared_references:
                st.write("### Shared References:")
                for ref in shared_references:
                    st.write(f"- {ref}: {reference_counts[ref]} times")

            # Display the distinct references
            if distinct_references:
                st.write("### Distinct References:")
                for ref in distinct_references:
                    st.write(f"- {ref}: {reference_counts[ref]} time")

        if no_ai_overview_indices:
            st.write("### Requests with No AIO Box")
            st.write(f"No AIO box found in the following requests: {no_ai_overview_indices}")

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
