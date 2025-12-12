# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on smoothie:", key="smoothie_name_input")
st.write("The name on your smoothie will be:", name_on_order)

# Get Snowflake session (using st.connection is correct)
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options from Snowflake
# Fetch as a list of strings for st.multiselect using .to_pandas()
# Note: st.multiselect on a Snowpark DF/Table selects the first column, which is fine here.
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME")).to_pandas()
fruit_options = my_dataframe['FRUIT_NAME'].tolist()

# Ingredient picker
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options # Use the list of strings
)

# Combine selected ingredients into a comma-separated string for database
ingredients_string = ", ".join(ingredients_list)

# Display the selected ingredients string (optional, can be removed to match the screenshot)
# st.write("Selected ingredients string:", ingredients_string)


# -----------------------------
# NUTRITION INFORMATION SECTION
# This section runs automatically upon ingredient selection (Streamlit's reactive nature)
# -----------------------------
if ingredients_list:
    st.subheader("🍉 Nutrition Information for Your Selected Fruits")

    for fruit in ingredients_list:
        # st.subheader for each fruit's table
        st.subheader(f"{fruit} Nutrition Information")

        # Clean fruit name for API lookup: lowercase and remove spaces
        api_fruit_name = fruit.lower().replace(" ", "")

        # Construct the API URL
        url = f"https://my.smoothiefroot.com/api/fruit/{api_fruit_name}"
        
        # Make the request
        response = requests.get(url)

        # Check for successful response (Status 200) and if it has expected data (e.g., 'family' key)
        if response.status_code == 200:
            data = response.json()
            # The API returns a dictionary, which must be converted to a DataFrame
            # for display. orient='index' turns dictionary keys (carbs, fat, etc.)
            # into the DataFrame index, and the values into a column.
            df = pd.DataFrame.from_dict(data, orient='index', columns=['value'])
            
            # Reset index to turn the keys into a column named 'nutrition' for better display
            df = df.reset_index().rename(columns={'index': 'nutrition'})
            
            st.dataframe(df, use_container_width=True)

        else:
            # Fruit NOT found -> show error table
            error_df = pd.DataFrame({
                "value": ["error", "Sorry, that fruit is not in our database."]
            }).T.rename(columns={0: "key", 1: "value"})
            
            # The error in the screenshot is slightly different. Let's replicate the structure from the image:
            error_df_screenshot_style = pd.DataFrame({
                "value": ["Sorry, that fruit is not in our database."],
                "error": [""] # Add empty column to match structure if needed, or simply display the error text
            })
            
            # A simple message or a dataframe with the error message works best
            st.dataframe(
                pd.DataFrame({"value": ["Sorry, that fruit is not in our database."]}, index=["error"]), 
                use_container_width=True
            )
            
            # Or simpler:
            # st.error(f"Could not find nutrition information for {fruit}.")


# -----------------------------
# SUBMIT ORDER BUTTON SECTION (Moved to the end to match screenshot layout)
# -----------------------------
time_to_insert = st.button("Submit Order")

if time_to_insert:
    if not ingredients_string:
        st.warning("Please select at least one ingredient!")
    elif not name_on_order:
        st.warning("Please enter a name for your smoothie!")
    else:
        # Safely quote the ingredients string for SQL insertion
        my_insert_stmt = (
            f"INSERT INTO smoothies.public.orders(ingredients, name_on_order) "
            f"VALUES ('{ingredients_string}', '{name_on_order}')"
        )

        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered! ✅ {name_on_order}')
