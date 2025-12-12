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

# Load fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Ingredient picker
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe
)

# Combine selected ingredients into a string
ingredients_string = "".join(ingredients_list)

# Display the selected ingredients string
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


# -----------------------------
# NUTRITION INFORMATION SECTION
# -----------------------------
st.header("🍉 Nutrition Information for Your Selected Fruits")

for fruit in ingredients_list:

    st.subheader(f"{fruit} Nutrition Information")

    # Clean fruit name for API
    api_fruit_name = fruit.lower().replace(" ", "")

    url = f"https://my.smoothiefroot.com/api/fruit/{api_fruit_name}"
    response = requests.get(url)

    # If fruit found in Smoothiefroot database
    if response.status_code == 200 and "family" in response.json():
        data = response.json()

        df = pd.DataFrame.from_dict(data, orient='index', columns=['value'])
        st.dataframe(df, use_container_width=True)

    else:
        # Fruit NOT found -> show error table (same as screenshot)
        error_df = pd.DataFrame({
            "value": ["Sorry, that fruit is not in our database."]
        })
        st.dataframe(error_df, use_container_width=True)
