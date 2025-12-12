# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# --- Smoothie Name Input ---
name_on_order = st.text_input("Name on smoothie:", key="smoothie_name_input")
st.write("The name on your smoothie will be:", name_on_order)

# --- Snowflake Connection and Fruit Options ---
# Get Snowflake session
try:
    cnx = st.connection("snowflake")
    session = cnx.session()
    
    # Load fruit options from Snowflake and convert to a list for multiselect
    # Select the FRUIT_NAME column from the fruit_options table
    my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
    
    # Fetch the data into a pandas DataFrame and then extract the list of fruit names
    fruit_options = my_dataframe.to_pandas()['FRUIT_NAME'].tolist()

except Exception as e:
    st.error(f"Could not connect to Snowflake or load fruit options. Error: {e}")
    # Provide a fallback list for development/testing if connection fails
    fruit_options = ["Tangerine", "Kiwi", "Lime", "Mango", "Ximenia", "Banana"]

# --- Ingredient Picker ---
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options, # Use the list of available fruits
    max_selections=5 # Limit selection to 5
)

# Combine selected ingredients into a comma-separated string for database/display
ingredients_string = ", ".join(ingredients_list)

# Optional: display the string (can be removed, but helpful for debugging/matching your initial code)
# st.write("Selected ingredients string:", ingredients_string)


# -----------------------------
# NUTRITION INFORMATION SECTION
# This section runs automatically based on the ingredients_list
# -----------------------------
if ingredients_list:
    st.header("🍉 Nutrition Information for Your Selected Fruits")

    # Loop through the list of selected ingredients
    for fruit in ingredients_list:
        
        # Display the subheader for the current fruit
        st.subheader(f"{fruit} Nutrition Information")

        # Clean the fruit name for the API endpoint: lowercase and remove spaces
        api_fruit_name = fruit.lower().replace(" ", "")

        # Construct the API URL
        url = f"https://my.smoothiefroot.com/api/fruit/{api_fruit_name}"
        
        try:
            # Make the external request
            response = requests.get(url)

            # Check for a successful response and valid JSON data
            if response.status_code == 200:
                data = response.json()
                
                # Check if the response is a dictionary (valid nutrition data)
                if isinstance(data, dict):
                    # Convert the dictionary to a DataFrame for display
                    df = pd.DataFrame.from_dict(data, orient='index', columns=['value'])
                    # For a nicer table, reset the index and rename the columns
                    df = df.reset_index().rename(columns={'index': 'Attribute', 'value': 'Value'})
                    
                    st.dataframe(df, use_container_width=True)
                else:
                    # Handle cases where the API returns a success status but empty/non-dict data
                    st.dataframe(
                        pd.DataFrame({"value": ["Sorry, that fruit is not in our database."]}, index=["error"]), 
                        use_container_width=True
                    )

            else:
                # Handle non-200 status codes (e.g., 404 Not Found)
                # Replicate the error table style shown in the screenshot
                st.dataframe(
                    pd.DataFrame({"value": ["Sorry, that fruit is not in our database."]}, index=["error"]), 
                    use_container_width=True
                )
                
        except requests.exceptions.RequestException as req_err:
            # Handle connection errors (e.g., network issues, DNS failure)
            st.error(f"Error fetching data for {fruit}: {req_err}")

# -----------------------------
# SUBMIT ORDER BUTTON SECTION (Placed after nutrition tables as per screenshot)
# -----------------------------
time_to_insert = st.button("Submit Order")

if time_to_insert:
    # Basic validation checks
    if not ingredients_string:
        st.warning("Please select at least one ingredient!")
    elif not name_on_order:
        st.warning("Please enter a name for your smoothie!")
    else:
        # Prepare and execute the SQL INSERT statement
        try:
            my_insert_stmt = (
                f"INSERT INTO smoothies.public.orders(ingredients, name_on_order) "
                f"VALUES ('{ingredients_string}', '{name_on_order}')"
            )

            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered! ✅ {name_on_order}')
        
        except Exception as db_err:
            st.error(f"Failed to submit order to Snowflake. Error: {db_err}")
