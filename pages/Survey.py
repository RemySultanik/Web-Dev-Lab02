# This creates the page for users to input data.
# The collected data should be appended to the 'data.csv' file.

import streamlit as st
import pandas as pd
import json
import os # The 'os' module is used for file system operations (e.g. checking if a file exists).


# PAGE CONFIGURATION
st.set_page_config(
    page_title="National Parks Survey",
    page_icon="🏞️",
)

# Reading parks JSON file
infile = open("parks.json", "r")
parks = json.load(infile)
infile.close()


# PAGE TITLE AND USER DIRECTIONS
st.title("National Parks Explorer 🏞️")
st.header("Share Your National Park Experiences")
st.write("Help us explore how people experience America's national parks! Tell us about a park you've visited and how many times you've been there.")


# DATA INPUT FORM
with st.form("survey_form"):

    # Park selection
    category_input = st.selectbox("Which national park have you visited?", list(parks.keys()))

    # Number of visits
    value_input = st.number_input(
        "How many times have you visited this park?",
        min_value=0,
        step=1
    )

    # Submit button
    submitted = st.form_submit_button("Submit Your Response")

    st.caption("You can submit multiple responses for different parks!")

    # Saving submitted data
    if submitted:

        # Creating a new row of data
        new_data = pd.DataFrame({
            "Category": [category_input],
            "Value": [value_input]
        })

        # Adding the new data to the CSV file
        new_data.to_csv("data.csv", mode="a", header=False, index=False)

        st.success("Your data has been submitted!")
        st.write(f"You entered: **Park:** {category_input}, **Number of Visits:** {value_input}")


# DATA DISPLAY
st.divider()
st.header("Current Data in CSV")

if os.path.exists('data.csv') and os.path.getsize('data.csv') > 0:
    current_data_df = pd.read_csv('data.csv')
    current_data_df.index = current_data_df.index + 1
    st.dataframe(current_data_df)
else:
    st.warning("The 'data.csv' file is empty or does not exist yet.")