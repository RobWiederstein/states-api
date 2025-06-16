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
    # CORRECTED: This map now perfectly matches your database schema.
    db_column_map = {
        "name": "state_name",
        "population": "population",
        "income": "income",
        "illiteracy": "illiteracy",
        "life_exp": "life_exp",
        "murder": "murder",
        "hs_grad": "hs_grad",
        "frost": "frost",
        "area": "area"
    }

    api_sort_key = sort_by.lower()
    if api_sort_key not in db_column_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort column. Please use one of: {', '.join(db_column_map.keys())}"
        )

    sort_column_in_db = db_column_map.get(api_sort_key)

    # Use double quotes for column names in SQL to handle case-sensitivity and special characters.
    query = f'SELECT * FROM states ORDER BY "{sort_column_in_db}" ASC'

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(query)
        db_results = cursor.fetchall()
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    finally:
        cursor.close()
        conn.close()

    # This loop is no longer needed because the DB columns and API keys now match.
    # The 'db_results' can be returned directly. This simplifies the code.
    return db_results

@app.get("/")
def read_root():
    return {"message": "Welcome to the US States API"}
