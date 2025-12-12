# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Connect to Snowflake
session = get_active_session()  # Make sure only ONE session is active

# Load fruit list from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert the Snowpark DataFrame to a Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Ingredient selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Show search values and nutrition info
if ingredients_list:
    st.header("🍉 Nutrition Information for Your Selected Fruits")
    
    for fruit_chosen in ingredients_list:
        # Get the SEARCH_ON value from Pandas DataFrame
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')

        # Call Fruityvice API
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on.lower()}")

        # ---------------------------------------------------------
        #  LOCAL NUTRITION FALLBACK DATABASE
        # ---------------------------------------------------------
        local_nutrition_data = {
            "quince": {"family": "Rosaceae", "genus": "Cydonia", "name": "Quince", "order": "Rosales",
                       "carbohydrates": "15.3", "protein": "0.4", "fat": "0.1", "calories": "57"},
            "raspberries": {"family": "Rosaceae", "genus": "Rubus", "name": "Raspberries", "order": "Rosales",
                            "carbohydrates": "11.9", "protein": "1.5", "fat": "0.7", "calories": "52"},
            "strawberries": {"family": "Rosaceae", "genus": "Fragaria", "name": "Strawberries", "order": "Rosales",
                             "carbohydrates": "7.7", "protein": "0.7", "fat": "0.3", "calories": "32"},
            "tangerine": {"family": "Rutaceae", "genus": "Citrus", "name": "Tangerine", "order": "Sapindales",
                          "carbohydrates": "13.3", "protein": "0.8", "fat": "0.3", "calories": "53"},
            "uglifruit": {"family": "Rutaceae", "genus": "Citrus", "name": "Ugli Fruit", "order": "Sapindales",
                          "carbohydrates": "9.0", "protein": "0.8", "fat": "0.2", "calories": "45"},
            "vanillafruit": {"family": "Orchidaceae", "genus": "Vanilla", "name": "Vanilla Fruit", "order": "Asparagales",
                             "carbohydrates": "12.7", "protein": "0.1", "fat": "0.1", "calories": "288"},
            "watermelon": {"family": "Cucurbitaceae", "genus": "Citrullus", "name": "Watermelon", "order": "Cucurbitales",
                           "carbohydrates": "7.6", "protein": "0.6", "fat": "0.2", "calories": "30"},
            "ximenia": {"family": "Olacaceae", "genus": "Ximenia", "name": "Ximenia", "order": "Santalales",
                        "carbohydrates": "14.0", "protein": "1.0", "fat": "1.5", "calories": "65"},
            "yerbamate": {"family": "Aquifoliaceae", "genus": "Ilex", "name": "Yerba Mate", "order": "Aquifoliales",
                          "carbohydrates": "8.0", "protein": "0.4", "fat": "0.2", "calories": "30"},
            "ziziphusjujube": {"family": "Rhamnaceae", "genus": "Ziziphus", "name": "Ziziphus Jujube", "order": "Rosales",
                               "carbohydrates": "20.2", "protein": "1.2", "fat": "0.2", "calories": "79"}
        }

        # Process nutrition data
        fruit_data = None

        # If API works
        if fruityvice_response.status_code == 200 and "genus" in fruityvice_response.json():
            fruit_data = fruityvice_response.json()
        # If API fails → use local data
        elif search_on.lower().replace(" ", "") in local_nutrition_data:
            fruit_data = local_nutrition_data[search_on.lower().replace(" ", "")]
        
        # Display nutrition table
        if fruit_data:
            df = pd.DataFrame.from_dict(fruit_data, orient='index', columns=['value'])
            st.dataframe(df, use_container_width=True)
        else:
            df = pd.DataFrame({"value": ["Sorry, that fruit is not in our database."]})
            st.dataframe(df, use_container_width=True)
