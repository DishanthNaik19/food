import os
os.makedirs("data", exist_ok=True)
import pandas as pd

# File paths
providers_fp = r"C:\Users\Dishanth\OneDrive\Desktop\project\app\data\cleaned_providers.csv"
receivers_fp = r"C:\Users\Dishanth\OneDrive\Desktop\project\app\data\cleaned_receivers.csv"
food_listings_fp = r"C:\Users\Dishanth\OneDrive\Desktop\project\app\data\cleaned_food_listings.csv"
claims_fp = r"C:\Users\Dishanth\OneDrive\Desktop\project\app\data\cleaned_claims.csv"

# Load CSV files
providers = pd.read_csv(providers_fp)
receivers = pd.read_csv(receivers_fp)
food_listings = pd.read_csv(food_listings_fp)
claims = pd.read_csv(claims_fp)

# Quick look at each dataset
print("Providers:\n", providers.head(), "\n")
print("Receivers:\n", receivers.head(), "\n")
print("Food Listings:\n", food_listings.head(), "\n")
print("Claims:\n", claims.head(), "\n")

# --- Data Cleaning ---
# Remove duplicates
providers.drop_duplicates(inplace=True)
receivers.drop_duplicates(inplace=True)
food_listings.drop_duplicates(inplace=True)
claims.drop_duplicates(inplace=True)

# Convert dates
food_listings["Expiry_Date"] = pd.to_datetime(food_listings["Expiry_Date"], errors="coerce")
claims["Timestamp"] = pd.to_datetime(claims["Timestamp"], errors="coerce")

# Standardize city names (trim spaces & title case)
for df in [providers, receivers, food_listings]:
    df["City"] = df["City"].str.strip().str.title()

# Handle missing values (example: fill missing contact with 'Not Provided')
providers["Contact"].fillna("Not Provided", inplace=True)
receivers["Contact"].fillna("Not Provided", inplace=True)

# Save cleaned CSVs
providers.to_csv("data/cleaned_providers.csv", index=False)
receivers.to_csv("data/cleaned_receivers.csv", index=False)
food_listings.to_csv("data/cleaned_food_listings.csv", index=False)
claims.to_csv("data/cleaned_claims.csv", index=False)

print("Cleaning complete. Cleaned files saved in data/ folder.")
import mysql.connector
print("mysql.connector is working")


import pandas as pd

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",      # your MySQL username
    password="qwerty123456@#$"  # your MySQL password
)
cursor = conn.cursor()

# Create database & tables
cursor.execute("CREATE DATABASE IF NOT EXISTS food_wastage")
cursor.execute("USE food_wastage")

# Read cleaned CSVs
providers = pd.read_csv(r"C:\Users\Dishanth\OneDrive\Desktop\project\app\data\cleaned_providers.csv")
receivers = pd.read_csv(r"C:\Users\Dishanth\OneDrive\Desktop\project\app\data\cleaned_receivers.csv")
food_listings = pd.read_csv(r"C:\Users\Dishanth\OneDrive\Desktop\project\app\data\cleaned_food_listings.csv")
claims = pd.read_csv(r"C:\Users\Dishanth\OneDrive\Desktop\project\app\data\cleaned_claims.csv")

# Insert providers
for _, row in providers.iterrows():
    cursor.execute("""
        INSERT INTO providers VALUES (%s,%s,%s,%s,%s,%s)
    """, tuple(row))

# Insert receivers
for _, row in receivers.iterrows():
    cursor.execute("""
        INSERT INTO receivers VALUES (%s,%s,%s,%s,%s)
    """, tuple(row))

# Insert food_listings
for _, row in food_listings.iterrows():
    cursor.execute("""
        INSERT INTO food_listings VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, tuple(row))

# Insert claims
for _, row in claims.iterrows():
    cursor.execute("""
        INSERT INTO claims VALUES (%s,%s,%s,%s,%s)
    """, tuple(row))

# Commit changes
conn.commit()
print(" Data inserted into SQL database successfully.")

# Close connection
cursor.close()
conn.close()


