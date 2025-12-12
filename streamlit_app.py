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
# --- Nutrition Information Section ---

st.header("🍉 Nutrition Information for Your Selected Fruits")

import requests
import pandas as pd

for fruit in ingredients_list:

    st.subheader(f"{fruit} Nutrition Information")

    # Convert fruit to lowercase for API
    api_fruit_name = fruit.lower().replace(" ", "")

    # API call
    url = f"https://my.smoothiefroot.com/api/fruit/{api_fruit_name}"
    response = requests.get(url)

    # If API returns valid nutrition data
    if response.status_code == 200 and "family" in response.json():
        data = response.json()

        # Convert dictionary to table
        df = pd.DataFrame.from_dict(data, orient='index', columns=['value'])
        st.dataframe(df, use_container_width=True)

    else:
        # Show error table (same as screenshot)
        error_df = pd.DataFrame({
            "value": ["Sorry, that fruit is not in our database."]
        })
        st.dataframe(error_df, use_container_width=True)
