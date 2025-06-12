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
        # Use RealDictCursor to get results as dictionaries
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
    # --- The Fix Starts Here ---

    # 1. Define a whitelist of allowed column names for security
    allowed_sort_columns = [
        "name", "population", "income", "illiteracy", "life_exp",
        "murder", "hs_grad", "frost", "area"
    ]

    # In your database, the "State" column is likely capitalized. Let's handle that.
    # The API will accept 'name' but query for 'State'
    db_column_map = {
        "name": '"State"', # Use quotes for case-sensitive column names
        "population": '"Population"',
        "income": '"Income"',
        "illiteracy": '"Illiteracy"',
        "life_exp": '"Life Exp"',
        "murder": '"Murder"',
        "hs_grad": '"HS Grad"',
        "frost": '"Frost"',
        "area": '"Area"'
    }


    # 2. Validate the user-provided sort_by parameter
    if sort_by.lower() not in allowed_sort_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort column. Please use one of: {', '.join(allowed_sort_columns)}"
        )

    # Map the friendly name to the actual database column name
    sort_column_db = db_column_map.get(sort_by.lower())

    conn = get_db_connection()
    # Use RealDictCursor to get results as dictionaries directly
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # 3. Create a dynamic and safe SQL query
    # Using f-string here is safe ONLY BECAUSE we validated `sort_column_db` against a whitelist.
    query = f"SELECT * FROM states ORDER BY {sort_column_db} ASC"

    cursor.execute(query)
    states = cursor.fetchall()

    cursor.close()
    conn.close()

    # 4. The result is already a list of dictionaries, so we just return it.
    # We need to rename the keys to be lowercase to match the Streamlit app's expectations
    result = []
    for row in states:
        # Create a new dictionary with lowercase keys
        new_row = {key.lower().replace(" ", "_"): value for key, value in row.items()}
        # Handle specific name changes
        if 'state' in new_row:
            new_row['name'] = new_row.pop('state')
        if 'life_exp' in new_row:
             new_row['life_exp'] = new_row.pop('life_exp')
        if 'hs_grad' in new_row:
             new_row['hs_grad'] = new_row.pop('hs_grad')
        result.append(new_row)

    return result
    # --- The Fix Ends Here ---


@app.get("/")
def read_root():
    return {"message": "Welcome to the US States API"}
