import os
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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
def get_all_states():
    """Endpoint to retrieve all states from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT State, Income, Population FROM states ORDER BY State ASC")
    states = cursor.fetchall()
    cursor.close()
    conn.close()

    # Format the result into a list of dictionaries
    result = [
        {"State": row[0], "Income": row[1], "Population": row[2]} for row in states
    ]
    return result

@app.get("/")
def read_root():
    return {"message": "Welcome to the US States API"}
