import requests
import streamlit as st
from transformers import pipeline
import json

def fetch_data_from_api(url):
    """
    Fetch data from the API with pagination.

    Args:
        url (str): The API endpoint URL.

    Returns:
        tuple: A tuple containing the data and an error message (if any).
    """
    all_data = []
    page = 1
    while True:
        response = requests.get(f"{url}?page={page}")
        if response.status_code != 200:
            return None, f"Failed to fetch data: {response.status_code}"
        try:
            data = response.json()
        except ValueError:
            return None, "Failed to parse JSON response."
        if 'data' not in data or 'data' not in data['data']:
            return None, "Unexpected data format."
        page_data = data['data']['data']
        if not page_data:
            break
        all_data.extend(page_data)
        page += 1
    return all_data, None

def load_summarizer():
    """
    Load the summarizer model.

    Returns:
        pipeline: The loaded summarization pipeline.
    """
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_context(context, summarizer):
    """
    Summarize context using Hugging Face model.

    Args:
        context (str): The text to summarize.
        summarizer (pipeline): The summarization pipeline.

    Returns:
        str: The summarized text.
    """
    summary = summarizer(context, max_length=60, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def process_data(api_url):
    """
    Process data from the API.

    Args:
        api_url (str): The API endpoint URL.

    Returns:
        tuple: A tuple containing the results and an error message (if any).
    """
    summarizer = load_summarizer()
    data, error = fetch_data_from_api(api_url)
    if error:
        return None, error
    
    results = []
    for item in data[:5]:
        if not isinstance(item, dict):
            continue  # Skip items with unexpected format
        response_text = item.get('response', '')
        sources = item.get('source', [])
        if not isinstance(sources, list):
            continue  # Skip items with unexpected source format
        summarized_sources = []
        for source in sources:
            context = source.get('context', '')
            link = source.get('link', '')
            if context:
                summarized_context = summarize_context(context, summarizer)
                summarized_sources.append({
                    'id': source['id'],
                    'context': summarized_context,
                    'link': link
                })
        results.append({'response': response_text, 'source': summarized_sources})
    return results, None

# Streamlit UI
st.title('API Citation Finder')
api_url = st.text_input('Enter the API URL:', 'https://devapi.beyondchats.com/api/get_message_with_sources')

if st.button('Fetch and Process Data'):
    try:
        with st.spinner('Fetching data...'):
            results, error = process_data(api_url)
        
        if error:
            st.error(error)
        else:
            table_data = []
            if results:
                first_result = results[0]
                response = first_result['response']
                sources = first_result['source']
                sources_str = ', '.join([
                    f"'id': {source['id']}, 'context': {source['context']}, 'link': {source['link']}"
                    for source in sources
                ])
                table_data.append({'Response': response, 'Source': sources_str})

            st.success('Data processed successfully!')
            st.write("Citations with links:")
            
            citations = []
            for citation in first_result['source']:
                if 'link' in citation and citation['link']:
                    citations.append({'id': citation['id'], 'link': citation['link']})
            st.json(citations)

            with open('cached_data.json', 'w') as f:
                json.dump(table_data, f)
            
            st.write("Processed Data:")
            st.table(table_data)

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
    except ValueError as e:
        st.error(f"JSON decoding failed: {e}")
