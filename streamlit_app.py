import streamlit as st
import requests
import json

# Set the page configuration
st.set_page_config(page_title="BTE Exam Marks Lookup ", layout="centered")

st.title("BTE Exam Marks Lookup BY SKV")
st.markdown("Enter the Bar Code below to retrieve exam marks details.")

# Input field for Bar_Code
bar_code_input = st.text_input("Enter Bar Code", help="e.g., 4102016023")

# Button to trigger the request
if st.button("Get Marks Details"):
    if bar_code_input:
        # Define the API endpoint
        url = "https://bteexam.com/Admin/Copy_Marks"

        # Define the request body
        payload = {
            "Checked_Type": "EVAL",
            "Eval_Session": "MAY 2025",
            "Bar_Code": bar_code_input
        }

        st.info("Sending request... Please wait.")

        try:
            # Send the POST request
            # Using json=payload automatically sets Content-Type to application/json
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            # Parse the JSON response
            data = response.json()

            if data:
                st.success("Details Retrieved Successfully!")
                # Display the data in a user-friendly format
                for item in data:
                    st.subheader(f"Details for Bar Code: {item.get('Bar_Code', 'N/A')}")
                    st.write(f"**Center Name:** {item.get('Center_Name', 'N/A')}")
                    st.write(f"**Faculty Name:** {item.get('Name', 'N/A')}")
                    st.write(f"**Contact No.:** {item.get('Contact_No', 'N/A')}")
                    st.write(f"**Catch No.:** {item.get('Catch_No', 'N/A')}")
                    st.write(f"**Paper Name:** {item.get('Paper_Name', 'N/A')}")
                    st.write(f"**Evaluation Session:** {item.get('Eval_Session', 'N/A')}")
                    st.write(f"**Checked Type:** {item.get('Checked_Type', 'N/A')}")
                    st.write(f"**Checked:** {'Yes' if item.get('Checked') else 'No'}")
                    st.write(f"**Total Marks:** {item.get('Total_Marks', 'N/A')}")
                    st.write(f"**Obtained Marks:** {item.get('Obt_Marks', 'N/A')}")
                    st.markdown("---") # Separator for multiple results
            else:
                st.warning("No data found for the provided Bar Code.")

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the API: {e}")
        except json.JSONDecodeError:
            st.error("Error decoding JSON response from the API. The response might not be valid JSON.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("Please enter a Bar Code to proceed.")

st.markdown("---")
st.caption("Developed with Streamlit and Python.")
