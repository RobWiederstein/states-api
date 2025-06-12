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
    # --- FINAL FIX ---
    # This map is now 100% correct, based on the output from inspectdb.py.
    # It maps the user-friendly API parameters to the exact, lowercase database column names.
    db_column_map = {
        "name": "state",
        "population": "population",
        "income": "income",
        "illiteracy": "illiteracy",
        "life_exp": "lifeexp",  # Corrected: no underscore
        "murder": "murder",
        "hs_grad": "hsgrad",   # Corrected: no underscore
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

    query = f"SELECT * FROM states ORDER BY {sort_column_in_db} ASC"

    try:
        cursor.execute(query)
        db_results = cursor.fetchall()
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    finally:
        cursor.close()
        conn.close()

    # --- FINAL FIX ---
    # This loop now correctly transforms the database output (with keys like 'state', 'lifeexp')
    # into the JSON response the Streamlit app expects (with keys like 'name', 'life_exp').
    final_result = []
    for row in db_results:
        # 'row' is a dictionary like {'state': 'Alabama', 'lifeexp': 69.05, ...}
        formatted_row = {
            "name": row.get("state"),
            "population": row.get("population"),
            "income": row.get("income"),
            "illiteracy": row.get("illiteracy"),
            "life_exp": row.get("lifeexp"), # Map from 'lifeexp'
            "murder": row.get("murder"),
            "hs_grad": row.get("hsgrad"),   # Map from 'hsgrad'
            "frost": row.get("frost"),
            "area": row.get("area"),
        }
        final_result.append(formatted_row)
    # --- END FIX ---

    return final_result

@app.get("/")
def read_root():
    return {"message": "Welcome to the US States API"}


