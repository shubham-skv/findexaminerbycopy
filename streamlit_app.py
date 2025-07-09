import streamlit as st
import requests
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set the page configuration
st.set_page_config(page_title="BTE Exam Marks Lookup ", layout="centered")

st.title("BTE Exam Marks Lookup BY SKV")
st.markdown("Enter a list of Copy Numbers below (one per line) to retrieve exam marks details.")

# Input field for multiple Bar_Codes
bar_codes_input = st.text_area(
    "Enter Copy Numbers (one per line)",
    height=200,
    help="e.g.,\n4102016023\n4102016024\n4102016025"
)

# Function to fetch marks for a single bar code
def fetch_marks(bar_code, url):
    payload = {
        "Checked_Type": "EVAL",
        "Eval_Session": "MAY 2025",
        "Bar_Code": bar_code
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        if data:
            # Assuming the API returns a list, even if it's just one item for the barcode
            return bar_code, data, None # Return bar_code, data, and no error
        else:
            return bar_code, None, f"No data found for Bar Code: {bar_code}"
    except requests.exceptions.Timeout:
        return bar_code, None, f"Request timed out for Bar Code: {bar_code}"
    except requests.exceptions.RequestException as e:
        return bar_code, None, f"Error connecting to API for {bar_code}: {e}"
    except json.JSONDecodeError:
        return bar_code, None, f"Error decoding JSON for {bar_code}. Response might not be valid JSON."
    except Exception as e:
        return bar_code, None, f"An unexpected error occurred for {bar_code}: {e}"

# Button to trigger the request
if st.button("Get Marks Details"):
    if bar_codes_input:
        # Split the input by new lines and clean up empty lines/whitespace
        bar_codes = [bc.strip() for bc in bar_codes_input.split('\n') if bc.strip()]

        if not bar_codes:
            st.warning("No valid Bar Codes entered. Please enter at least one.")
            st.stop()

        url = "https://bteexam.com/Admin/Copy_Marks"

        # Use a placeholder for the status message
        status_placeholder = st.empty()
        status_placeholder.info(f"Sending requests for {len(bar_codes)} Bar Codes... Please wait.")

        results = []
        errors = []

        # Use ThreadPoolExecutor for concurrent requests
        # Max workers can be adjusted based on network conditions and API limits
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks for each barcode
            future_to_barcode = {executor.submit(fetch_marks, bc, url): bc for bc in bar_codes}

            for future in as_completed(future_to_barcode):
                bar_code_processed = future_to_barcode[future]
                try:
                    bar_code, data, error = future.result()
                    if error:
                        errors.append(error)
                    elif data:
                        for item in data:
                            results.append({
                                "Bar Code": item.get('Bar_Code', 'N/A'),
                                "Center Name": item.get('Center_Name', 'N/A'),
                                "Faculty Name": item.get('Name', 'N/A'),
                                "Contact No.": item.get('Contact_No', 'N/A'),
                                "Catch No.": item.get('Catch_No', 'N/A'),
                                "Paper Name": item.get('Paper_Name', 'N/A'),
                                "Evaluation Session": item.get('Eval_Session', 'N/A'),
                                "Checked Type": item.get('Checked_Type', 'N/A'),
                                "Checked": 'Yes' if item.get('Checked') else 'No',
                                "Total Marks": item.get('Total_Marks', 'N/A'),
                                "Obtained Marks": item.get('Obt_Marks', 'N/A')
                            })
                except Exception as exc:
                    errors.append(f"An unexpected error occurred while processing {bar_code_processed}: {exc}")

        # Clear the status message placeholder
        status_placeholder.empty()

        if results:
            st.success("Details Retrieved Successfully for the entered Bar Codes!")
            df = pd.DataFrame(results)
            st.dataframe(df)
        else:
            st.warning("No data could be retrieved for any of the provided Bar Codes.")

        if errors:
            st.error("Errors occurred during processing:")
            for error_msg in errors:
                st.write(f"- {error_msg}")
    else:
        st.warning("Please enter Bar Codes to proceed.")

st.markdown("---")
st.caption("Developed with Streamlit and Python.")
