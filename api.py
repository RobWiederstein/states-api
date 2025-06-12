import os
import psycopg2
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor

app = FastAPI(title="US States API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
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
    # --- THE FIX ---
    # The database hint told us all column names are lowercase.
    # This map now correctly reflects the actual database schema.
    db_column_map = {
        "name": "state",
        "population": "population",
        "income": "income",
        "illiteracy": "illiteracy",
        "life_exp": "life_exp",
        "murder": "murder",
        "hs_grad": "hs_grad",
        "frost": "frost",
        "area": "area"
    }
    # --- END FIX ---

    api_sort_key = sort_by.lower()
    if api_sort_key not in db_column_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort column. Please use one of: {', '.join(db_column_map.keys())}"
        )

    sort_column_in_db = db_column_map.get(api_sort_key)

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Since column names are simple (no spaces, all lowercase), we no longer need quotes.
    query = f"SELECT * FROM states ORDER BY {sort_column_in_db} ASC"

    try:
        cursor.execute(query)
        db_results = cursor.fetchall()
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    finally:
        cursor.close()
        conn.close()

    # --- THE FIX ---
    # The API response keys need to match what the Streamlit app expects ('name', 'life_exp', etc.).
    # The database returns lowercase keys ('state', 'life_exp', etc.). We just need to rename 'state' to 'name'.
    final_result = []
    for row in db_results:
        # 'row' is a dictionary like {'state': 'Alabama', 'population': 3615, ...}
        # We rename the 'state' key to 'name' for the final output.
        row['name'] = row.pop('state')
        final_result.append(row)
    # --- END FIX ---

    return final_result


@app.get("/")
def read_root():
    return {"message": "Welcome to the US States API"}
