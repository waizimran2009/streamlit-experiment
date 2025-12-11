import streamlit as st
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

# ------------------------------
# Ingredient picker
# ------------------------------
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options_df,
    max_selections = 5 
)

# Make ingredients comma-separated for readability
ingredients_string = ", ".join(ingredients_list)
st.write("Selected ingredients:", ingredients_string)

# ------------------------------
# Submit order button
# ------------------------------
if st.button("Submit Order"):
    if not ingredients_string:
        st.warning("Please select at least one ingredient!")
    elif not name_on_order:
        st.warning("Please enter a name for your smoothie!")
    else:
        session.sql(
            f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order, order_filled)
            VALUES ('{ingredients_string}', '{name_on_order}', FALSE)
            """
        ).collect()
        st.success(f'Your Smoothie is ordered! ✅ {name_on_order}')

# ------------------------------
# Display unfilled orders
# ------------------------------
orders_df = session.table("smoothies.public.orders").filter(col("order_filled") == False)

st.subheader("Unfilled Orders")
st.dataframe(orders_df.to_pandas())

# ------------------------------
# Mark an order as filled
# ------------------------------

# Use ORDER_UID instead of ORDER_ID
order_ids = [row["ORDER_UID"] for row in orders_df.select(col("ORDER_UID")).collect()]

if order_ids:
    selected_order_id = st.selectbox("Select order to mark as filled", order_ids)

    if st.button("Mark as Filled"):
        session.sql(
            f"""
            UPDATE smoothies.public.orders
            SET order_filled = TRUE
            WHERE order_uid = {selected_order_id}
            """
        ).collect()
        st.success(f"Order {selected_order_id} marked as filled ✅")
else:
    st.info("No unfilled orders to display.")



