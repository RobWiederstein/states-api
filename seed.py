import os
import requests
import pandas as pd
from sqlalchemy import create_engine

print("Starting data refresh script...")

# Get the database URL from the environment variable provided by Docker
# This is the same variable our .env file sets
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# This is the URL your migration script was likely fetching from
DATA_SOURCE_URL = "https://raw.githubusercontent.com/RobWiederstein/states-api/main/data/states.json"

try:
    # --- 1. Fetch Fresh Data ---
    print(f"Fetching fresh data from {DATA_SOURCE_URL}...")
    response = requests.get(DATA_SOURCE_URL)
    response.raise_for_status()  # Raise an exception for bad status codes
    data = response.json()
    print("Data fetched successfully.")

    # Convert the list of dictionaries to a Pandas DataFrame
    df = pd.DataFrame(data)
    # Optional: You can rename columns here if needed
    # df.rename(columns={'old_name': 'new_name'}, inplace=True)

    # --- 2. Connect to the Database ---
    print("Connecting to the database...")
    engine = create_engine(DATABASE_URL)

    # --- 3. Replace the Data in the Table ---
    # The 'to_sql' method with if_exists='replace' is a powerful way to do this.
    # It will DROP the old table, CREATE a new one with the same name,
    # and INSERT all the data from the DataFrame.
    # The 'index=False' prevents Pandas from writing the DataFrame index as a column.
    table_name = "states" # Make sure this matches your table name
    print(f"Replacing data in the '{table_name}' table...")
    df.to_sql(table_name, engine, if_exists='replace', index=False)

    print(f"Successfully inserted {len(df)} records. Data refresh complete.")

except Exception as e:
    print(f"An error occurred: {e}")
    # Exit with a non-zero status code to indicate failure
    exit(1)
