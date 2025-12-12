# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on smoothie:")
st.write("The name on your smoothie will be:", name_on_order)


# Get Snowflake session
cnx=st.connection("snowflake")
session = cnx.session()

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Ingredient picker
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe
)

# Combine selected ingredients into a string
ingredients_string = "".join(ingredients_list)  # same logic as yours
st.write("Selected ingredients string:", ingredients_string)

# Button for submitting order
time_to_insert = st.button("Submit Order")

if time_to_insert:
    if not ingredients_string:
        st.warning("Please select at least one ingredient!")
    elif not name_on_order:
        st.warning("Please enter a name for your smoothie!")
    else:
        # Build SQL statement as a single line
        my_insert_stmt = (
            f"INSERT INTO smoothies.public.orders(ingredients, name_on_order) "
            f"VALUES ('{ingredients_string}', '{name_on_order}')"
        )

        # Execute insert
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered!✅{name_on_order}')




