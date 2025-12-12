# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Get Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Ingredient picker
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list
)

# Combine selected ingredients
ingredients_string = "".join(ingredients_list)
st.write("Selected ingredients string:", ingredients_string)

# Button for submitting order
time_to_insert = st.button("Submit Order")

if time_to_insert:
    if not ingredients_string:
        st.warning("Please select at least one ingredient!")
    elif not name_on_order:
        st.warning("Please enter a name for your smoothie!")
    else:
        my_insert_stmt = (
            f"INSERT INTO smoothies.public.orders(ingredients, name_on_order) "
            f"VALUES ('{ingredients_string}', '{name_on_order}')"
        )

        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered! ✅ {name_on_order}')

# -------------------------------------------------------------
# 🎯 NEW SECTION: Nutrition info from SmoothieFroot API
# -------------------------------------------------------------
# -------------------------------------------------------------
# 🎯 NEW SECTION: Nutrition info from SmoothieFroot API (FIXED)
# -------------------------------------------------------------
st.header("🍉 Nutrition Information for Your Selected Fruits")

# Mapping: Your fruit names → API fruit names
fruit_api_names = {
    "Apples": "apple",
    "Apple": "apple",
    "Blueberries": "blueberry",
    "Blueberry": "blueberry",
    "Strawberries": "strawberry",
    "Strawberry": "strawberry",
    "Cantaloupe": "cantaloupe",
    "Banana": "banana",
    "Bananas": "banana",
    "Mango": "mango",
    "Mangos": "mango",
    "Pineapple": "pineapple",
    "Dragon Fruit": "dragonfruit",
    "Grapes": "grape",
    "Grape": "grape",
}

def get_fruit_data(fruit_name):
    """
    Fetch nutrition data using corrected API-friendly fruit names
    """
    api_name = fruit_api_names.get(fruit_name, fruit_name.lower())

    try:
        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{api_name}"
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error retrieving info for {fruit_name}: {e}")
        return None


# Show nutrition info for each selected fruit
if ingredients_list:
    for fruit in ingredients_list:
        st.subheader(f"🍎 Nutrition for {fruit}")

        fruit_data = get_fruit_data(fruit)

        if fruit_data:
            df = pd.DataFrame([fruit_data])
            st.dataframe(df, use_container_width=True)
        else:
            st.warning(f"No nutrition data found for {fruit}.")
else:
    st.info("Select fruits above to see their nutrition info.")
