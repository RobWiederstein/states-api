import os
import psycopg2
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor

app = FastAPI(title="US States API")

# This allows your front-end app to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the database connection URL from Render's environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")

@app.get("/states")
def get_all_states(sort_by: str = Query("name", description="Column to sort by.")):
    """
    Endpoint to retrieve all states from the database,
    sorted by a specified column.
    """
    # Define a mapping from the lowercase API parameter to the exact database column name.
    # This acts as a whitelist for security and a mapping for correctness.
    db_column_map = {
        "name": "State",
        "population": "Population",
        "income": "Income",
        "illiteracy": "Illiteracy",
        "life_exp": "Life Exp",
        "murder": "Murder",
        "hs_grad": "HS Grad",
        "frost": "Frost",
        "area": "Area"
    }

    # Validate the user-provided sort_by parameter against our whitelist
    api_sort_key = sort_by.lower()
    if api_sort_key not in db_column_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort column. Please use one of: {', '.join(db_column_map.keys())}"
        )

    # Get the actual column name for the database query
    sort_column_in_db = db_column_map.get(api_sort_key)
    # Quote the column name to handle spaces and case-sensitivity safely in SQL
    safe_sort_column = f'"{sort_column_in_db}"'

    conn = get_db_connection()
    # Use RealDictCursor to get results as dictionaries instead of tuples.
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Construct the final, safe query
    query = f"SELECT * FROM states ORDER BY {safe_sort_column} ASC"

    try:
        cursor.execute(query)
        # fetchall() will return a list of dictionaries, e.g., [{'State': 'Alabama', 'Life Exp': 70.6, ...}]
        db_results = cursor.fetchall()
    except psycopg2.Error as e:
        # NEW: If the query fails, we now catch the error and report it clearly.
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    finally:
        # Always close the connection
        cursor.close()
        conn.close()

    # Manually format the response to have the lowercase keys the Streamlit app expects.
    # This is much safer and clearer than the previous complex logic.
    final_result = []
    for row in db_results:
        # The keys from RealDictCursor are the exact column names: 'State', 'Population', 'Life Exp', etc.
        # The .get() method is used for safety; it returns None if a key is missing.
        formatted_row = {
            "name": row.get("State"),
            "population": row.get("Population"),
            "income": row.get("Income"),
            "illiteracy": row.get("Illiteracy"),
            "life_exp": row.get("Life Exp"),
            "murder": row.get("Murder"),
            "hs_grad": row.get("HS Grad"),
            "frost": row.get("Frost"),
            "area": row.get("Area"),
        }
        final_result.append(formatted_row)

    return final_result


@app.get("/")
def read_root():
    return {"message": "Welcome to the US States API"}
