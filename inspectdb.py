import os
import psycopg2

# --- IMPORTANT ---
# This script must be run from a terminal where the DATABASE_URL
# environment variable is set, just like when you run your API locally.
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: The DATABASE_URL environment variable is not set.")
    print("You may need to source it from your Render dashboard or a .env file.")
else:
    conn = None  # Initialize conn to None
    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # This query asks the database for the names of all columns in the 'states' table.
        query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'states'
        ORDER BY ordinal_position;
        """

        cursor.execute(query)
        columns = cursor.fetchall() # This will be a list of tuples, e.g., [('state',), ('population',)]

        print("\n" + "="*40)
        print("Found the following column names in 'states':")
        print("="*40)
        for col_tuple in columns:
            print(col_tuple[0]) # Print the actual column name string
        print("="*40)
        print("\nUse this exact list to update the API's app.py file.")


    except psycopg2.Error as e:
        print(f"\nAn error occurred while connecting or querying the database: {e}")

    finally:
        # Ensure the connection is always closed
        if conn:
            conn.close()
            print("\nConnection closed.")
