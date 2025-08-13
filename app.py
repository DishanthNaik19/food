import streamlit as st
import pandas as pd
import plotly.express as px
from db_config import get_connection

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title=" Local Food Wastage Management System", layout="wide")

# ---------------------------
# DATABASE HELPERS
# ---------------------------
@st.cache_data
def load_data():
    conn = get_connection()
    providers = pd.read_sql("SELECT * FROM providers", conn)
    receivers = pd.read_sql("SELECT * FROM receivers", conn)
    food_listings = pd.read_sql("SELECT * FROM food_listings", conn)
    claims = pd.read_sql("SELECT * FROM claims", conn)
    conn.close()
    return providers, receivers, food_listings, claims

def run_query(query, params=None):
    conn = get_connection()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

def execute_sql(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    conn.commit()
    conn.close()

providers, receivers, food_listings, claims = load_data()

# ---------------------------
# NAVIGATION TABS
# ---------------------------
tab1, tab2, tab3, tab4 = st.tabs([" Home", " Data View", " Analysis", "CRUD Operations"])

# ---------------------------
# HOME TAB
# ---------------------------
with tab1:
    st.title(" Local Food Wastage Management System")
    st.markdown("""
    **Purpose**: Reduce food wastage by connecting providers with those in need.

    **Features**:
    - View and filter food listings
    - Analyze trends with charts
    - Add/Edit/Delete food records
    - Access provider & receiver contact details
    """)

# ---------------------------
# DATA VIEW TAB
# ---------------------------
with tab2:
    st.sidebar.header("Filters")
    cities = st.sidebar.multiselect("City", food_listings["City"].unique())
    provider_types = st.sidebar.multiselect("Provider Type", food_listings["Provider_Type"].unique())
    food_types = st.sidebar.multiselect("Food Type", food_listings["Food_Type"].unique())
    meal_types = st.sidebar.multiselect("Meal Type", food_listings["Meal_Type"].unique())

    filtered_food = food_listings.copy()
    if cities:
        filtered_food = filtered_food[filtered_food["City"].isin(cities)]
    if provider_types:
        filtered_food = filtered_food[filtered_food["Provider_Type"].isin(provider_types)]
    if food_types:
        filtered_food = filtered_food[filtered_food["Food_Type"].isin(food_types)]
    if meal_types:
        filtered_food = filtered_food[filtered_food["Meal_Type"].isin(meal_types)]

    st.subheader("Filtered Food Listings")
    st.dataframe(filtered_food)

    st.subheader("Provider Contacts")
    st.dataframe(providers[["Name", "Type", "City", "Contact"]])

    st.subheader("Receiver Contacts")
    st.dataframe(receivers[["Name", "Type", "City", "Contact"]])

# ---------------------------
# ANALYSIS TAB - 15 QUERIES
# ---------------------------
with tab3:
    st.title("📊 Analysis Dashboard - 15 SQL Queries")

    queries = {
        "1️⃣ Providers per City":
            "SELECT City, COUNT(*) AS Provider_Count FROM providers GROUP BY City;",

        "2️⃣ Receivers per City":
            "SELECT City, COUNT(*) AS Receiver_Count FROM receivers GROUP BY City;",

        "3️⃣ Most Contributing Provider Type":
            "SELECT Type, COUNT(*) AS Total_Providers FROM providers GROUP BY Type ORDER BY Total_Providers DESC LIMIT 1;",

        "4️⃣ Provider Contact Info (Bengaluru)":
            "SELECT Name, Contact FROM providers WHERE City = 'Bengaluru';",

        "5️⃣ Receivers with Most Claims":
            """SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims
               FROM claims c
               JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
               GROUP BY r.Name
               ORDER BY Total_Claims DESC;""",

        "6️⃣ Total Food Quantity Available":
            "SELECT SUM(Quantity) AS Total_Quantity_Available FROM food_listings;",

        "7️⃣ City with Highest Food Listings":
            """SELECT City, COUNT(*) AS Total_Listings
               FROM food_listings
               GROUP BY City
               ORDER BY Total_Listings DESC
               LIMIT 1;""",

        "8️⃣ Most Common Food Types":
            """SELECT Food_Type, COUNT(*) AS Total_Availability
               FROM food_listings
               GROUP BY Food_Type
               ORDER BY Total_Availability DESC;""",

        "9️⃣ Claims Count per Food Item":
            """SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claims_Count
               FROM claims c
               JOIN food_listings f ON c.Food_ID = f.Food_ID
               GROUP BY f.Food_Name
               ORDER BY Claims_Count DESC;""",

        " Provider with Most Completed Claims":
            """SELECT p.Name, COUNT(c.Claim_ID) AS Successful_Claims
               FROM claims c
               JOIN food_listings f ON c.Food_ID = f.Food_ID
               JOIN providers p ON f.Provider_ID = p.Provider_ID
               WHERE c.Status = 'Completed'
               GROUP BY p.Name
               ORDER BY Successful_Claims DESC
               LIMIT 1;""",

        "1️⃣1️⃣ Total Quantity Donated per Provider":
            """SELECT p.Name, SUM(f.Quantity) AS Total_Donated
               FROM food_listings f
               JOIN providers p ON f.Provider_ID = p.Provider_ID
               GROUP BY p.Name
               ORDER BY Total_Donated DESC;""",

        "1️⃣2️⃣ Claims per Food Type":
            """SELECT f.Food_Type, COUNT(c.Claim_ID) AS Total_Claims
               FROM claims c
               JOIN food_listings f ON c.Food_ID = f.Food_ID
               GROUP BY f.Food_Type
               ORDER BY Total_Claims DESC;""",

        "1️⃣3️⃣ Claim Status Percentage":
            """SELECT Status, 
                      COUNT(*) AS Count_Status,
                      ROUND((COUNT(*) / (SELECT COUNT(*) FROM claims)) * 100, 2) AS Percentage
               FROM claims
               GROUP BY Status;""",

        "1️⃣4️⃣ Average Quantity Claimed per Receiver":
            """SELECT r.Name, ROUND(AVG(f.Quantity), 2) AS Avg_Quantity_Claimed
               FROM claims c
               JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
               JOIN food_listings f ON c.Food_ID = f.Food_ID
               GROUP BY r.Name;""",

        "1️⃣5️⃣ Most Claimed Meal Type":
            """SELECT Meal_Type, COUNT(*) AS Claim_Count
               FROM claims c
               JOIN food_listings f ON c.Food_ID = f.Food_ID
               GROUP BY Meal_Type
               ORDER BY Claim_Count DESC;"""
    }

    selected_query = st.selectbox("Select a Query", list(queries.keys()))
    sql_to_run = queries[selected_query]
    df = run_query(sql_to_run)

    st.subheader(f"Result for: {selected_query}")
    st.dataframe(df)

    if len(df.columns) >= 2 and pd.api.types.is_numeric_dtype(df[df.columns[1]]):
        if "Percentage" in df.columns[1] or "Percent" in df.columns[1]:
            fig = px.pie(df, names=df.columns[0], values=df.columns[1], title=selected_query)
        else:
            fig = px.bar(df, x=df.columns[0], y=df.columns[1], title=selected_query)
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# CRUD TAB
# ---------------------------
with tab4:
    st.title("✏️ Manage Food Listings")
    crud_choice = st.radio("Action", ["Add", "Edit", "Delete"])

    if crud_choice == "Add":
        with st.form("add_food"):
            food_name = st.text_input("Food Name")
            quantity = st.number_input("Quantity", min_value=1)
            expiry_date = st.date_input("Expiry Date")
            provider_id = st.selectbox("Provider", providers["Provider_ID"])
            provider_type = st.text_input("Provider Type")
            city = st.text_input("City")
            food_type = st.text_input("Food Type")
            meal_type = st.text_input("Meal Type")
            submitted = st.form_submit_button("Add Food")
            if submitted:
                execute_sql(
                    """INSERT INTO food_listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, City, Food_Type, Meal_Type)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (food_name, quantity, expiry_date, provider_id, provider_type, city, food_type, meal_type)
                )
                st.success("Food item added!")

    elif crud_choice == "Edit":
        food_id = st.selectbox("Select Food ID", food_listings["Food_ID"])
        row = food_listings[food_listings["Food_ID"] == food_id].iloc[0]
        with st.form("edit_food"):
            food_name = st.text_input("Food Name", row["Food_Name"])
            quantity = st.number_input("Quantity", value=row["Quantity"])
            expiry_date = st.date_input("Expiry Date", row["Expiry_Date"])
            provider_type = st.text_input("Provider Type", row["Provider_Type"])
            city = st.text_input("City", row["City"])
            food_type = st.text_input("Food Type", row["Food_Type"])
            meal_type = st.text_input("Meal Type", row["Meal_Type"])
            submitted = st.form_submit_button("Update Food")
            if submitted:
                execute_sql(
                    """UPDATE food_listings SET Food_Name=%s, Quantity=%s, Expiry_Date=%s, Provider_Type=%s, City=%s, Food_Type=%s, Meal_Type=%s WHERE Food_ID=%s""",
                    (food_name, quantity, expiry_date, provider_type, city, food_type, meal_type, food_id)
                )
                st.success("Food item updated!")

    elif crud_choice == "Delete":
        food_id = st.selectbox("Select Food ID to Delete", food_listings["Food_ID"])
        if st.button("Delete Food"):
            execute_sql("DELETE FROM food_listings WHERE Food_ID=%s", (food_id,))
            st.success("Food item deleted!")
