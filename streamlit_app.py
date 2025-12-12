# ------------------------------
# Import packages
# ------------------------------
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# ------------------------------
# Title
# ------------------------------
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# ------------------------------
# Name input
# ------------------------------
name_on_order = st.text_input("Name on smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# ------------------------------
# Snowflake session
# ------------------------------
session = get_active_session()

# ------------------------------
# Load fruit options
# ------------------------------
fruit_options_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_list = [row["FRUIT_NAME"] for row in fruit_options_df.collect()]

# ------------------------------
# Ingredient picker
# ------------------------------
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# ------------------------------
# Submit order
# ------------------------------
if st.button("Submit Order"):
    if not ingredients_list:
        st.warning("Please select at least one ingredient!")
    elif not name_on_order:
        st.warning("Please enter a name for your smoothie!")
    else:
        ingredients_string = ", ".join(ingredients_list)
        session.sql(
            f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order, order_filled)
            VALUES ('{ingredients_string}', '{name_on_order}', FALSE)
            """
        ).collect()
        st.success(f'Your Smoothie is ordered! ✅ {name_on_order}')

# ------------------------------
# Display nutrition info for selected fruits
# ------------------------------
if ingredients_list:
    st.write("### 🍉 Nutrition Information for Your Selected Fruits")
    
    for fruit_chosen in ingredients_list:

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Prepare API-friendly name
        api_fruit_name = fruit_chosen.lower().replace(" ", "").replace("-", "")

        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{api_fruit_name}")
            
            if response.status_code == 200:
                sf_df = pd.DataFrame(response.json())
                st.dataframe(sf_df, use_container_width=True)
            else:
                st.dataframe(
                    pd.DataFrame({
                        "value": [f"Sorry, {fruit_chosen} is not in the SmoothieFroot database."]
                    }),
                    use_container_width=True
                )
        except:
            st.dataframe(
                pd.DataFrame({
                    "value": [f"Sorry, {fruit_chosen} is not in the SmoothieFroot database."]
                }),
                use_container_width=True
            )

# ------------------------------
# Display unfilled orders (optional)
# ------------------------------
orders_df = session.table("smoothies.public.orders").filter(col("order_filled") == False)
st.subheader("Unfilled Orders")
st.dataframe(orders_df.to_pandas())
