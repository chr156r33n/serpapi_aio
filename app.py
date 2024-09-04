    import streamlit as st
    from serpapi import GoogleSearch

    st.title("Google Search API with SerpAPI")

    # Test the import and basic functionality
    try:
        params = {
            "engine": "google",
            "q": "test",
            "api_key": "secret_api_key"
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        st.write("SerpAPI import and call successful!")
    except Exception as e:
        st.write(f"Error: {e}")
