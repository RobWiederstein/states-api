import os
import psycopg2
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Imports for Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables from .env
load_dotenv()

# --- THIS IS THE CORRECT ORDER ---
# 1. Create the Limiter instance first.
limiter = Limiter(key_func=get_remote_address)

# 2. Create the FastAPI app instance.
app = FastAPI(title="US States API", root_path="/states")

# 3. Now, apply the limiter and exception handler to the app.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# --- END OF CORRECTION ---


# Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pull the database connection string from environment
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")

@app.get("/states")
@limiter.limit("100/minute") # Apply the rate limit decorator
def get_states_by_name(request: Request, name_contains: str = Query(None, description="Filter by partial state name")):
    """
    Returns states where the name contains the given substring (case-insensitive).
    If no filter is provided, all states are returned.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        if name_contains:
            query = """
                SELECT * FROM states
                WHERE LOWER(state_name) LIKE %s
                ORDER BY state_name ASC
            """
            value = f"%{name_contains.lower()}%"
            cursor.execute(query, (value,))
        else:
            query = "SELECT * FROM states ORDER BY state_name ASC"
            cursor.execute(query)

        results = cursor.fetchall()
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    finally:
        cursor.close()
        conn.close()

    return results

@app.get("/")
@limiter.limit("100/minute") # Also protect the root path
def read_root(request: Request):
    return {"message": "Welcome to the US States API"}
