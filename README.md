# Python-API-Citation-Finder

This project fetches data from an API endpoint, processes it to extract and summarize sources, and displays the results using Streamlit.

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/DenisMahajan/Python-API-Citation-Finder.git
    cd Python-API-Citation-Finder
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the Streamlit app:
    ```bash
    streamlit run app1.py
    ```

2. And click "Fetch and Process Data".

## Edge Cases

- The script handles non-200 responses from the API.
- The script handles invalid JSON responses.
- The script skips items with unexpected data formats.
