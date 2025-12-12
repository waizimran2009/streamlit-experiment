# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Connect to Snowflake (ONE active session only)
session = get_active_session()

# Load fruit list from Snowflake
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(
    col("FRUIT_NAME"), col("SEARCH_ON")
)

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

        # Call Fruityvice API safely
        try:
            fruityvice_response = requests.get(
                f"https://fruityvice.com/api/fruit/{search_on.lower().replace(' ', '')}"
            )
            fruityvice_json = fruityvice_response.json() if fruityvice_response.status_code == 200 else None

            # Sometimes Fruityvice returns a list instead of a dictionary
            if isinstance(fruityvice_json, list) and len(fruityvice_json) > 0:
                fruityvice_json = fruityvice_json[0]

        except:
            fruityvice_json = None

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

        # Normalize key for fallback lookup
        lookup_key = search_on.lower().replace(" ", "")

        # Final fruit data: API → fallback → error
        if fruityvice_json and "genus" in fruityvice_json:
            fruit_data = fruityvice_json
        elif lookup_key in local_nutrition_data:
            fruit_data = local_nutrition_data[lookup_key]
        else:
            fruit_data = None

        # Display nutrition table
        if fruit_data:
            df = pd.DataFrame.from_dict(fruit_data, orient='index', columns=['value'])
            st.dataframe(df, use_container_width=True)
        else:
            df = pd.DataFrame({"value": ["Sorry, that fruit is not in our nutrition database."]})
            st.dataframe(df, use_container_width=True)
